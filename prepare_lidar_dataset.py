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
    """ reads in data from file, returns a 2D numpy array of data (even if data is only 1D) """
    """
        temporal axis is vertical, spatial axis (vertical in real life) is horizontal with "up" being
        array[time][location]
    """
    pass

def process_vehicle():
    """ takes in numpy array of vehicle data, processes it, returns numpy array of vehicle data """
    pass

def store_as_hdf5():
    """ stores the numpy array as hdf5 file """
    pass

def detect_vehicles():
    """ returns an array of starting and ending indices of vehicles, given a numpy array of raw data """
    pass

def main():
    data_to_process = read_in_data() # array?
    
    
    for data in data_to_process:
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    