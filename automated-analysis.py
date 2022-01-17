#!/usr/bin/env python 
import argparse
import sys
import csv
import os
import time
import pandas as pd
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
    merged_filepath = "/home/ubuntu/lura_files/MERGED-CLINICAL-CSV/device_"
    merged_file = merged_filepath + device_id + ".csv"
    with open(file_path_to_merge, mode='r') as new_file:
        new_csv_data = new_file.read()
    
    with open(merged_file, mode='a') as big_file:
        big_file.write(new_csv_data)
        
# Search directory and subdirectories for pH receiver data,
# the device ID files could be in any patient ID subdirectory
def collect_patient_csv_files(patient_ids, device_ids):
    path = "/home/ubuntu/lura_files/"   # this is bad but easier to test across hardwares
    id_prefix = path + "ble-receiver"
    tablet_id = "clinical-tabletA"      # Make sure to check the tablet too :)
    patient_ids = list(set(patient_ids)) # Remove possible patient ID duplicates
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
#                if line.count(':') != 2:
#                    print("** CHECK DEVICE: " + device_file)
                if current_header not in line and line != '\n' and line.count(':') == 2:
                #if current_header not in line and line != '\n':
                    if line.count('\n') != 1:
                        funky_lines = line.split(',')
                        for funky_line in funky_lines:
                            temp_file.write(funky_line + "\n")
                    else:
                        temp_file.write(line)
    # use pandas to sort by timestamp, delete CSVs, then write final CSV
    df = pd.read_csv(temp_filename)
    df.sort_values(["Time"], inplace=True, ascending=False)
    os.remove(full_file_path)
    os.remove(temp_filename)
    df.to_csv(full_file_path, index=False)
                    
# Cleans up file formatting, empty lines, etc then sorts data by timestamp
# Data is sorted in descending order, i.e. most recent data is at the top
def sort_merged_csv_files_by_date():
    root_path = "/home/ubuntu/lura_files/MERGED-CLINICAL-CSV/"
    files_dir = os.listdir(root_path)
    for device_file in files_dir:
        full_file_path = root_path + device_file
        clean_up_csv_formatting(full_file_path, root_path, device_file)

# delete em all haha        
def reset_files():
    root_path = "/home/ubuntu/lura_files/MERGED-CLINICAL-CSV/"
    for file_name in os.listdir(root_path):
        os.remove(os.path.join(root_path, file_name))
        
def return_average(lines, col):
    average = 0
    running_avg_pts = 13
    num_lines = len(lines)
    if num_lines < 13:
        running_avg_pts = num_lines - 1
    for i in range(1, running_avg_pts):
        average = average + float(lines[i].split(',')[col])
    average = average / (running_avg_pts - 1) 
    return round(average,2)

def check_threshold(lines, low_thresh, high_thresh, col):
        if float(lines[1].split(',')[col]) > low_thresh and float(lines[1].split(',')[col]) < high_thresh:
            return "good"
        else:
            return "NEEDS REVIEW"

# Return "good" or "NEEDS REVIEW" , and last 1hr average (12 rows of data)
def analyze_ph_data(lines):
    pH_col = 1
    pH_high_thresh = 10
    pH_low_thresh = 3
    good_or_bad = check_threshold(lines, pH_low_thresh, pH_high_thresh, pH_col)
    hour_avg = return_average(lines, pH_col)
    return good_or_bad, hour_avg

# Return "good" or "NEEDS REVIEW", and last battery mV value 
def analyze_battery_data(lines):
    batt_col = 3
    batt_high_thresh = 3000
    batt_low_thresh = 2100
    good_or_bad = check_threshold(lines, batt_low_thresh, batt_high_thresh, batt_col)
    hour_avg = return_average(lines, batt_col)
    return good_or_bad, hour_avg

