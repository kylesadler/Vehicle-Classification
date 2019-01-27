""" This module:
        (1) takes in compressed raw lidar in hdf5 files
        (2) identifies vehicles and normalizes data
        (4) stores processed vehicle data as m x n images in hfd5 file
        
    This module works for both 1D and 2D (scanning) lidar data
    
    
    2D lidar
    
    time is vertical starting with earliest time
    data[time][position]
"""

import numpy as np
import h5py
from datetime import datetime

INPUT_DIR = "compressed_data"
OUTPUT_DIR = "processed_data"



def normalize_vehicle():
    """ takes in numpy array of vehicle data, processes it, returns numpy array of vehicle data """
    pass


def vehicle_detected(a):
    """ a is a numpy array of arbitrary length. method returns true if there is a vehicle """
    pass


def process_data(data):
    """
    def process_single_beam_data(data):
        "" takes in 1D numpy array data and extracts vehicles, normalizes, ect. returns processed data ""
        pass

    
    def process_scanning_data(data):
        "" takes in 2D numpy array data and extracts vehicles, normalizes, ect. returns processed data ""
        pass
    """
    
    
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
        
    
        
                    
    
    
def process_file(file):
    
    hdf5_file = h5py.File(file, 'r')
    keys = hdf5_file.keys()
    keys.sort() # ensure that data is processed in order
    
    for k in keys:
        
        lidar_data = np.array(hdf5_file.get(k)) # array
        process_data(lidar_data)
        
    
def main():
    """data_to_process = h5py.File('data.h5', 'r') # array
    
    #if(SINGLE_BEAM_LIDAR):
        processed_data = process_single_beam_data(data_to_process)
    else:
        processed_data = process_scanning_data(data_to_process)
    #
    
    processed_vehicles = processed_vehicles(data_to_process)

    store_as_hdf5(processed_vehicles)"""
    
    files_to_process = get_files_to_process()
    
    # collection of detected vehicles, each image stored under vehicle ID
    vehicles = h5py.File(os.path.join(OUTPUT_DIR, "vehicles_"+str(datetime.now()).replace("-","").replace(":","").replace(" ","").replace(".","")+".h5"), 'w')
    
    
    for file in files_to_process: # these are hdf5 files from different days. do not go together
        process_file(file)
     
        # normalize vehicles
        vehicle_image = normalize()
        
        
        vehicles.create_dataset(vehicle_ID, data=vehicle_image)
                              
    vehicles.close()
    
def is_hdf5_file(file):
    name = file.split(".")
    return name[1] == "h5"
    
def get_files_to_process():
    output = []
    
    for file in os.listdir(INPUT_DIR):
       if(id_hdf5_file(file)):
           output.append(file)  
    
    return output
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    