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

WORKING_DIR = "data" # where all the data is stored, if in same folder as this script, WORKING_DIR = "."
VID_FILE_EXTENSION = ".MTS"







def main():
    
    folders_to_process = get_folders_to_process(WORKING_DIR) # get folders to process
    
    for folder in folders_to_process:
        process_folder(os.path.join(WORKING_DIR, folder))
    
def normalize_vehicle(v):
    """ takes in numpy array of vehicle data, processes it, returns numpy array of vehicle data """
    pass


def vehicle_detected(a):
    """ a is a numpy array of arbitrary length. method returns true if there is a vehicle """
    pass


def find_vehicle(hdf5_input_file, keys, video_files, start_time):
    """
        given: input_file, keys (sorted chronologically), start_time
        return are_more_vehicles, end_time, vehicle_ID (unique), vehicle_image (numpy array), video_frames
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
    """ given a numpy array of a vehicle image, process it """
    normalize_vehicle(v)
    
def is_hdf5_file(file):
    return file[-3:] == ".h5"

def get_video_files(folder):
    videos = []
    for file in os.listdir(folder):
        if(file[-len(VID_FILE_EXTENSION):] ==  VID_FILE_EXTENSION):
            videos.append(os.path.join(folder, file))
    
    return videos

def get_hdf5_and_vid_dir(folder):
    hdf5_files = []
    vid_dirs = []
    
    for file in os.listdir(folder):
        try:
            if(os.isdir(file) and file[-6:] == "_video"): # is a video dir
                vid_dirs.append(os.path.join(folder, file))
            elif(is_hdf5_file(file)):
                hdf5_files.append(os.path.join(folder, file))
        except:
            pass

    return vid_dirs, hdf5_files
    
def get_file_pairs(root):
    
    """ return [[video_dir, h5 file], [video_dir, h5 file], ... ] """
    vid_dirs, hdf5_files = get_hdf5_and_vid_dir(root)
    
    for vid_dir in vid_dirs:
        for hf in hdf5_files:
            try:
                if(vid_dir[:15] == hf[:15]):
                    file_pairs.append([vid_dir, hf])
            except:
                pass
                
    return file_pairs

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
    """ given folder =  WORKING_DIR//YYYY-MM-DD UNPROCESSED//
    
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
    # for multiple collections on the same date
    file_pairs = get_file_pairs(folder) # files[data_collection_num][file_type: 0 = video_dir, 1 = hdf5_file]
    
    for file_pair in file_pairs:
        video_folder = file_pair[0]  
        hdf5_file = file_pair[1]  
        
        process_files(hdf5_file, video_folder, WORKING_DIR)
        
def process_files(hdf5_file_path, video_folder_path, output_dir):
    """ given paths to corresponding hdf5 file and video folder
        hdf5_file_path = WORKING_DIR//YYYY-MM-DD UNPROCESSED//YYYY-MM-DD-HHMM.h5
        video_folder_path = WORKING_DIR//YYYY-MM-DD UNPROCESSED//YYYY-MM-DD-HHMM_video
    
         | --> 2018-10-02-1437.h5
         | --> 2018-10-02-1437_video/ (corresponding movie for each capture)
             | --> 0000.mov
             | --> 0001.mov
             | --> 0002.mov
        
    output:
    | --> 2018-10-02 PROCESSED/
        | --> 2018-10-02-1437_vehicles.h5 (vehicle_ID, video_frames, processed lidar image tuples)
    """
    
    video_files = get_video_files(video_folder_path)
    video_files.sort()
    head, hdf5_file_name = os.path.split(hdf5_file_path)
    output_dir_path = os.path.join(output_dir, hdf5_file_name[:10] + " PROCESSED")
    
    if not os.path.exists(output_dir_path): # make output_dir_path if it doesn't exist
        os.makedirs(output_dir_path)
    
    hdf5_output_file = h5py.File(os.path.join(output_dir_path, hdf5_file_name[:-3]+"_vehicles.h5"), 'a')
    hdf5_input_file = h5py.File(hdf5_file_path, 'r')
    keys = hdf5_input_file.keys()
    keys.sort() # ensure that data is processed in order
    
    
    """
        variables:
            hdf5_output_file
            hdf5_input_file
            keys        (sorted chronologically)
            video_files (sorted chronologically)
    """
    parse_vehicles(hdf5_input_file, keys, video_files, hdf5_output_file)
    
    hdf5_output_file.close()
        
def parse_vehicles(hdf5_input_file, keys, video_files, hdf5_output_file): # TODO
    """
        parse vehicles and store them in hdf5_output_file
        
        given:
            hdf5_output_file
            hdf5_input_file
            keys        (sorted chronologically)
            video_files (sorted chronologically)
        
        output:
            hdf5_output_file(vehicle_ID, video_frames, processed lidar image tuples)
    """
    are_more_vehicles = True
    
    start = 0
    
    while(are_more_vehicles):
        are_more_vehicles, start, vehicle_ID, vehicle, video_frames = find_vehicle(hdf5_input_file, keys, video_files, start)
        
        # normalize vehicle
        vehicle_image = process_vehicle(vehicle)
        
        try:
            hdf5_output_file.create_dataset(str(vehicle_ID), data=vehicle_image)
        except:
            print("dataset " + str(vehicle_ID)+" has already been created.")
            raise


if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    