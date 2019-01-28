""" This module:
        (1) takes in compressed raw lidar in hdf5 files
        (2) identifies vehicles and normalizes data
        (4) stores processed vehicle data as m x n images in hfd5 file
        
    This module works for both 1D and 2D (scanning) lidar data
    
    
    2D lidar
    
    time is vertical starting with earliest time
    data[time][position]
    
    | --> data/
        | --> 2018-10-02 UNPROCESSED/
             | --> 2018-10-02-1437.h5
             | --> 2018-10-02-1437_video/ (corresponding movie for each capture)
                 | --> 0000.mov
                 | --> 0001.mov
                 | --> 0002.mov
        
    output:
    | --> 2018-10-02 PROCESSED/
        | --> 2018-10-02-1437_vehicles.h5 (vehicle_ID, video_frames, processed lidar image tuples)
    
    
"""

import numpy as np
import h5py
from datetime import datetime
import os
from Tools.scripts.finddiv import process

INPUT_DIR = "data" # where all the data is stored, if in same folder as this script, INPUT_DIR = "."


def normalize_vehicle(v):
    """ takes in numpy array of vehicle data, processes it, returns numpy array of vehicle data """
    pass


def vehicle_detected(a):
    """ a is a numpy array of arbitrary length. method returns true if there is a vehicle """
    pass


def find_vehicle(input_file, keys, start_time):
    """
        given: input_file, keys (sorted chronologically), start_time
        return are_more_vehicles, end_time, vehicle (numpy array), vehicle_ID (unique)
    """
    lidar_data = np.array(hdf5_file.get(k)) # array
    
    count = 0 # consecutive measurements with a vehicle detected
    current_vehicle =[]
    recording_vehicle = False
    
    # find vehicles
    for time in range(len(lidar_data)):
       
        # data[time][position], measurement is a data capture at a specific time
        # go through measurements identifying vehicles; if vehicle is found, process and add to list
        
        measurement = lidar_data[time]
        
        vehicle_present = vehicle_detected(measurement)
        
        # if there isn't a vehicle in the current frame and we are not recording a current vehicle, continue
        if(not vehicle_present and not recording_vehicle): 
            continue
        
        elif(vehicle_present and not recording_vehicle):
            count+=1
            
            if(count > DETECTION_THRESHOLD):
                
                count = 0
                
                for i in range(DETECTION_THRESHOLD): # add previous points to vehicle
                    current_vehicle.append(data[time - DETECTION_THRESHOLD + i])#
                
                recording_vehicle = True            
            
        
        elif(not vehicle_present and recording_vehicle):
            count+=1
            
            if(count > DETECTION_THRESHOLD):
                
                count = 0
                
                current_vehicle = current_vehicle[:len(current_vehicle)-DETECTION_THRESHOLD]
                
                # stop recording vehicle
                
                recording_vehicle = False    
                
                processed_vehicles.append(normalize_vehicle(current_vehicle))
                current_vehicle = []
            
            
            
        if(recording_vehicle): # add data point to current vehicle
            
            current_vehicle.append(measurement)
        
    
def process_vehicle(v):
    normalize_vehicle(v)
    
def is_hdf5_file(file):
    name = file.split(".")
    return name[1] == "h5"
    
def get_files(root):
    
    """ return [[video_dir, h5 file], [video_dir, h5 file], ... ] """ # TODO
    file_pairs = []
    
    for file in os.listdir(root):
        if(is_hdf5_file(file)):
           hdf5_files.append(os.path.join(root, file))  
        elif(os.isdir(file) and file[-6:] == "_video"):
            videos.append(os.path.join(root, file))

    return file_pairs

def main():
    
    folders_to_process = get_folders_to_process(INPUT_DIR) # get folders to process
    
    for folder in folders_to_process:
        process_folder(os.path.join(INPUT_DIR, folder))
    
def get_folders_to_process(root):
    """ returns folders in current dir with format 2018-10-02 UNPROCESSED/ and no corresponding 2018-10-02 PROCESSED/ """
    
    processed_folders, unprocessed_folders = search_processed_folders(root)
    
    folders = []
    for un_folder in unprocessed_folders:
        if(un_folder[:11] + un_folder[13:] not in processed_folders):
            folders.append(un_folder)
            
    return folders

def search_processed_folders(root):
    
    processed_folders = []
    unprocessed_folders = []
    
    for file in os.listdir(root):
        try:
            if(os.path.isdir(os.path.join(root, file)) and file[-9:] == "PROCESSED"):
                if(file[-10] == ' '):
                    processed_folders.append(file)
                elif(file[-12:-9] == " UN"):
                    unprocessed_folders.append(file)
        except:
            pass
            
    return processed_folders, unprocessed_folders

def process_folder(folder):
    """ given folder =  INPUT_DIR//YYYY-MM-DD UNPROCESSED//
    
    | --> 2018-10-02 UNPROCESSED/
             | --> 2018-10-02-1437.h5
             | --> 2018-10-02-1437_videos/ (corresponding movie for each capture)
                 | --> 0000.mov
                 | --> 0001.mov
                 | --> 0002.mov
        
    output:
    | --> 2018-10-02 PROCESSED/
        | --> 2018-10-02-1437_vehicles.h5 (vehicle_ID, video_frames, processed lidar image tuples)
    
    """
    # for multiple collections on the same date
    file_array = get_files(folder) # files[data_collection_num][file_type: 0 = video_dir, 1 = hdf5_file]
    
    for file_set in file_array:
        video_folder = file_set[0]  
        hdf5_file = file_set[1]  
        
        process_files(hdf5_file, video_folder)
        
        
def process_files(hdf5_file, video_folder):

    input_file = h5py.File("compressed_data.h5", 'r')
    keys = input_file.keys()
    keys.sort() # ensure that data is processed in order
    
    output_file = h5py.File(os.path.join(OUTPUT_DIR, "vehicles.h5"), 'a')
    
    are_more_vehicles = True
    
    start = 0
    
    while(are_more_vehicles):
        are_more_vehicles, start, vehicle, vehicle_ID = find_vehicle(input_file, keys, start)
        
        # normalize vehicle
        vehicle_image = process_vehicle(vehicle)
        
        try:
            output_file.create_dataset(vehicle_ID, data=vehicle_image)
        except:
            print("dataset " + str(vehicle_ID)+" has already been created.")

    
    output_file.close()
    #os.remove(file) see if there is a way to remove used dataset
        
if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    