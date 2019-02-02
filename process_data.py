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
             |
             | --> 2018-10-02-1437X.h5 (where X is RECORDING_LOCATION)
             | --> ...
             | --> 2018-10-02-HHMMX.h5 (where X is RECORDING_LOCATION)
             |
             | --> 2018-10-02-1437X_video/ (corresponding movie for each capture)
                 | --> 0000.mov
                 | --> 0001.mov
                 | --> 0002.mov
                 | --> ...
             | --> ...
             | --> 2018-10-02-HHMMX_video/ (corresponding movie for each capture)
                 | --> 0000.mov
                 | --> 0001.mov
                 | --> 0002.mov
                 | --> ...
        
    output:
    | --> 2018-10-02 PROCESSED/
        | --> 2018-10-02_vehicles.h5 (vehicle_ID, processed lidar)
        | --> 2018-10-02_vehicles.csv (vehicle_ID)
        | --> 2018-10-02_photos
            | --> 20181002143759X_0.png (FRAMES_PER_VEHICLE photos for each vehicle_ID)
            | --> 20181002143759X_1.png
            | --> 20181002143759X_2.png
            | --> 20181002143759X_3.png
            |       ...
            | --> YYYYMMDDHHmmssX_0.png
            | --> YYYYMMDDHHmmssX_1.png
            | --> YYYYMMDDHHmmssX_2.png
            | --> YYYYMMDDHHmmssX_3.png
    
    
    upload vehicle_ID to database, groundtruth interface gets photos stored locally of vehicle_ID
    
"""

import numpy as np
import h5py
from datetime import datetime
import os
import cv2

"""
from moviepy.editor import VideoFileClip
clip = VideoFileClip("my_video.mp4")
print( clip.duration )
"""

WORKING_DIR = "." # where all the data is stored, if in same folder as this script, WORKING_DIR = "."
VID_FILE_EXTENSION = ".MTS"
DETECTION_THRESHOLD = 10
IMAGE_SAVE_EXTENSION = ".jpg"
FRAMES_PER_VEHICLE = 10
VIDEO_START = "20190206133451672" # HHMMSSmmm of when the first video starts(according to lidar's clock)
# we are processing many folders of data





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


    
def process_vehicle_signature(v):
    """ given a numpy array of a vehicle image, process it """
    # TODO crop vertically
    # TODO slice timestamp off of end of each row (useless info) 
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
                if(vid_dir[:16] == hf[:16]): # if YYYY-MM-DD-HHMMX matches on filenames (first 16 chars)
                    file_pairs.append([vid_dir, hf])
            except:
                pass
                
    return file_pairs

def get_folders_to_process(root):
    """ returns folders in current dir with format 2018-10-02 UNPROCESSED/ and no corresponding 2018-10-02 PROCESSED/ """
    
    processed_folders, unprocessed_folders = search_processed_folders(root)
    
    folders = []
    for un_folder in unprocessed_folders:
        if(un_folder[:11] + un_folder[13:] not in processed_folders): # if file names share the same date
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
             | --> 2018-10-02-1437X.h5
             | --> 2018-10-02-1437X_video/ (corresponding movie for each capture)
                 | --> 0000.mov
                 | --> 0001.mov
                 | --> 0002.mov
        
    output:
    | --> 2018-10-02 PROCESSED/
        | --> 2018-10-02_vehicles.h5 (vehicle_ID, video_frames, processed lidar image tuples)
    
    """
    # for multiple collections on the same date
    file_pairs = get_file_pairs(folder) # files[data_collection_num][file_type: 0 = video_dir, 1 = hdf5_file]
    
    for file_pair in file_pairs:
        video_folder = file_pair[0]  
        hdf5_file = file_pair[1]  
        
        vid_strt = input("enter video start time for "+video_folder+" in HHMMSSmmm form:")
        process_files(hdf5_file, video_folder, vid_strt)
        
