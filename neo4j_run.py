import pandas as pd
from neo4j import GraphDatabase
import neo4j_functions as nf
import neo4j_metrics as nm

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "[PASSWORD]")

prereqs = pd.read_csv("comp_prereqs.csv")
# prereqs = pd.read_csv("math_prereqs.csv")
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    nf.delete_all(driver)
    nf.populate_db_n_tree(driver, prereqs)
    nm.stratify_db(driver)
    depth = nm.get_curriculum_depth(driver)
    breadth = nm.get_curriculum_breadth(driver)
    flux = nm.get_curriculum_flux(driver)
    print(f"Curriculum depth: {depth}")
    print(f"Curriculum breadth: {breadth}")
    print(f"Curriculum flux: {flux}")