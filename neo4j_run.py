import pandas as pd
from neo4j import GraphDatabase
import neo4j_functions as nf
import neo4j_curriculum_metrics as ncum
import neo4j_course_metrics as ncom
import report_gen as rg

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "[PASSWORD]")

# Comment according to curriculum under consideration
prereqs = pd.read_csv("comp_prereqs.csv")
# prereqs = pd.read_csv("math_prereqs.csv")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    nf.delete_all(driver)

    # Comment according to model under consideration
    nf.populate_db_n_tree(driver, prereqs) # M_2
    # nf.populate_db_partial_num # M_4

    ncum.stratify_db(driver)
    ncom.delete_projections(driver)
    ncom.create_projections(driver)

    depth = ncum.get_curriculum_depth(driver)
    breadth = ncum.get_curriculum_breadth(driver)
    flux = ncum.get_curriculum_flux(driver)
    print("Curriculum level metrics:\n")
    print(f"Curriculum depth: {depth}")
    print(f"Curriculum breadth: {breadth}")
    print(f"Curriculum flux: {flux}")

    print("\nCourse level metrics:\n")
    papers = ncum.get_all_papers(driver)
    papers.sort()
    rg.print_misc_report(driver, papers)
