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


def process_vehicle():
    """ takes in numpy array of vehicle data, processes it, returns numpy array of vehicle data """
    pass


def store_as_hdf5(data):
    """ stores the numpy array as hdf5 file """
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
    
    # data[time][position], measurement is a data capture at a specific time
    for measurement in data:
        pass
    
def main():
    data_to_process = read_in_data() # array
    
    """if(SINGLE_BEAM_LIDAR):
        processed_data = process_single_beam_data(data_to_process)
    else:
        processed_data = process_scanning_data(data_to_process)
    """
    
    processed_data = process_data(data_to_process)

    store_as_hdf5(processed_data)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    