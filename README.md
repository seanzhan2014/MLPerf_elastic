# MLPerf_elastic

This project provides a Python script for analyzing log files, extracting specific information based on keywords, and storing the results in Elasticsearch for further analysis and visualization with Kibana.

## Features

- Searches for specific keywords in slurm output files (e.g., `nodelist`, `jobID`, `run_start`, `run_stop`).
- Extracts and aggregates relevant data from log files.
- Stores the extracted data in Elasticsearch for analysis and visualization.

## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.6 or later is installed.
- Elasticsearch 7.x or later is up and running.
- The `elasticsearch` Python package is installed.

## Installing the Project

To install the project, follow these steps:

1. Clone the repository to your local machine:
