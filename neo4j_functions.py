import pandas as pd
import re
from neo4j import GraphDatabase

import token_functions as tf

def delete_all(driver):
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

##
# Add prereqs functions
##

def add_prereqs_trad(driver, dest_id, prereq):
    if isinstance(prereq, str):
        query = """
        MERGE (p:Paper {name: $prereqName})
        MATCH (n)
        WHERE elementId(n) = $id
        MERGE (p)-[:PREREQ]->(n)
        """
        _, _, _ = driver.execute_query(query, prereqName=prereq, id=dest_id)
    else:
        query = """
        CREATE (c:Connector {name: $connectorName})
        MATCH (n)
        WHERE elementId(n) = $id
        MERGE (c)-[:PREREQ]->(n)
        RETURN c
        """
        records, _, _ = driver.execute_query(query, connectorName=prereq[0], id=dest_id)
        id = records[0]["c"].element_id
        for i in range(1, len(prereq)):
            add_prereqs_trad(driver, id, prereq[i])

def add_prereqs_num(driver, dest_id, prereq, weight, divide_on="or"):
    if isinstance(prereq, str):
        query = """
        MERGE (p:Paper {name: $prereqName})
        MATCH (n)
        WHERE elementId(n) = $id
        MERGE (p)-[:PREREQ {weight: $weight}]->(n)
        """
        _, _, _ = driver.execute_query(query, prereqName=prereq, id=dest_id, weight=weight)
    else:
        if (prereq[0] == divide_on):
            for i in range(1, len(prereq)):
                add_prereqs_num(driver, dest_id, prereq[i], weight / (len(prereq) - 1))
        else:
            for i in range(1, len(prereq)):
                add_prereqs_num(driver, dest_id, prereq[i], weight)

##
# Add row functions
##

def add_row_trad(driver, row, collapse_option=False):
    paper = str(row['Paper'])
    query = """
    MERGE (p:Paper {name: $paperName})
    RETURN p
    """
    records, _, _ = driver.execute_query(query, paperName=paper)
    id = records[0]["p"].element_id

    if pd.notna(row['Primary prerequisite']):
        prereq = tf.parse_tokens(tf.tokenize(str(row['Primary prerequisite'])))
        if collapse_option:
            prereq = tf.collapse_tokens(prereq)
        add_prereqs_trad(driver, id, prereq)

def add_row_num(driver, row, divide_on="or"):
    paper = str(row['Paper'])
    query = """
    MERGE (p:Paper {name: $paperName})
    RETURN p
    """
    records, _, _ = driver.execute_query(query, paperName=paper)
    id = records[0]["p"].element_id

    if pd.notna(row['Primary prerequisite']):
        prereq = tf.collapse_tokens(tf.parse_tokens(tf.tokenize(str(row['Primary prerequisite']))))
        add_prereqs_num(driver, id, prereq, weight=1.0, divide_on=divide_on)

##
# Populate functions
##

def populate_db_bin_tree(driver, prereqs):
    for index, row in prereqs.iterrows():
        add_row_trad(driver, row)

def populate_db_n_tree(driver, prereqs):
    for index, row in prereqs.iterrows():
        add_row_trad(driver, row, collapse_option=True)

def populate_db_num(driver, prereqs, divide_on="or"):
    for index, row in prereqs.iterrows():
        add_row_num(driver, row, divide_on=divide_on)