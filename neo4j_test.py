# python -m pytest neo4j_test.py -s

import time
import pandas as pd
import pytest
from neo4j import GraphDatabase
import neo4j_functions as nf

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "[PASSWORD HERE]")

@pytest.fixture(scope="module")
def db_driver():
    """Manages the lifecycle of the database driver."""
    driver = GraphDatabase.driver(URI, auth=AUTH)
    yield driver
    driver.close()

def get_query_performance(db_driver, query, num_rounds):
    delta_sum = 0

    with db_driver.session() as session:
        for i in range(num_rounds):
            session.run("CALL db.clearQueryCaches()")

            start_time = time.perf_counter()

            result = session.run(query)
            result.consume()
            
            end_time = time.perf_counter()
            
            delta_sum += end_time - start_time
    
    delta_mean = delta_sum / float(num_rounds)
    return delta_mean

def run_compare_query(db_driver, query):
    print(f"\n\nResults for query:\n{query}\n")

    prereqs = pd.read_excel("prereqs_tidied.xlsx")

    nf.delete_all(db_driver)
    nf.populate_db_bin_tree(db_driver, prereqs)
    time = get_query_performance(db_driver, query, 5)
    print(f"\nAverage query execution time for binary tree:\n\n{time:.4f}s")

    nf.delete_all(db_driver)
    nf.populate_db_n_tree(db_driver, prereqs)
    time = get_query_performance(db_driver, query, 5)
    print(f"\nAverage query execution time for n-tree:\n\n{time:.4f}s")

    nf.delete_all(db_driver)
    nf.populate_db_num(db_driver, prereqs, divide_on="or")
    time = get_query_performance(db_driver, query, 5)
    print(f"\nAverage query execution time for numerical model (dividing on OR):\n\n{time:.4f}s")

    nf.delete_all(db_driver)
    nf.populate_db_partial_num(db_driver, prereqs)
    time = get_query_performance(db_driver, query, 5)
    print(f"\nAverage query execution time for semi-numerical model:\n\n{time:.4f}s")

def run_compare_queries(db_driver, query1, query2, query3, query4):
    prereqs = pd.read_excel("prereqs_tidied.xlsx")

    nf.delete_all(db_driver)
    nf.populate_db_bin_tree(db_driver, prereqs)
    time = get_query_performance(db_driver, query1, 5)
    print(f"\nResults for query\n{query1}")
    print(f"\nAverage query execution time for binary tree:\n\n{time:.4f}s")

    nf.delete_all(db_driver)
    nf.populate_db_n_tree(db_driver, prereqs)
    time = get_query_performance(db_driver, query2, 5)
    print(f"\nResults for query\n{query2}")
    print(f"\nAverage query execution time for n-tree:\n\n{time:.4f}s")

    nf.delete_all(db_driver)
    nf.populate_db_num(db_driver, prereqs, divide_on="or")
    time = get_query_performance(db_driver, query3, 5)
    print(f"\nResults for query\n{query3}")
    print(f"\nAverage query execution time for numerical model (dividing on OR):\n\n{time:.4f}s")

    nf.delete_all(db_driver)
    nf.populate_db_partial_num(db_driver, prereqs)
    time = get_query_performance(db_driver, query4, 5)
    print(f"\nResults for query\n{query4}")
    print(f"\nAverage query execution time for semi-numerical model:\n\n{time:.4f}s")




##
# Tests
##

def test_match_papers(db_driver):
    query = """
    MATCH (p:Paper)
    RETURN p
    """

    run_compare_query(db_driver, query)

def test_match_prereqs(db_driver):
    query = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    """

    run_compare_query(db_driver, query)

def test_optional_match_prereqs(db_driver):
    query = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n, r, m
    """

    run_compare_query(db_driver, query)

def test_find_mandatory_prereqs(db_driver):
    query1 = query2 = """
    MATCH path = (in:Paper)-[:PREREQ*1..]->(p:Paper {name: 'COMP 325'})
    WHERE all(node IN nodes(path)[1..-1] WHERE node:Connector AND node.name = 'and')
    RETURN DISTINCT in
    """

    query3 = """
    MATCH (in:Paper)-[:PREREQ {weight: 1.0}]->(p:Paper {name: 'COMP 325'})
    RETURN in
    """

    query4 = """
    MATCH path = (in:Paper)-[:PREREQ {weight: 1.0}]->(p:Paper {name: 'COMP 325'})
    WHERE all(node IN nodes(path)[1..-1] WHERE node:Connector)
    RETURN DISTINCT in
    """

    run_compare_queries(db_driver, query1, query2, query3, query4)
