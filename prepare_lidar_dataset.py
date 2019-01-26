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
    pass

def process_data():
    """ takes in numpy array of data, processes it, returns numpy array of data """
    pass

def store_as_hdf5():
    """ stores the numpy array as hdf5 file """
    pass

def detect_vehicles():
    """ returns an array of starting and ending indeces of vehicles, given a numpy array of raw data """
    pass

def main():
    pass