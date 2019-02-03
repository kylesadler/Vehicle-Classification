""" 

TODO: figure out video/data synchronizing

Note: sorry for the long names, just trying to keep organized


This module:
        (1) takes in compressed raw lidar in hdf5 files
        (2) identifies vehicles and normalizes data
        (4) stores processed vehicle data as m x n images in hfd5 file
        
    This module works for both 1D and 2D (scanning) lidar data
    
    
    steps: 
    set lidar to output data into a folder called raw_data (this can be changed)
    run compress_data.py with the correct recording location
    move created folder onto main machine in a working directory
    for each params.txt file, enter the associated parameters
    put the associated video files in respective video folders
    put process_data.py in the working directory
    run process_data.py
    upload csv output file to database
    
    
    2D lidar
    
    time is vertical starting with earliest time
    data[time][position]
    
    | --> data/
        | --> 2018-10-02 UNPROCESSED/
             | --> 2018-10-02-1437X_params.txt
             | --> ...
             | --> YYYY-MM-DD-HHMMX_params.txt
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
from moviepy.editor import VideoFileClip


WORKING_DIR = "."               # where all the data is stored, if in same folder as this script, WORKING_DIR = "."
VID_FILE_EXTENSION = ".MTS"
DETECTION_THRESHOLD = 10        # number of consecutive frames before recognizing vehicle
IMAGE_SAVE_EXTENSION = ".jpg"
FRAMES_PER_VEHICLE = 10         # number of frames to save per vehicle
SECONDS_PER_FRAME = .25         # number of seconds between frames

""" TODO make parameters.txt file for each folder's video start time, min distance, and max distance """

def main():
    
    folders_to_process = get_folders_to_process(WORKING_DIR) # get folders to process
    
    for folder in folders_to_process:
        print("processing folder " + folder)
        process_folder(os.path.join(WORKING_DIR, folder))

