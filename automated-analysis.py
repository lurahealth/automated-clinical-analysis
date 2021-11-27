#!/usr/bin/env python 
import argparse
import sys
import csv
import os
from pathlib import Path

# Parses file stored at "path" that describes patient ID <> device ID 
# relationships. Returns an array of patient IDs and device IDs, such
# that patient_id[i] is related to device_id[i]
def parse_ID_relations_file(path):
    patient_ids = []
    device_ids  = []
    id_relations_file = open(path, 'r')
    csvreader = csv.reader(id_relations_file, delimiter=',')
    header = next(csvreader) # I don't really need the header but,
    for row in csvreader:
        # patient_ids[X] will be related to device_ids[X]
        patient_ids.append(row[0]) # row[0] is the patient ID
        device_ids.append(row[1]) # row[1] is the active device ID
    
    return patient_ids, device_ids

# Appends csv file at file_path_to_merge to device_id file in the
# merged files location
def append_csv_by_device_id(device_id, file_path_to_merge):
    merged_filepath = "../lura_files/MERGED-CLINICAL-CSV/device_"
    merged_file = merged_filepath + device_id + ".csv"
    with open(file_path_to_merge, mode='r') as new_file:
        new_csv_data = new_file.read()
    
    with open(merged_file, mode='a') as big_file:
        big_file.write(new_csv_data)
        
# Search directory and subdirectories for pH receiver data,
# the device ID files could be in any patient ID subdirectory
def collect_patient_csv_files(patient_ids, device_ids):
    path = "../lura_files/" # this is bad but easier to test across hardwares
    id_prefix = path + "ble-receiver"
    tablet_id = "clinical-tabletA"     # Make sure to check the tablet too :)
    for patient_id in patient_ids:
        # search ph receiver directory for all active pH retainers
        for device_id in device_ids:
            device_id_file = "LuraHealth_" + device_id + ".csv"
            filename = id_prefix + patient_id + "/csv_files/"
            complete_filename = filename + device_id_file
            full_dir_path = id_prefix + patient_id + "/csv_files/"
            # If device ID file exists in patient ID directory, collect it
            patient_dir = os.listdir(full_dir_path)
            if device_id_file in patient_dir:
                append_csv_by_device_id(device_id, complete_filename)

# Need to write to a temp file, delete previous file, and change temp name
def clean_up_csv_formatting(full_file_path, root_path, device_file):
    correct_header = "Time,pH,temp,batt,pHmV\n"
    current_header = "Time (YYYY-MM-DD HH-MM-SS),pH (calibrated),temp (mv),batt (mv),pH (mv)"
    temp_filename = root_path + "TEMP" + device_file
    # Open both files, dirty and temp
    with open(full_file_path, mode='r') as dirty_file:
        with open(temp_filename, mode='a') as temp_file:
            temp_file.write(correct_header) # give it the right header
            # Write everything except lines with headers or empty newlines
            for line in dirty_file:
                if current_header not in line and line != '\n':
                    temp_file.write(line)
                    
        

def sort_merged_csv_files_by_date():
    root_path = "../lura_files/MERGED-CLINICAL-CSV/"
    files_dir = os.listdir(root_path)
    for device_file in files_dir:
        full_file_path = root_path + device_file
        clean_up_csv_formatting(full_file_path, root_path, device_file)


def main(argv):
    
     parser = argparse.ArgumentParser(description="Collects, organizes, and analyzes Lura Health PHSS files. Results are delivered automatically via email.")
                                      
     parser.add_argument('patient_file', type=str, help='Path to CSV file for patient ID <> device ID  relations.')
         
     parser.add_argument('email_file', type=str, help='Path to CSV file containing emails that updates should be sent to.')
     
     parser.add_argument('interval', type=float, help='Interval that analysis and email updates should be performed, in hours. One email will be sent every time an analysis event occurs.') 
    
     args = parser.parse_args()
     
     patient_ids, device_ids = parse_ID_relations_file(args.patient_file)
     
     print("active patients: ", patient_ids)
     print("active devices: ", device_ids)
     
     collect_patient_csv_files(patient_ids, device_ids)
     sort_merged_csv_files_by_date()
     

if __name__ == "__main__":
    main(sys.argv[:])
