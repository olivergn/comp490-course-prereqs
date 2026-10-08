##
# Preparation functions
##
def delete_projections(driver):
    driver.execute_query("CALL gds.graph.drop('cpn', false)")
    driver.execute_query("CALL gds.graph.drop('cpn-papers-only', false)")

def create_projections(driver):
    exists_query = """
    CALL gds.graph.exists($graphName)
    YIELD exists
    """
    cpn_project_query = """
    CALL gds.graph.project(
        'cpn',
        ['Paper', 'Connector'],
        {
            PREREQ: {
                type: 'PREREQ',
                // Reverse so that centrality is conferred backwards
                orientation: 'REVERSE'
            }
        }
    )
    """
    cpn_op_project_query = """
    CALL gds.graph.project.cypher(
        'cpn-papers-only',
        'MATCH (p:Paper) RETURN id(p) AS id, ["Paper"] AS labels',
        'MATCH path = (p1:Paper)-[:PREREQ*1..]->(p2:Paper)
            WHERE p1 <> p2
            AND ALL(c IN nodes(path)[1..-1] WHERE c:Connector)
        // Invert so that centrality is conferred backwards
        RETURN id(p2) AS source, id(p1) AS target, "PREREQ_DIRECT" as type'
    )
    """

    records, _, _ = driver.execute_query(exists_query, graphName="cpn")
    if not (records and records[0]["exists"]):
        driver.execute_query(cpn_project_query)

    records, _, _ = driver.execute_query(exists_query, graphName="cpn-papers-only")
    if not (records and records[0]["exists"]):
        driver.execute_query(cpn_op_project_query)

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

##
# Out-component size metrics
##

def get_outcomponent_size(driver, course_code):
    query = """
    MATCH (p:Paper {name: $targetName})
    MATCH (p)-[:PREREQ*1..]->(postreq:Paper)
    RETURN count(DISTINCT postreq) AS outCompSize
    """

    records, _, _ = driver.execute_query(query, targetName=course_code)
    return records[0]["outCompSize"]

def get_weighted_downstream_impact(driver, course_code):
    query = """
    MATCH (p:Paper {name: $targetName})
    MATCH (p)-[rels:PREREQ*1..]->(postreq:Paper)
    RETURN sum(REDUCE(prod = 1.0, r IN rels | prod * coalesce(r.weight, 1.0))) AS wdImpact
    """

    records, _, _ = driver.execute_query(query, targetName=course_code)
    return records[0]["wdImpact"]

##
# Betweenness and PageRank centrality
##

def get_betweenness(driver, course_code):
    query = """
    CALL gds.betweenness.stream('cpn')
    YIELD nodeId, score
    WITH gds.util.asNode(nodeId) AS p, score
    WHERE p:Paper and p.name = $targetName
    RETURN score AS betweenness
    """

    records, _, _ = driver.execute_query(query, targetName=course_code)
    return records[0]["betweenness"]

def get_no_connectors_betweenness(driver, course_code):
    query = """
    CALL gds.betweenness.stream('cpn-papers-only')
    YIELD nodeId, score
    WITH gds.util.asNode(nodeId) AS p, score
    WHERE p:Paper and p.name = $targetName
    RETURN score AS ncBetweenness
    """

    records, _, _ = driver.execute_query(query, targetName=course_code)
    return records[0]["ncBetweenness"]

def get_pagerank(driver, course_code):
    query = """
    CALL gds.pageRank.stream('cpn')
    YIELD nodeId, score
    WITH gds.util.asNode(nodeId) AS p, score
    WHERE p:Paper and p.name = $targetName
    RETURN score AS pagerank
    """

    records, _, _ = driver.execute_query(query, targetName=course_code)
    return records[0]["pagerank"]

def get_no_connectors_pagerank(driver, course_code):
    query = """
    CALL gds.pageRank.stream('cpn-papers-only')
    YIELD nodeId, score
    WITH gds.util.asNode(nodeId) AS p, score
    WHERE p:Paper and p.name = $targetName
    RETURN score AS ncPagerank
    """

    records, _, _ = driver.execute_query(query, targetName=course_code)
    return records[0]["ncPagerank"]