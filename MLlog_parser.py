import os
import re
import json
import argparse
import socket
import time

LOGSTASH_HOST = '127.0.0.1' 
LOGSTASH_PORT = 5044 


KEY_EVENTS = {
    'run_start':'time_ms',
    'run_stop':'time_ms', 
    'global_batch_size':'value', 
    'local_batch_size':'value',
    'epoch_count':'value',
    'submission_benchmark':'value',
    'init_start':'time_ms',
    'init_stop':'time_ms',
    'train_samples':'value',
    'eval_samples':'value'
}

PATTERNS = {
    #example line:
    #+ NODELIST=HMYKQ04
    #'nodelist': re.compile(r'^\+ NODELIST=([^\$]+)$'),
    #example line:
    #MASTER_PORT 29500, WORLD_SIZE 8, MLPERF_SLURM_FIRSTNODE 2NYKQ04, SLURM_JOB_ID 779,
    #'jobID': re.compile(r'SLURM_JOB_ID (\d+)'),
    #example line:
    #:::DLPAL /mnt/weka/MLPerf/smc_run/ssd.sqsh 778 1 2NYKQ04 'unknown' SMC_H100
    'dlpal': re.compile(r'^:::DLPAL (\S*) (\S*) (\S*) (\S*) (\S*) (\S*)'),
    #example line:
    #:::MLLOG {"namespace": "", "time_ms": 1710009491383, "event_type": "POINT_IN_TIME", 
    'mllog': re.compile(r'^:::MLLOG (\{.+\})')
}

def parse_mllog(mllog_line):
    try:
        mllog_raw_info = json.loads(mllog_line)
    except json.JSONDecodeError as e:
            return None
    if mllog_raw_info['key'] in  KEY_EVENTS:
        return {mllog_raw_info['key']: mllog_raw_info[KEY_EVENTS[mllog_raw_info['key']]]}

def process_file(file_path):

    run_events = {}
    #= metadata.copy()

    with open(file_path, 'r') as file:
        metadata = {
            'container':None,
            'jobID': None,
            'nodenum': None,
            'nodelist': None,
            'machine_type': None,
            'source_log': None
        }
        for line in file:
            mllog_info = None
            m = PATTERNS['dlpal'].match(line)
            if m:
                metadata['container'] = m.group(1)
                metadata['jobID'] = m.group(2)
                metadata['nodenum'] = m.group(3)
                metadata['nodelist'] = m.group(4)
                metadata['machine_type'] = m.group(6)
            m =  PATTERNS['mllog'].match(line)
            if m:
                mllog_line = m.group(1)
                mllog_info = parse_mllog(mllog_line)
            if mllog_info:
                run_events.update(mllog_info)
    if run_events:
        run_events.update(metadata)
        run_events['source_log']=file_path
        return json.dumps(run_events)

def main(directory_path):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((LOGSTASH_HOST, LOGSTASH_PORT))
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        #file_path = "/home/ubuntu/sample_logs/smc_run/logs/ssd/ssd_run_logs/240309224319669447555_5.log"
        if os.path.isdir(file_path):
            continue
        json_data = process_file(file_path)
        if json_data:
            print(json_data)
            json_data += "\n"
            sock.sendall(json_data.encode('utf-8'))

    sock.shutdown(socket.SHUT_WR)
    sock.close()
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process log files.", add_help=False)
    parser.add_argument("-d", "--directory", required=True, type=str, help="Directory containing log files.")
    
    args = parser.parse_args()
    
    main(args.directory)

