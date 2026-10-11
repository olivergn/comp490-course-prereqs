import argparse
import os
import logging
import pandas as pd
from neo4j import GraphDatabase
import neo4j_functions as nf
import neo4j_curriculum_metrics as ncum
import neo4j_course_metrics as ncom
import report_gen as rg

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
DB_PASSWORD = os.getenv("DB_PASSWORD", "[PASSWORD]")
AUTH = ("neo4j", DB_PASSWORD)

logging.getLogger("neo4j").setLevel(logging.ERROR)

parser = argparse.ArgumentParser()
parser.add_argument(
    "-t", "--task",
    type=str,
    choices=["all", "curriculum", "course"],
    default="all",
    help="The task suite (all, curriculum, course) to be run (default: all)"
)
parser.add_argument(
    "-m", "--model",
    type=str,
    choices=["m1", "m2", "m3", "m4"],
    default="m2",
    help="The model (m1, m2, m3, m4) to implement the CPN (default: m2)"
)
parser.add_argument(
    "-f", "--file",
    type=str,
    default="comp_prereqs.csv",
    help="The prerequisites file used to produce the CPN (default: comp_prereqs.csv)"
)

args = parser.parse_args()

def run_pipeline():
    task = args.task
    model = args.model
    prereqs = pd.read_csv(args.file)

    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()

        nf.delete_all(driver)

        if model == "m1":
            nf.populate_db_bin_tree(driver, prereqs)
        elif model == "m2":
            nf.populate_db_n_tree(driver, prereqs)
        elif model == "m3":
            nf.populate_db_num(driver, prereqs)
        elif model == "m4":
            nf.populate_db_partial_num(driver, prereqs)

        ncum.stratify_db(driver)
        ncom.delete_projections(driver)
        ncom.create_projections(driver)

        if task in ["all", "curriculum"]:
            depth = ncum.get_curriculum_depth(driver)
            breadth = ncum.get_curriculum_breadth(driver)
            flux = ncum.get_curriculum_flux(driver)
            print("Curriculum level metrics:\n")
            print(f"Curriculum depth: {depth}")
            print(f"Curriculum breadth: {breadth}")
            print(f"Curriculum flux: {flux}")

        if task in ["all", "course"]:
            print("\nCourse level metrics:\n")
            papers = ncum.get_all_papers(driver)
            papers.sort()
            rg.print_degree_report(driver, papers)
            if model == "m3" or model == "m4":
                rg.print_weighted_report(driver, papers)
            rg.print_misc_report(driver, papers)

if __name__ == "__main__":
    run_pipeline()
