import pandas as pd
from neo4j import GraphDatabase
import neo4j_functions as nf

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "[PASSWORD HERE]")

# prereqs = pd.read_csv("test.csv")
prereqs = pd.read_excel("prereqs_tidied.xlsx")
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    nf.delete_all(driver)
    nf.populate_db_n_tree(driver, prereqs)