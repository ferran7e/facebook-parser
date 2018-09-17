from argparse import ArgumentParser
import os
import logging
import sys
import json
import pprint
from nested_lookup import nested_lookup
import datetime
import time
import xlsxwriter

logging.basicConfig()
log = logging.getLogger('FB-PARSER')
log.setLevel(logging.INFO)

def check_file(file_path):
    if os.path.isfile(file_path):
        return True
    else:
        return False

def check_folder(folder_path):
    if os.path.isdir(folder_path):
        return True
    else:
        return False

def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument('folder_path', metavar='folder_path', nargs=1)
    parsed_arguments = parser.parse_args()
    directory_path = parsed_arguments.folder_path[0]


    # Check for the directory path.
    if check_folder(directory_path):
        log.info('Specified directory is valid')
        return directory_path
    else:
        sys.exit('\n*** This file path is not valid. Terminating. ***\n')

def collect_JSON(directory_path):
    json_files = []

    for subdir, dirs, files in os.walk(directory_path):
        for file in files:
            ext = os.path.splitext(file)[-1].lower()
            if ext == '.json':
                json_files.append(os.path.join(subdir, file))
    return json_files

def collect_timestamps(json_files):
    timestamps = []
    for json_item in json_files:
        with open(json_item, 'r') as fp:
            data = json.load(fp)

            timestamp_vars = [
                'timestamp',
                'creation_timestamp',
                'modified_timestamp',
                'last_modified_timestamp',
                'start_timestamp',
                'registration_timestamp'
                ]
            for timestamp_lingo in timestamp_vars:
                found_timestamps = nested_lookup(timestamp_lingo, data)
                for ts in found_timestamps:
                    timestamps.append(datetime.datetime.fromtimestamp(ts))

            ms_timestamps = nested_lookup('timestamp_ms', data)
            for ts in ms_timestamps:
                timestamps.append(datetime.datetime.fromtimestamp(ts/1000))

    return timestamps

def stamps_to_file(timestamps):
    count = 0
    output_name = 'output-' + str(time.time()) +'.xlsx'
    workbook = xlsxwriter.Workbook(output_name)
    worksheet = workbook.add_worksheet(name="Timestamps")

    for ts in timestamps:
        formatted_ts = ts.strftime('%m/%d/%y %H:%M')
        worksheet.write(count, 0, formatted_ts)
        worksheet.write(count, 1, ts)

        count += 1

    workbook.close()

    return True, output_name

if __name__ == '__main__':
    log.info('FACEBOOK-PARSER IS STARTING')
    directory_path = parse_arguments()
    json_files = collect_JSON(directory_path)
    timestamps = sorted(collect_timestamps(json_files))
    success, output_name = stamps_to_file(timestamps)

    if success:
        log.info('OPERATION COMPLETED SUCCESSFULLY!')
        log.info('Filename: ' + output_name)