def process_folder(folder):
    """ given folder =  WORKING_DIR//YYYY-MM-DD UNPROCESSED//
    
    | --> 2018-10-02 UNPROCESSED/
             | --> 2018-10-02-1437X_params.txt
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
    file_tuples = get_related_files(folder) # files[data_collection_num][file_type: 0 = video_dir, 1 = hdf5_file]
    if(len(file_tuples) == 0):
        print("nothing to process in folder "+folder)
        return
    
    for file_tuple in file_tuples:
        video_folder = file_tuple[0]  
        hdf5_file = file_tuple[1]  
        param_file = file_tuple[2]  
        print("processing files "+hdf5_file+", "+video_folder+", "+param_file)
        process_files(hdf5_file, video_folder, param_file)

def process_files(hdf5_file_path, video_folder_path, params_txt_path):
    """ 
        given:
        
            hdf5_file_path = WORKING_DIR//YYYY-MM-DD UNPROCESSED//YYYY-MM-DD-HHMMX.h5 (X is recording location)
            video_folder_path = WORKING_DIR//YYYY-MM-DD UNPROCESSED//YYYY-MM-DD-HHMMX_video
            video_start is the time that the video starts using the lidars internal time (should be the correct time)
                                       
        
        run process_data with:
            
            input_lidar_data_hdf5
            input_lidar_data_keys      (sorted chronologically)
            input_video_file_paths     (sorted chronologically)
            output_database_csv        
            output_photo_folder_path
            output_lidar_signature_hdf5
        
    """
    
    
    """                               """
    """                               """
    """  make all input/output files  """
    """                               """
    """                               """
    
    
    head, hdf5_file_name = os.path.split(hdf5_file_path)
    YYYY_MM_DD = hdf5_file_name[:10]  #YYYY-MM-DD
    recording_location = hdf5_file_name[-4]

    # make output_dir_path if it doesn't exist
    output_dir_path = os.path.join(WORKING_DIR, YYYY_MM_DD + " PROCESSED")
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)

    file_name_start = os.path.join(output_dir_path, YYYY_MM_DD) # WORKING_DIR//YYYY-MM-DD PROCESSED//YYYY-MM-DD
    
    # make output hdf5 file -- stores (vehicle_ID, lidar_signature) 
    # YYYY-MM-DD-HHMM_vehicles.h5
    output_lidar_signature_hdf5 = h5py.File(file_name_start + "_vehicles.h5", 'a')
    
    # open input hdf5 file -- stores compressed lidar data
    input_lidar_data_hdf5 = h5py.File(hdf5_file_path, 'r')
    input_lidar_data_keys = input_lidar_data_hdf5.keys()
    input_lidar_data_keys.sort() # ensure that keys are processed in order
    
    # make output csv file -- (stores vehcile_ID, label)
    # if csv file is empty, initialize it
    output_database_csv = open(file_name_start + "_vehicles.csv", 'a')
    if(os.path.getsize(file_name_start + "_vehicles.csv") <= 0):
        output_database_csv.write("vehicle_ID,label")
    
    # get list of all the video file paths in order
    input_video_file_paths = get_video_files(video_folder_path)
    input_video_file_paths.sort()
    
    # make output folder for photos
    output_photo_folder_path = file_name_start + "_photos"
    if not os.path.exists(output_photo_folder_path):
        os.makedirs(output_photo_folder_path)
    
    # open params.txt file
    params_file = open(params_txt_path, 'r')
    
    """                               """
    """                               """
    """       process all data        """
    """                               """
    """                               """
    
    process_data(input_lidar_data_hdf5, input_lidar_data_keys, input_video_file_paths, recording_location, params_file, output_database_csv, output_photo_folder_path, output_lidar_signature_hdf5)
    
    
    """                               """
    """                               """
    """      close all the files      """
    """                               """
    """                               """
    input_lidar_data_hdf5.close()
    output_database_csv.close()
    output_lidar_signature_hdf5.close()

def process_data(input_lidar_data_hdf5, input_lidar_data_keys, input_video_file_paths, recording_location, params_file, output_database_csv, output_photo_folder_path, output_lidar_signature_hdf5):
    """
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
    
    video_start = params_file.readline().split(":")[1].strip()
    MAX_DISTANCE_mm = params_file.readline().split(":")[1].strip()
    MIN_DISTANCE_mm = params_file.readline().split(":")[1].strip()

    
    
    gap_count = 0                         # consecutive measurements between vehicle detections
    current_vehicle_signature = []
    
    # video_start is string 'HHMMSSmmm' when the video starts according to the lidar
    vid_parse = video_parser(input_video_file_paths, output_photo_folder_path, video_start)

    
    # loop through all keys, save timestamps in csv, save lidar signatures in hdf5
    for key in input_lidar_data_keys:
        
        # loop through all lidar_measurement in dataset with specified key
        for lidar_measurement in np.array(input_lidar_data_hdf5.get(key)):
            
            # if there is a vehicle in the current frame, save it to current_vehicle_signature
            if(vehicle_detected(lidar_measurement, MIN_DISTANCE_mm, MAX_DISTANCE_mm)):
                current_vehicle_signature.add(lidar_measurement)
                gap_count = 0
            else:
                if(len(current_vehicle_signature) == 0):
                    continue 
                elif(len(current_vehicle_signature) < DETECTION_THRESHOLD): 
                    current_vehicle_signature = []
                else:
                    gap_count += 1
                    
                    if(gap_count >= DETECTION_THRESHOLD): # end vehicle and save everything
                        
                        # vehicle_ID is the timestamp of first vehicle measurement concatenated with the recording location
                        vehicle_ID = str(current_vehicle_signature[0][-1]) + recording_location
                        try:
                            vid_parse.save_vehicle_images(vehicle_ID)
                            processed_vehicle_signature = process_vehicle_signature(np.array(current_vehicle_signature))
                            save_to_hdf5(hdf5_output_file, vehicle_ID, processed_vehicle_signature)
                            save_to_csv(output_database_csv, vehicle_ID+", -1")
                        
                        except:
                            input_lidar_data_hdf5.close()
                            output_database_csv.close()
                            output_lidar_signature_hdf5.close()
                            raise Exception("could not save vehicle: " + vehicle_ID)
    
                        
                        current_vehicle_signature = []
                        gap_count = 0
 
 

def normalize_vehicle(v):
    """ take in numpy array of vehicle data, normalize it, return numpy array of vehicle data """
    return (v - np.min(v))/np.ptp(v)


def vehicle_detected(a, MIN_DISTANCE_mm, MAX_DISTANCE_mm):
    """ a is a 1 x N numpy array. method returns true if there is a vehicle 
        expected_points is a 1 x N vector of the expected distance for each point
    """
    # return true if more 30% of the points are within MIN_DISTANCE_mm and MAX_DISTANCE_mm
    return ((a > MIN_DISTANCE_mm) and (a < MAX_DISTANCE_mm)).sum() > a.size()*.3


    
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

