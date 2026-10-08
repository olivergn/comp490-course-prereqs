import re

def check_course_code(course_code):
    pattern = r"^[A-Z]{4} \d{3}$"
    return re.match(pattern, course_code)

##
# Topological stratification
##

def stratify_db(driver):
    query = """
    MATCH (p:Paper) WHERE NOT ()-[]->(p)
    SET p.stratum = 1
    """
    driver.execute_query(query)

    iterative_query = """
    MATCH (p:Paper)
    WHERE p.stratum IS NULL
    MATCH path = (prereq:Paper)-[:PREREQ*1..]->(p)
    WHERE ALL(c IN nodes(path)[1..-1] WHERE c:Connector)
    WITH p, collect(prereq) AS prereqs
    WHERE ALL(pr IN prereqs WHERE pr.stratum IS NOT NULL and pr.stratum < $stratId)
    SET p.stratum = $stratId
    """
    stratum_id = 2

    for i in range(10):
        driver.execute_query(iterative_query, stratId=stratum_id)
        stratum_id += 1

def get_all_papers(driver):
    query = """
    MATCH (p:Paper)
    RETURN p.name AS name
    """
    records, _, _ = driver.execute_query(query)
    paper_names = [record["name"] for record in records if check_course_code(record["name"])]
    return paper_names

def get_nodes_in_stratum(driver, strat_id):
    query = """
    MATCH (p:Paper)
    WHERE p.stratum = $stratId
    RETURN p.name AS name
    """
    records, _, _ = driver.execute_query(query, stratId=strat_id)
    paper_names = [record["name"] for record in records if check_course_code(record["name"])]
    return paper_names

def get_ultimate_nodes(driver):
    query = """
    MATCH (p:Paper)
    WHERE NOT (p)-[:PREREQ]->()
    RETURN p.name AS name
    """

    records, _, _ = driver.execute_query(query)
    paper_names = [record["name"] for record in records if check_course_code(record["name"])]
    return paper_names

def get_stratum_flux(driver, strat_id):
    stratum = get_nodes_in_stratum(driver, strat_id)
    strat_size = len(stratum)
    in_paths = 0
    out_paths = 0

    in_query = """
    MATCH path = (start:Paper)-[rels:PREREQ*0..]->(end:Paper {name: $targetName})
    WHERE start.stratum = ($stratId - 1)
    AND ALL (n IN nodes(path)[1..-1] WHERE n:Connector)
    RETURN sum(REDUCE(prod = 1.0, r IN rels | prod * coalesce(r.weight, 1.0))) AS totalPaths
    """
    out_query = """
    MATCH path = (start:Paper {name: $targetName})-[rels:PREREQ*0..]->(end:Paper)
    WHERE end.stratum = ($stratId + 1)
    AND ALL (n IN nodes(path)[1..-1] WHERE n:Connector)
    RETURN sum(REDUCE(prod = 1.0, r IN rels | prod * coalesce(r.weight, 1.0))) AS totalPaths
    """

    for name in stratum:
        records, _, _ = driver.execute_query(in_query, targetName=name, stratId=strat_id)
        in_paths += records[0]["totalPaths"]
        records, _, _ = driver.execute_query(out_query, targetName=name, stratId=strat_id)
        out_paths += records[0]["totalPaths"]

    if strat_size > 0:
        return (out_paths - in_paths) / strat_size
    return None

##
# Curriculum-level metric functions
##

def get_curriculum_breadth(driver):
    total_breadth = 0
    count = 0
    i = 1
    while True:
        stratum = get_nodes_in_stratum(driver, i)
        if not stratum:
            break
        total_breadth += len(stratum)
        count += 1
        i += 1
    
    if count > 0:
        return total_breadth / count
    else:
        return None

def get_curriculum_depth(driver):
    ultimate_paper_names = get_ultimate_nodes(driver)
    total_depth = 0
    count = 0

    query = """
    MATCH path = ()-[:PREREQ*0..]->(target:Paper {name: $targetName})
    WITH path, [n IN nodes(path) WHERE n:Paper] AS paperNodes
    ORDER BY size(paperNodes) DESC
    RETURN path, size(paperNodes) AS paperCount
    LIMIT 1
    """

    for name in ultimate_paper_names:
        records, _, _ = driver.execute_query(query, targetName=name)

        if records:
            total_depth += records[0]["paperCount"]
        else:
            total_depth += 1
        count += 1

    if count > 0:
        return total_depth / count
    else:
        return None

def get_curriculum_flux(driver):
    total_flux = 0
    count = 0
    i = 1
    while True:
        strat_flux = get_stratum_flux(driver, i)
        if strat_flux is None:
            break
        total_flux += strat_flux
        count += 1
        i += 1

    if count > 0:
        return total_flux / count
    else:
        return None

##
# Print functions
##

def print_stratification(driver):
    i = 1
    while True:
        stratum = get_nodes_in_stratum(driver, i)
        if not stratum:
            break
        print(f"Stratum {i}:\t")
        print(stratum)
        print(f"Stratum size: {len(stratum)}")
        i += 1

def print_stratum_fluxes(driver):
    i = 1
    while True:
        strat_flux = get_stratum_flux(driver, i)
        if  not strat_flux:
            break
        print(f"Stratum {i} flux: {strat_flux}")
        i += 1