""" 

TODO: figure out video/data synchronizing

Note: sorry for the long names, just trying to keep organized


This module:
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
        | --> 2018-10-02-1437_vehicles.h5 (vehicle_ID, processed lidar)
        | --> 2018-10-02-1437_vehicles.csv (vehicle_ID, photo_ID)
        | --> 2018-10-02-1437_photos
            | --> 00000000_0.png (x photos for each photo_ID)
            | --> 00000000_1.png
            | --> 00000000_2.png
            | --> 00000000_3.png
            |       ...
            | --> 00000001_0.png
            | --> 00000001_1.png
            | --> 00000001_2.png
            | --> 00000001_3.png
    
    
"""

import numpy as np
import h5py
from datetime import datetime
import os
from Tools.scripts.finddiv import process

WORKING_DIR = "data" # where all the data is stored, if in same folder as this script, WORKING_DIR = "."
VID_FILE_EXTENSION = ".MTS"
DETECTION_THRESHOLD = 10






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


    
def process_vehicle_image(v):
    """ given a numpy array of a vehicle image, process it """
    # TODO crop vertically
    return normalize_vehicle(v)
    
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
    
    
    """                               """
    """                               """
    """  make all input/output files  """
    """                               """
    """                               """
    
    # get list of all the video file paths in order
    input_video_file_paths = get_video_files(video_folder_path)
    input_video_file_paths.sort()
    
    
    # make output_dir_path if it doesn't exist
    head, hdf5_file_name = os.path.split(hdf5_file_path)
    output_dir_path = os.path.join(output_dir, hdf5_file_name[:10] + " PROCESSED")
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
    
    # make output hdf5 file -- stores (vechicle_ID, lidar_signature) 
    output_lidar_signature_hdf5 = h5py.File(os.path.join(output_dir_path, hdf5_file_name[:-3]+"_vehicles.h5"), 'a')
    
    # open input hdf5 file -- stores compressed lidar data
    input_lidar_data_hdf5 = h5py.File(hdf5_file_path, 'r')
    input_lidar_data_keys = input_lidar_data_hdf5.keys()
    input_lidar_data_keys.sort() # ensure that keys are processed in order
    
    # make output csv file -- (stores vehcile_ID, photo_ID)
    output_photo_IDs_csv = open(os.path.join(output_dir_path,hdf5_file_name[:-3]+"_vehicles.csv"), 'a')
    output_photo_IDs_csv.write("vehicle_ID,photo_ID")
    
    # make output folder for photos
    output_photo_folder_path = os.path.join(output_dir_path,hdf5_file_name[:-3]+"photos")
    if not os.path.exists(output_photo_folder_path):
        os.makedirs(output_photo_folder_path)
    
    
    """
        variables:
            output_lidar_signature_hdf5
            input_lidar_data_hdf5
            input_lidar_data_keys        (sorted chronologically)
            input_video_file_paths (sorted chronologically)
    """
    # process all the vehicles
    """
        parse vehicles and store them in output_lidar_signature_hdf5
        
        given:
            
            input_lidar_data_hdf5
            input_lidar_data_keys      (sorted chronologically)
            input_video_file_paths     (sorted chronologically)
            output_photo_IDs_csv        
            output_photo_folder_path
            output_lidar_signature_hdf5
        
        output:
            a populated hdf5_output_file with (vehicle_ID, processed lidar images)
            a populated output_photo_IDs_csv with (vehicle_ID, photo_ID)
            photos of vehicles in output_photo_folder_path
    """

    
    gap_count = 0 # consecutive measurements between vehicle detections
    current_vehicle = []
    
    
    # loop through all keys
    for key in input_lidar_data_keys:
        
        # loop through all lidar_measurement in dataset with specified key
        for lidar_measurement in np.array(input_lidar_data_hdf5.get(key)):
            
            # if there is a vehicle in the current frame, save it to current_vehicle
            if(vehicle_detected(lidar_measurement)):
                current_vehicle.add(lidar_measurement)
                gap_count = 0
            else:
                if(len(current_vehicle) == 0):
                    continue 
                elif(len(current_vehicle) < DETECTION_THRESHOLD): 
                    current_vehicle = []
                else:
                    gap_count += 1
                    
                    if(gap_count >= DETECTION_THRESHOLD):
                        save_pictures() # TODO and generate vehicle_ID, photo_ID
                        save(vehicle_ID, np.array(current_vehicle), photo_ID, hdf5_output_file, output_photo_IDs_csv)
                        current_vehicle = []
                        gap_count = 0
    
    
    
    
    # close all the files
    output_lidar_signature_hdf5.close()
    output_photo_IDs_csv.close()
    output_lidar_signature_hdf5.close()
    
        

def save(vehicle_ID, vehicle_image, photo_ID, hdf5_output_file, output_photo_IDs_csv):
    """ save vehicle_ID (str), photo_ID (str), vehicle_lidar_image (np array) in specified files"""        
    
    try: # to process and save vehicle image
        processed_vehicle_image = process_vehicle_image(vehicle_image)
        hdf5_output_file.create_dataset(vehicle_ID, data=processed_vehicle_image)
    except Exception as e:
        print("dataset " + vehicle_ID + " cannot be created in file: " + hdf5_output_file.name)
        #print(repr(e))
        raise e
    
    try: # to save photo_ID
        output_photo_IDs_csv.write(vehicle_ID + "," + photo_ID)
    except Exception as e:
        print("could not write " + vehicle_ID + " to csv file: " + output_photo_IDs_csv.name)
        #print(repr(e))
        raise e

if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    