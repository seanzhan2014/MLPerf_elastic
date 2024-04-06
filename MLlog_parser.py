import os
import re
import json
import argparse
import socket
import time

LOGSTASH_HOST = '10.250.250.11' 
LOGSTASH_PORT = 5044 

MLPARSER_REC = "./mllog-parser.rec"

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
    #:::DLPAL /mnt/weka/MLPerf/smc_run/ssd.sqsh 778 1 2NYKQ04 'unknown' SMC_H100
    'dlpal': re.compile(r'^:::DLPAL (\S*) (\S*) (\S*) (\S*) (\S*) (\S*)'),
    #example line:
    #:::MLLOG {"namespace": "", "time_ms": 1710009491383, "event_type": "POINT_IN_TIME", 
    'mllog': re.compile(r'.*:::MLLOG (\{.+\})')
}

def parse_mllog(mllog_line):
    try:
        mllog_raw_info = json.loads(mllog_line)
    except json.JSONDecodeError as e:
            return None
    if mllog_raw_info['key'] in  KEY_EVENTS:
        #special case for mllog contains run_stop: if not success, then ignore
        if mllog_raw_info['key'] == "run_stop":
            if mllog_raw_info['metadata'] and  mllog_raw_info['metadata']['status']!= "success": 
                return None
        return {mllog_raw_info['key']: mllog_raw_info[KEY_EVENTS[mllog_raw_info['key']]]}

def process_file(file_path):
    run_events = {}

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
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
        run_events['run_time'] = 0
        if not 'run_start' in run_events.keys() or not 'run_stop' in run_events.keys():
            return None
        if run_events['run_start'] is None or run_events['run_stop'] is None :
            return None
        run_events['run_time'] = (int(run_events['run_stop']) - int(run_events['run_start']))/1000
        return json.dumps(run_events)

def main(directories):
    processed_logs = []
    if os.path.exists(MLPARSER_REC):
        with open(MLPARSER_REC, 'r') as rec_file:
            for line in rec_file:
                log_dict = json.loads(line)
                if 'source_log' in log_dict:
                    processed_logs.append(log_dict['source_log'])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((LOGSTASH_HOST, LOGSTASH_PORT))
    rec_file = open(MLPARSER_REC, 'a')
    directory_list = directories.split(',')
    for directory_path in directory_list:
        for filename in os.listdir(directory_path):
            if not filename.endswith(".log"):
                continue
            file_path = os.path.join(directory_path, filename)
            if os.path.isdir(file_path):
                continue
            if file_path in processed_logs:
                continue
            json_data = process_file(file_path)
            if json_data:
                print(json_data)
                json_data += "\n"
                rec_file.write(json_data)
                sock.sendall(json_data.encode('utf-8'))
    rec_file.close()
    sock.shutdown(socket.SHUT_WR)
    sock.close()
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process log files.", add_help=False)
    parser.add_argument("-d", "--directories", required=True, type=str, help="Directory list of MLPerf log files. Multiple directories have to be seperate by comma.")
    
    args = parser.parse_args()
    
    main(args.directories)

