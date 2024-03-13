# MLPerf_elastic

A Python script for analyzing MLPerf log files, extracting specific information based on keywords, send the results to logtash to store in Elasticsearch for further analysis and visualization with Kibana.
It also gives an example of logstash conf file.

## Features

- Searches for specific keywords in slurm output files (e.g., `nodelist`, `jobID`, `run_start`, `run_stop`).
- Extracts and aggregates relevant data from log files.
- Stores the extracted data in Elasticsearch for analysis and visualization.
- It only scan the MLPerf log file (specified by env variable LOGDIR). Scanning the slurm output file can get wrong result.

## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.6 or later is installed.
- Elasticsearch 7.x or later is up and running.
- The `elasticsearch` Python package is installed.

## Installing the Project

To install the project, follow these steps:

1. Clone the repository to your local machine
2. Change the logstash info in the script
3. Run it "python MLlog_parser.py -d <MLPerf log>"
