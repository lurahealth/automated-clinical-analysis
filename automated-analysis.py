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

def collect_patient_csv_files(patient_ids, device_ids):
    path = "../lura_files/" # this is bad but easier to test across hardwares
    id_prefix = path + "ble-receiver"
    tablet_id = "clinical-tabletA"     # Make sure to check the tablet too :)
    for patient_id in patient_ids:
        # search ph receiver directory for all active pH retainers
        for device_id in device_ids:
            device_id = "LuraHealth" + device_id + ".csv"
            filename = id_prefix + patient_id + "/csv_files/"
            complete_filename = filename + device_id
            # print("complete FILENAME: ", complete_filename)
            patient_dir = os.listdir(id_prefix + patient_id + "/csv_files")
            print("Patient dir: ", patient_dir)
            print("Device id: " , device_id)
            
            if device_id in patient_dir:
                # print(complete_filename)
                print("yeaaah buddy lmao")
                # do something lol fuck


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
     

if __name__ == "__main__":
    main(sys.argv[:])
