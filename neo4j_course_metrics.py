##
# Non-weighted degree measures
##

def get_indegree(driver, course_code):
    query = """
    MATCH (p:Paper {name: $targetName})
    RETURN COUNT { ()-[:PREREQ]->(p) } AS inDegree
    """

    records, _, _ = driver.execute_query(query, targetName=course_code)
    return records[0]["inDegree"]

def get_course_path_indegree(driver, course_code):
    query = """
    MATCH (p:Paper {name: $targetName})
    MATCH path = (prereq:Paper)-[:PREREQ*1..]->(p)
    WHERE ALL(c IN nodes(path)[1..-1] WHERE c:Connector)
    RETURN count(path) AS cpInDegree
    """

    records, _, _ = driver.execute_query(query, targetName=course_code)
    return records[0]["cpInDegree"]

def get_outdegree(driver, course_code):
    query = """
    MATCH (p:Paper {name: $targetName})
    RETURN COUNT { (p)-[:PREREQ]->() } AS outDegree
    """

    records, _, _ = driver.execute_query(query, targetName=course_code)
    return records[0]["outDegree"]

def get_course_path_outdegree(driver, course_code):
    query = """
    MATCH (p:Paper {name: $targetName})
    MATCH path = (p)-[:PREREQ*1..]->(postreq:Paper)
    WHERE ALL(c IN nodes(path)[1..-1] WHERE c:Connector)
    RETURN count(path) AS cpOutDegree
    """

    records, _, _ = driver.execute_query(query, targetName=course_code)
    return records[0]["cpOutDegree"]

def get_total_degree(driver, course_code):
    indegree = get_indegree(driver, course_code)
    outdegree = get_outdegree(driver, course_code)
    return indegree + outdegree

def get_total_course_path_degree(driver, course_code):
    cp_indegree = get_course_path_indegree(driver, course_code)
    cp_outdegree = get_course_path_outdegree(driver, course_code)
    return cp_indegree + cp_outdegree

##
# Weighted degree metrics
##

def get_weighted_indegree(driver, course_code):
    query = """
    MATCH ()-[e:PREREQ]->(p:Paper {name: $targetName})
    RETURN sum(e.weight) AS wInDegree
    """

    records, _, _ = driver.execute_query(query, targetName=course_code)
    return records[0]["wInDegree"]

def get_weighted_course_path_indegree(driver, course_code):
    query = """
    MATCH (p:Paper {name: $targetName})
    MATCH path = (prereq:Paper)-[rels:PREREQ*1..]->(p)
    WHERE ALL(c IN nodes(path)[1..-1] WHERE c:Connector)
    RETURN sum(REDUCE(prod = 1.0, r IN rels | prod * coalesce(r.weight, 1.0))) AS wcpInDegree
    """

    records, _, _ = driver.execute_query(query, targetName=course_code)
    return records[0]["wcpInDegree"]

def get_weighted_outdegree(driver, course_code):
    query = """
    MATCH (p:Paper {name: $targetName})-[e:PREREQ]->()
    RETURN sum(e.weight) AS wOutDegree
    """

    records, _, _ = driver.execute_query(query, targetName=course_code)
    return records[0]["wOutDegree"]

def get_weighted_course_path_outdegree(driver, course_code):
    query = """
    MATCH (p:Paper {name: $targetName})
    MATCH path = (p)-[rels:PREREQ*1..]->(postreq:Paper)
    WHERE ALL(c IN nodes(path)[1..-1] WHERE c:Connector)
    RETURN sum(REDUCE(prod = 1.0, r IN rels | prod * coalesce(r.weight, 1.0))) AS wcpOutDegree
    """

    records, _, _ = driver.execute_query(query, targetName=course_code)
    return records[0]["wcpOutDegree"]

def get_total_weighted_degree(driver, course_code):
    w_indegree = get_weighted_indegree(driver, course_code)
    w_outdegree = get_weighted_outdegree(driver, course_code)
    return w_indegree + w_outdegree

def get_total_weighted_course_path_degree(driver, course_code):
    wcp_indegree = get_weighted_course_path_indegree(driver, course_code)
    wcp_outdegree = get_weighted_course_path_outdegree(driver, course_code)
    return wcp_indegree + wcp_outdegree