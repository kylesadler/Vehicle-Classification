""" This module:
        (1) takes in compressed raw lidar data
        (2) identifies vehicles in the compressed data
        (3) processes data for each vehicle
        (4) stores this processed data as m x n images in hfd5 file
        
    This module works for both 1D and 2D (scanning) lidar data
"""