# Return "good" or "NEEDS REVIEW", and last 1hr average (12 rows of data)
def analyze_temp_data(lines):
    temp_col = 2
    temp_high_thresh = 40
    temp_low_thresh = 12
    good_or_bad = check_threshold(lines, temp_low_thresh, temp_high_thresh, temp_col)
    hour_avg = return_average(lines, temp_col)
    return good_or_bad, hour_avg

# Performs analysis of battery level, connection time, pH readings, and temperature
# Indicates if device is "good" or needs further analysis
# Writes results to a summary .txt file, with the most recent 30mins of data (6 rows)
def run_simple_analysis(patient_ids, device_ids):
    root_path     = "/home/ubuntu/lura_files/MERGED-CLINICAL-CSV/"
    summary_fname = "ANALYSIS_SUMMARY.txt"
    # Create the summary file and add in a title/whatever to begin
    with open(root_path + summary_fname, mode='a') as summary_file:
        summary_file.write("Lura Health First-In-Man Clinical Live Data Summary\n")
        summary_file.write("*************************************************************\n\n")
        for device_csv in os.listdir(root_path): 
                curr_device_id = device_csv.split('.')[0]
                curr_device_id = curr_device_id.split('_')[1]
                if curr_device_id != "SUMMARY":
                    summary_file.write("Patient " + patient_ids[device_ids.index(curr_device_id)] + " ")
                    summary_file.write("Device " + curr_device_id + " - - - - - - - -\n")
                    # Write summary of analysis things first
                    with open(root_path + device_csv, mode='r') as csv_file:
                        lines = csv_file.readlines()
                        summary_file.write("    Last connection:   " + lines[1].split(',')[0] + "\n")
                        summary_file.write("    Battery level:     " + analyze_battery_data(lines)[0])
                        summary_file.write(" (last 1 hr. avg: "      + str(analyze_battery_data(lines)[1]) + ")\n")
                        summary_file.write("    pH Sensor Data:    " + analyze_ph_data(lines)[0])
                        summary_file.write(" (last 1 hr. avg: "      + str(analyze_ph_data(lines)[1]) + ")\n")
                        summary_file.write("    Temperature Data:  " + analyze_temp_data(lines)[0])
                        summary_file.write(" (last 1 hr. avg: "      + str(analyze_temp_data(lines)[1]) + ")\n\n")
        # Page break of sorts, and then just print most recent 30 mins of data (6 rows)
        summary_file.write("************************************************************\n\n")
        summary_file.write("                     Time,            pH,temp,batt,pHmV\n")       
        for device_csv in os.listdir(root_path): 
                curr_device_id = device_csv.split('.')[0]
                curr_device_id = curr_device_id.split('_')[1]
                if curr_device_id != "SUMMARY":
                    summary_file.write("(Device " + curr_device_id + ") - - - - - - - - - - - - - - - - - - - - - - - -\n")
                    with open(root_path + device_csv, mode='r') as csv_file:
                        lines = csv_file.readlines()
                        lines_to_print = 5
                        if len(lines) < 5:
                            lines_to_print = len(lines)
                        for i in range(1,lines_to_print):
                            summary_file.write("                  " + lines[i])
                        summary_file.write("\n")    
                        
            
def main(argv):
    
     parser = argparse.ArgumentParser(description="Collects, organizes, and analyzes Lura Health PHSS files. Results are stored in a summary file.")
                                      
     parser.add_argument('patient_file', type=str, help='Path to CSV file for patient ID <> device ID  relations.')
    
     args = parser.parse_args()
     
     patient_ids, device_ids = parse_ID_relations_file(args.patient_file)
     
     print("active patients: ", patient_ids)
     print("active devices: ", device_ids)
     
     reset_files() # delete old summaries and update with brand new fresh files
     collect_patient_csv_files(patient_ids, device_ids)
     sort_merged_csv_files_by_date()
     run_simple_analysis(patient_ids, device_ids)

if __name__ == "__main__":
    main(sys.argv[:])