def process_files(hdf5_file_path, video_folder_path, video_start):
    """ 
        SORRY FOR THE LONG FUNCTION, didn't want to copy lots of variables to sub functions
    
        given paths to corresponding hdf5 file and video folder
        hdf5_file_path = WORKING_DIR//YYYY-MM-DD UNPROCESSED//YYYY-MM-DD-HHMMX.h5 (X is recording location)
        video_folder_path = WORKING_DIR//YYYY-MM-DD UNPROCESSED//YYYY-MM-DD-HHMM_video
        
                                       
        parse vehicles and store them in output_lidar_signature_hdf5
        
        given:
            
            input_lidar_data_hdf5
            input_lidar_data_keys      (sorted chronologically)
            input_video_file_paths     (sorted chronologically)
            output_database_csv        
            output_photo_folder_path
            output_lidar_signature_hdf5
        
        output:
            a populated hdf5_output_file with (vehicle_ID, processed lidar images)
            a populated output_database_csv with (vehicle_ID,label)
            photos of vehicles in output_photo_folder_path
    """
    
    
    """                               """
    """                               """
    """  make all input/output files  """
    """                               """
    """                               """
    
    
    head, hdf5_file_name = os.path.split(hdf5_file_path)
    YYYY_MM_DD = hdf5_file_name[:10]  #YYYY-MM-DD
    recording_location = str(hdf5_file_name[-4])

    # make output_dir_path if it doesn't exist
    output_dir_path = os.path.join(WORKING_DIR, YYYY_MM_DD + " PROCESSED")
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)

    file_name_start = os.path.join(output_dir_path, YYYY_MM_DD)
    
    # make output hdf5 file -- stores (vehicle_ID, lidar_signature) 
    # YYYY-MM-DD-HHMM_vehicles.h5
    output_lidar_signature_hdf5 = h5py.File(file_name_start + "_vehicles.h5", 'a')
    
    # open input hdf5 file -- stores compressed lidar data
    input_lidar_data_hdf5 = h5py.File(hdf5_file_path, 'r')
    input_lidar_data_keys = input_lidar_data_hdf5.keys()
    input_lidar_data_keys.sort() # ensure that keys are processed in order
    
    # make output csv file -- (stores vehcile_ID, label)
    output_database_csv = open(file_name_start + "_vehicles.csv", 'a')

    if(os.path.getsize(file_name_start + "_vehicles.csv") <= 0): # if csv file is empty, initialize it
        output_database_csv.write("vehicle_ID,label")
    
    # get list of all the video file paths in order
    input_video_file_paths = get_video_files(video_folder_path)
    input_video_file_paths.sort()
    
    # make output folder for photos
    output_photo_folder_path = file_name_start + "_photos"
    if not os.path.exists(output_photo_folder_path):
        os.makedirs(output_photo_folder_path)
    
    
    """                               """
    """                               """
    """       process all data        """
    """                               """
    """                               """

    
    gap_count = 0 # consecutive measurements between vehicle detections
    current_vehicle_signature = []

    current_video_file_paths_index = 0
    current_video_capture = cv2.VideoCapture(input_video_file_paths[current_video_file_paths_index])
    timestamp_current_video_ms = 0
    time_left_in_current_video_ms = get_video_time_ms(current_video_capture)

    # make sure about this
    prev_time_ms = to_ms(video_start) # when the first video starts in ms relative to lidar sensors internal time

    
    # loop through all keys, save timestamps in csv, save lidar signatures in hdf5
    for key in input_lidar_data_keys:
        
        # loop through all lidar_measurement in dataset with specified key
        for lidar_measurement in np.array(input_lidar_data_hdf5.get(key)):
            
            # if there is a vehicle in the current frame, save it to current_vehicle_signature
            if(vehicle_detected(lidar_measurement)):
                current_vehicle_signature.add(lidar_measurement)
                gap_count = 0
            else:
                if(len(current_vehicle_signature) == 0):
                    continue 
                elif(len(current_vehicle_signature) < DETECTION_THRESHOLD): 
                    current_vehicle_signature = []
                else:
                    gap_count += 1
                    
                    # end vehicle and save everything
                    if(gap_count >= DETECTION_THRESHOLD):
                        
                        # vehicle_ID is the timestamp of first vehicle measurement concatenated with the recording location
                        vehicle_ID = str(current_vehicle_signature[0][-1]) + recording_location
                        
                        
                        
                        
                        
                        current_time_ms = to_ms(vehicle_ID[8:17]) # only pass in HHMMSSmmm (entire vehicle_ID is YYYYMMDDHHMMSSmmmX)
                        time_to_advance_ms = current_time_ms - prev_time_ms # time to advance in videos
                        prev_time_ms = current_time_ms
                        
                        # advance through the videos to find the correct one
                        while(time_to_advance_ms > time_left_in_current_video_ms):
                            time_to_advance -= time_left_in_current_video_ms
                            current_video_capture.release()
                            current_video_file_paths_index+=1

                            try:
                                current_video_capture = cv2.VideoCapture(input_video_file_paths[current_video_file_paths_index])
                            except Exeption as e: # if error, close and save everything
                                current_video_capture.release()
                                input_lidar_data_hdf5.close()
                                output_database_csv.close()
                                output_lidar_signature_hdf5.close()
                                raise Exception("could not open video file: " + current_video_file_paths_index + " in folder " + video_folder_path)
                            
                            timestamp_current_video_ms = 0
                            time_left_in_current_video_ms = get_video_time_ms(current_video_capture)

                            


                        # go to correct time in correct video
                        current_video_capture_time = current_video_capture.get(cv2.CV_CAP_PROP_POS_MSEC)
                        assert(current_video_capture.set(cv2.CV_CAP_PROP_POS_MSEC, current_video_capture_time + time_to_advance_ms))
                        time_left_in_current_video_ms -= time_to_advance_ms
                        timestamp_current_video_ms += time_to_advance_ms
                        assert(time_left_in_current_video_ms >= 0)
                           
                        
                        # video is at correct time
                        frame = 0
                        success, image = current_video_capture.read()

                        while(frame < FRAMES_PER_VEHICLE):
                            
                            assert(success)
                            
                            image_file_path = os.path.join(output_photo_folder_path, vehicle_ID + "_" + str(frame))
                            
                            try: # save photo
                                cv2.imwrite(image_file_path  + IMAGE_SAVE_EXTENSION, image) 
                            except:
                                print("could not save " + image_file_path + IMAGE_SAVE_EXTENSION + " in folder " + output_photo_folder_path)
                            
                            frame+=1
                            
                            # if at end of one video, go to the start of the next
                            if(current_video_capture.get(cv2.CV_CAP_PROP_FRAME_COUNT) == current_video_capture.get(cv2.CV_CAP_PROP_POS_FRAMES)):
                                current_video_capture.release()
                                current_video_file_paths_index+=1
                                
                                try:
                                    current_video_capture = cv2.VideoCapture(input_video_file_paths[current_video_file_paths_index])
                                except Exeption as e: # if an error, close and save everything
                                    current_video_capture.release()
                                    input_lidar_data_hdf5.close()
                                    output_database_csv.close()
                                    output_lidar_signature_hdf5.close()
                                    raise Exception("could not open video file: " + current_video_file_paths_index + " in folder " + video_folder_path)
                            
                            timestamp_current_video_ms = 0
                            time_left_in_current_video_ms = get_video_time_ms(current_video_capture)

                            
                            success, image = vidcap.read()
                        
                        
                        # update variables
                        current_video_capture_time = current_video_capture.get(cv2.CV_CAP_PROP_POS_MSEC)
                        time_left_in_current_video_ms = get_video_time_ms(current_video_capture) - current_video_capture_time
                        
                        
                        
                        
                        try: # to process and save current_vehicle_signature
                            processed_vehicle_signature = process_vehicle_signature(np.array(current_vehicle_signature))
                            hdf5_output_file.create_dataset(vehicle_ID, data=processed_vehicle_signature)
                        except Exception as e:
                            print("dataset " + vehicle_ID + " cannot be created in file: " + hdf5_output_file.name)
                            #print(repr(e))
                            raise e
                        
                        try: # to save vehicle_ID,vehicle label (timestamp of vehicle) to output_database_csv
                            output_database_csv.write(vehicle_ID+", -1")
                        except Exception as e:
                            print("could not write '" + vehicle_ID+", -1' to csv file: " + output_database_csv.name)
                            #print(repr(e))
                            raise e
                        
                        current_vehicle_signature = []
                        gap_count = 0
    
    
    
    
    """                               """
    """                               """
    """      close all the files      """
    """                               """
    """                               """
    current_video_capture.release()
    input_lidar_data_hdf5.close()
    output_database_csv.close()
    output_lidar_signature_hdf5.close()
    

def to_ms(time):
    """ convert string 'HHMMSSmmm' to ms """
    hours = int(time[:2])
    minutes = int(time[2:4]) + hours*60
    sec = int(time[4:6]) + minutes*60
    ms = int(time[6:]) + sec*1000
    return ms
    

def get_video_time_ms(video_cap):
    """ return the length of video_cap in ms """
    pass

if __name__ == "__main__":
    main()
    