def get_files(folder):
    hdf5_files = []
    vid_dirs = []
    param_files = []
    
    for file in os.listdir(folder):
        try:
            file_path = os.path.join(folder, file)
            if(os.path.isdir(file_path) and file[-6:] == "_video"): # is a video dir
                print(file)
                vid_dirs.append(file_path)
            elif(is_hdf5_file(file)):
                hdf5_files.append(file_path)
            elif(file[-11:] == "_params.txt"): # file is param file
                param_files.append(file_path)
        except:
            raise

    return vid_dirs, hdf5_files, param_files
    
def get_related_files(root):
    
    """ return [[video_dir, h5 file, param file], [video_dir, h5 file, param file], ... ] """
    vid_dirs, hdf5_files, param_files = get_files(root)
    file_tuples = []
    
    for vid_dir in vid_dirs:
        for hf in hdf5_files:
            for pf in param_files:
                try:
                    #print(vid_dir[:41]+', '+hf[:41]+', '+pf[:41])
                    if(vid_dir[:41] == hf[:41] and pf[:41] == hf[:41]): # if YYYY-MM-DD-HHMMX matches on filenames (first 16 chars)
                        file_tuples.append([vid_dir, hf, pf])
                except:
                    pass
                
    return file_tuples

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
      
def save_to_hdf5(file, dset_name, dset_data):
    try: # to save the dataset
        file.create_dataset(dset_name, data=dset_data)
    except Exception as e:
        print("dataset " + dset_name + " cannot be created in file: " + file.name)
        #print(repr(e))
        raise e
    
def save_to_csv(file, string):
    try: # to save vehicle_ID,vehicle label (timestamp of vehicle) to output_database_csv
        file.write(string)
    except Exception as e:
        print("could not write '" +string +"' to csv file: " + file.name)
        #print(repr(e))
        raise e

if __name__ == "__main__":
    main()
    
    
# keeps track of video traversal
class video_parser:
    """ all times are in seconds """
    def __init__(self, in_paths, out_path, video_start_time):
        self.input_video_file_paths = in_paths
        self.output_photo_folder_path = out_path
        self.video_timestamp = 0 # stores the timestamp in 
        self.video_index = 0
        self.video = VideoFileClip(self.input_video_file_paths[0])    # current video
        self.absolute_time = self.to_absolute_sec(video_start_time) # stores the absolute time
    
    def save_vehicle_images(vehicle_ID):
        """ save vehicle frames """
        
        # set self.video_timestamp to the specified time
        self.advance_video_to(self.to_absolute_sec(vehicle_ID[8:17])) # to_absolute_sec('HHMMSSmmm') (entire vehicle_ID is YYYYMMDDHHMMSSmmmX)
    
        for frame in range(FAMES_PER_VEHICLE):
    
            # save frame and update times
            image_file_path = os.path.join(self.output_photo_folder_path, vehicle_ID + "_" + str(frame) + IMAGE_SAVE_EXTENSION)
            self.video.save_frame(image_file_path, t=self.video_timestamp)
    
            # advance video by SECONDS_PER_FRAME seconds
            self.advance_video_to(self.absolute_time + SECONDS_PER_FRAME)
        
    def advance_video_to(self, new_time): # throws an exception
        """ advance video to specified absolute timestamp
            update:
                self.absolute_time
                self.video_timestamp
                self.video
                self.video_index
                """
        # find vehicle in videos
        time_to_advance = new_time - self.absolute_time
        self.absolute_time = new_time
        
        # while the time_to_advance is greater than the time left in current video
        while(time_to_advance > current_video.duration - self.video_timestamp):
            time_to_advance -= current_video.duration - self.video_timestamp
            assert(time_to_advance > 0)
            self.video_index += 1
            self.video = VideoFileClip(self.input_video_file_paths[self.video_index])
            self.video_timestamp = 0
        
        self.video_timestamp += time_to_advance
    
    def to_absolute_sec(self, time):
        """ convert string 'HHMMSSmmm' to sec """
        hours = int(time[:2])
        minutes = int(time[2:4]) + hours*60
        sec = int(time[4:6]) + minutes*60
        return int(time[6:])/1000 + sec
    
    
    