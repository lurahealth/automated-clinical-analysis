#!/usr/bin/env python 
import argparse
import sys
import csv
import os

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
