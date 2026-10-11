# COMP490 Course Prerequisites Investigation Code
This code was developed for the data-gathering and results stage of my COMP490 dissertation investigating nested Boolean course prerequisites in course prerequisite networks (CPNs). It includes functionality to generate a CPN, compute adapted course-level and curriculum-level measures of a CPN, and test a CPN's performance.

To run, use the following Docker commands:

`docker compose up --build --abort-on-container-exit` - spin up Neo4j database container

`docker compose run --rm test-runner` - run performance and other tests used for stage 1 of the investigation

`docker compose run --rm test-runner python neo4j_run.py` - run structural course and curriculum tests used for stage 2 of the investigation

`docker compose run --rm test-runner python neo4j_run.py -t [TASK] -m [MODEL] -f [FILENAME]` - run structural course and curriculum tests with options:
- `[TASK]` refers to which investigation to run, `course`, `curriculum`, or `all`
- `[MODEL]` refers to which implementation model to use, `m1` through `m4` (only `m2` and `m4` tested)
- `[FILENAME]` refers to which course prerequisites CSV file to run