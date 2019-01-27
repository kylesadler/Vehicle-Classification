""" This module:
        (1) takes in compressed raw lidar in hdf5 files
        (2) identifies vehicles and normalizes data
        (4) stores processed vehicle data as m x n images in hfd5 file
        
    This module works for both 1D and 2D (scanning) lidar data
    
    
    2D lidar
    
    time is vertical starting with earliest time
    data[time][position]
    
    ONlY WORKS AFTER ALL DATA HAS BEEN WRITTEN INTO /compressed_data
"""

import numpy as np
import h5py
from datetime import datetime

INPUT_DIR = "compressed_data"
OUTPUT_DIR = "processed_data"



def normalize_vehicle(v):
    """ takes in numpy array of vehicle data, processes it, returns numpy array of vehicle data """
    pass


def vehicle_detected(a):
    """ a is a numpy array of arbitrary length. method returns true if there is a vehicle """
    pass


def find_vehicle(data, input_file, keys, start_time):
    """
    return are_more_vehicles, vehicle (numpy array), vehicle_ID (unique)
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
    
def get_files_to_process():
    output = []
    
    for file in os.listdir(INPUT_DIR):
       if(is_hdf5_file(file)):
           output.append(os.path.join(INPUT_DIR, file))  

    return output

def main():
    
    files_to_process = get_files_to_process()
    
    input_file = h5py.File("compressed_data.h5", 'r')
    keys = input_file.keys()
    keys.sort() # ensure that data is processed in order
    
    output_file = h5py.File(os.path.join(OUTPUT_DIR, "vehicles.h5"), 'a')
    
    are_more_vehicles = True
    
    while(are_more_vehicles):
        
        are_more_vehicles, vehicle, vehicle_ID = find_vehicle(lidar_data, input_file, keys, start)
        
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    