import os
import re
import json
import argparse

def parse_mllog(mllog_line):
    try:
        mmlog_info = json.loads(mllog_line)
    except json.JSONDecodeError as e:
            return None
    else:
        return mmlog_info

def process_file(file_path, test_type):
    patterns = {
        #example line:
        #+ NODELIST=HMYKQ04
        'nodelist': r'^\+ NODELIST=([^\$]+)$',
        #example line:
        #MASTER_PORT 29500, WORLD_SIZE 8, MLPERF_SLURM_FIRSTNODE 2NYKQ04, SLURM_JOB_ID 779,
        'jobID': r'SLURM_JOB_ID (\d+)'
        #example line:
        #:::MLLOG {"namespace": "", "time_ms": 1710009491383, "event_type": "POINT_IN_TIME", 
        'mllog': r'^:::MLLOG (\{.+\})'
    }

    metadata = {
        'test_type': test_type,
        'nodelist': None,
        'jobID': None
    }
    key_events = {
            'run_start':'time_ms',
            'run_stop':'time_ms', 
            'global_batch_size':'value', 
            'local_batch_size':'value',
            'epoch_count':'value',
            'submission_benchmark':'value',
            'init_start':'time_ms']

    run_events = []

    with open(file_path, 'r') as file:
        for line in file:
            if not metadata['nodelist'] and patterns['nodelist'].match(line):
                metadata['nodelist'] = patterns['nodelist'].match(line).group(1)
            elif not metadata['jobID'] and patterns['jobID'].match(line):
                metadata['jobID'] = patterns['jobID'].match(line).group(1)
            elif patterns['mllog'].match(line):
                parse_mllog(patterns['mllog'].match(line).group(1))
            if mllog_info:
                run_events.append(mllog_info)

    for event in run_events:
        output = metadata.copy()
        output.update(event)
        print(json.dumps(output))

def main(directory_path, test_type):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isdir(file_path):
            continue

        print(f"Processing file: {filename}")
        process_file(file_path, test_type)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process log files.", add_help=False)
    parser.add_argument("-d", "--directory", required=True, type=str, help="Directory containing log files.")
    parser.add_argument("-t", "--test_type", required=True, type=str, help="Type of test.")
    
    args = parser.parse_args()
    
    main(args.directory, args.test_type)

