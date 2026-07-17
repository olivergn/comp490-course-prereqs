# python -m pytest neo4j_test_2.py -s

import time
import pandas as pd
import pytest
from neo4j import GraphDatabase
import neo4j_functions as nf
import random
import os

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = ("neo4j", "[PASSWORD]")

@pytest.fixture(scope="module")
def db_driver():
    """Manages the lifecycle of the database driver."""
    driver = GraphDatabase.driver(URI, auth=AUTH)
    yield driver
    driver.close()

def get_query_performance(db_driver, query):
    time_taken = 0

    with db_driver.session() as session:
        session.run("CALL db.clearQueryCaches()")

        start_time = time.perf_counter()

        result = session.run(query)
        result.consume()
        
        end_time = time.perf_counter()
        
        time_taken = end_time - start_time
    
    return time_taken

def run_query_performance_round(db_driver, query, prereqs, schedule, results):
    for i in schedule:
        nf.delete_all(db_driver)
        if i == 0:
            nf.populate_db_bin_tree(db_driver, prereqs)
        elif i == 1:
            nf.populate_db_n_tree(db_driver, prereqs)
        elif i == 2:
            nf.populate_db_num(db_driver, prereqs)
        elif i == 3:
            nf.populate_db_partial_num(db_driver, prereqs)
        time = get_query_performance(db_driver, query)
        results[i] += time

def run_multiple_query_performance_round(db_driver, query1, query2, query3, query4, prereqs, schedule, results):
    for i in schedule:
        nf.delete_all(db_driver)
        time = 0
        if i == 0:
            nf.populate_db_bin_tree(db_driver, prereqs)
            time = get_query_performance(db_driver, query1)
        elif i == 1:
            nf.populate_db_n_tree(db_driver, prereqs)
            time = get_query_performance(db_driver, query2)
        elif i == 2:
            nf.populate_db_num(db_driver, prereqs)
            time = get_query_performance(db_driver, query3)
        elif i == 3:
            nf.populate_db_partial_num(db_driver, prereqs)
            time = get_query_performance(db_driver, query4)
        results[i] += time

def get_avg_query_performance(db_driver, query, num_rounds):
    prereqs = pd.read_csv("prereqs_tidied.csv")
    results = [0,0,0,0]

    for i in range(num_rounds):
        schedule = [0,1,2,3]
        random.shuffle(schedule)
        run_query_performance_round(db_driver, query, prereqs, schedule, results)
    
    for i in range(len(results)):
        results[i] = float(results[i]) / num_rounds
    
    return results

def get_avg_multiple_queries_performance(db_driver, query1, query2, query3, query4, num_rounds):
    prereqs = pd.read_csv("prereqs_tidied.csv")
    results = [0,0,0,0]

    for i in range(num_rounds):
        schedule = [0,1,2,3]
        random.shuffle(schedule)
        run_multiple_query_performance_round(db_driver, query1, query2, query3, query4, prereqs, schedule, results)
    
    for i in range(len(results)):
        results[i] = float(results[i]) / num_rounds
    
    return results

def print_avg_query_performance(db_driver, query, num_rounds):
    results = get_avg_query_performance(db_driver, query, num_rounds)
    print(f"\n\nResults for query:\n{query}\n")
    print(f"\nAverage query execution time for binary tree:\n\n{results[0]:.4f}s")
    print(f"\nAverage query execution time for n-tree:\n\n{results[1]:.4f}s")
    print(f"\nAverage query execution time for numerical model:\n\n{results[2]:.4f}s")
    print(f"\nAverage query execution time for partial numerical model:\n\n{results[3]:.4f}s")

def print_avg_multiple_query_performance(db_driver, query1, query2, query3, query4, num_rounds):
    results = get_avg_multiple_queries_performance(db_driver, query1, query2, query3, query4, num_rounds)
    print(f"\n\nResults for multiple queries:\n")
    print(f"\nAverage execution time for binary tree:\nQuery:\n{query1}\n\n{results[0]:.4f}s")
    print(f"\nAverage execution time for n-tree:\nQuery:\n{query2}\n\n{results[1]:.4f}s")
    print(f"\nAverage execution time for numerical model:\nQuery:\n{query3}\n\n{results[2]:.4f}s")
    print(f"\nAverage execution time for partial numerical model:\nQuery:\n{query4}\n\n{results[3]:.4f}s")

def print_results(db_driver, query):
    with db_driver.session() as session:
        result = session.run(query)
        for record in result:
            print(record)
        result.consume()

##
# Tests
##

def test_match_papers(db_driver):
    query = """
    MATCH (p:Paper)
    RETURN p
    """

    print_avg_query_performance(db_driver, query, 5)

def test_match_edges(db_driver):
    query = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    """

    print_avg_query_performance(db_driver, query, 5)

def test_optional_match_edges(db_driver):
    query = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n, r, m
    """

    print_avg_query_performance(db_driver, query, 5)

def test_find_mandatory_prereqs(db_driver):
    query1 = query2 = """
    MATCH path = (p:Paper)-[:PREREQ*1..]->
        (:Paper {name: "COMP 325"})
    WHERE all(c IN nodes(path)[1..-1]
    WHERE c:Connector AND c.name = "and")
    RETURN DISTINCT p
    """

    query3 = """
    MATCH (p:Paper)-[:PREREQ {weight: 1.0}]->
    (:Paper {name: "COMP 325"})
    RETURN DISTINCT p
    """

    query4 = """
    MATCH path = (p:Paper)-[:PREREQ*1..]->
        (:Paper {name: "COMP 325"})
    WHERE all(c IN nodes(path)[1..-1] WHERE c:Connector)
    AND all(e IN relationships(path) WHERE e.weight = 1.0)
    RETURN DISTINCT p
    """

    print_avg_multiple_query_performance(db_driver, query1, query2, query3, query4, 5)

def test_find_all_prereqs(db_driver):
    query1 = query2 = query4 = """
    MATCH path = (p:Paper)-[:PREREQ*1..]->
        (:Paper {name: "COMP 325"})
    WHERE all(c IN nodes(path)[1..-1] WHERE c:Connector)
    RETURN DISTINCT p
    """

    query3 = """
    MATCH (p:Paper)-[:PREREQ]->
        (:Paper {name: "COMP 325"})
    RETURN DISTINCT p
    """

    print_avg_multiple_query_performance(db_driver, query1, query2, query3, query4, 5)

def test_compare_avg_path_length(db_driver):
    prereqs = pd.read_csv("prereqs_tidied.csv")
    query = """
    MATCH (a:Paper), (b:Paper)
    WHERE a <> b
    MATCH p = shortestPath((a)-[*]->(b))
    RETURN avg(length(p))
    """

    nf.delete_all(db_driver)
    nf.populate_db_bin_tree(db_driver, prereqs)
    print(f"\nResults for binary tree:\n")
    print_results(db_driver, query)

    nf.delete_all(db_driver)
    nf.populate_db_n_tree(db_driver, prereqs)
    print(f"\nResults for n-tree:\n")
    print_results(db_driver, query)

    nf.delete_all(db_driver)
    nf.populate_db_num(db_driver, prereqs, divide_on="or")
    print(f"\nResults for numerical model:\n")
    print_results(db_driver, query)

    nf.delete_all(db_driver)
    nf.populate_db_partial_num(db_driver, prereqs)
    print(f"\nResults for partial numerical model:\n")
    print_results(db_driver, query)
