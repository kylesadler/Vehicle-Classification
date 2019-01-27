import numpy as np
import h5py

""" This module:
        (1) takes in compressed raw lidar data
        (2) identifies vehicles in the compressed data
        (3) processes and normalizes data for each vehicle
        (4) stores processed vehicle data as m x n images in hfd5 file
        
    This module works for both 1D and 2D (scanning) lidar data
"""

def read_in_data():
    """ reads in data from file, returns a numpy array of data """
    """
        for 2D array temporal axis is vertical, spatial axis (vertical in real life) is horizontal
        array[time][location]
    """
    pass


def normalize_vehicle():
    """ takes in numpy array of vehicle data, processes it, returns numpy array of vehicle data """
    pass


def store_as_hdf5(data):
    """ stores the numpy array as hdf5 file """
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
    
    processed_vehicles = []
    count = 0 # consecutive measurements with a vehicle detected
    current_vehicle =[]
    recording_vehicle = False
    
    
    # data[time][position], measurement is a data capture at a specific time
    for time in range(len(data)): # go through measurements identifying vehicles; if vehicle is found, process and add to list
        
        measurement = data[time]
        
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
        
    
    
    return processed_vehicles
    
def main():
    data_to_process = read_in_data() # array
    
    """if(SINGLE_BEAM_LIDAR):
        processed_data = process_single_beam_data(data_to_process)
    else:
        processed_data = process_scanning_data(data_to_process)
    """
    
    processed_vehicles = processed_vehicles(data_to_process)

    store_as_hdf5(processed_vehicles)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    