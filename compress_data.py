# make sure only copying measurement values, not extraneous info

"""
 lidar sensor outputs uncompressed data files named raw_data_XYZ.log where XYZ is a natural number with up to three digits.
 These files are originally stored in /raw_data.
 
 this program compresses these raw data files into one hdf5 file (hdf5 files have no constraints on size)
 
 Working_Directory
    --> raw_data
        --> raw_data_XYZ.log
        --> ...
        --> raw_data_XYZ.log
    
    --> YYYY-MM-DD UNPROCESSED
        --> YYYY-MM-DD-HHMM{RECORDING_LOCATION}.h5
    
    --> compress_data.py
    
    --> compress_data_error_log.log
        

"""

import os
from time import sleep
from datetime import datetime
import numpy as np
import h5py

###	params to configure	###
RECORDING_LOCATION = 0	# if unsure of your recording location number, talk to Dr. Hernandez
INPUT_DIR = "raw_data"	# lidar outputs raw data files into this directory
MIN_TO_SLEEP = 0.01; 	# time to let files complete writing before processing, 2x lidar output interval suggested
ERRORS_ONLY = False	# prints and logs only errors (ignores warnings) if true
###################################


OUTPUT_DIR = None
LOG_FILE_NAME = "compress_data_error_log.log"
BASE_OF_DATA_POINTS = 16 # should be in hexadecimal

log_file = open(LOG_FILE_NAME, "a+")  # opens the log file (or creates it if it does not exist)
incorrectly_formatted_files = [] # so warnings don't flood error log



def main():
    
    compressed_data_file_name = None
    
    while(True):
        
        # get all files to compress in directory
        files_to_compress = get_files_to_compress(os.listdir(INPUT_DIR))
        
        if(len(files_to_compress) == 0):
            continue
        
        # sleeps for MIN_TO_SLEEP, let files_to_compress finish writing
        sleep(60 * MIN_TO_SLEEP);

            
        files_to_compress.sort() # ensures that data is in correct order
        dataset_name = get_name(files_to_compress[0]) # store each dataset as the earliest timestamp of the file batch
        compressed_data = [] # data for the entire loop of files
        files_to_delete =[]
        
        if(compressed_data_file_name == None):
            # compressed_data_file_name is YYYY-MM-DD-HHMM{RECORDING_LOCATION}
            compressed_data_file_name = dataset_name[:4]+"-"+dataset_name[4:6]+"-"+dataset_name[6:8]+"-"+dataset_name[8:-2]+str(RECORDING_LOCATION)
            OUTPUT_DIR = compressed_data_file_name[:10] +" UNPROCESSED"
            if not os.path.exists(OUTPUT_DIR): # make OUTPUT_DIR if it doesn't exist
                os.makedirs(OUTPUT_DIR)
        
        try: # to initialize compressed_data_file
            compressed_data_file = h5py.File(os.path.join(OUTPUT_DIR, compressed_data_file_name + ".h5"), 'a')
        except:
            log_error("could not create compressed data file: " + compressed_data_file_name)
            raise Exception("well shit")
        
        # make a blank params.txt file
        param_file = open(os.path.join(OUTPUT_DIR, "params.txt"), 'a')
        param_file.close()
        
        
        
        for file in files_to_compress: # loop through all files to compress
            
            try: # to open file
                input_file = open(os.path.join(INPUT_DIR, file), "r")
            except:
                log_error("could not open input file: " + input_file.name)
                continue  # skip loop iteration so file is not deleted
            
            line = input_file.readline()
            
            # loop through input file, compress each line, and write to output file
            while(line != ""):
                try: # to compress line
                    compressed_data.append(parse_line(line))
                except Exception as e:
                    log_warning("could not parse line in file: " + input_file.name + ": " + line)
                
                line = input_file.readline()
                    
            input_file.close()
            files_to_delete.append(file)
            print("compressing file " + file)
            
            
        
        
        
        
        try: # to write compressed data to compressed_data_file
            assert(len(compressed_data) > 0)
            array_of_data = np.array([np.array(line) for line in compressed_data]) # convert list of lists to 2D numpy array
            compressed_data_file.create_dataset(dataset_name, data=array_of_data)
        except Exception as e:
            log_error("could not create dataset "+dataset_name+" in " + compressed_data_file_name)
            raise e

        for file in files_to_delete:
            try: # to delete used raw data files
                os.remove(os.path.join(INPUT_DIR, file))
            except Exception as e:
                #print(repr(e))
                log_warning("could not delete raw data file: " + file)
                              
                              
        compressed_data_file.close() # writes compressed_data_file to the disk
        
        
def get_name(file):
    f = open(os.path.join(INPUT_DIR, file), "r")
    
    return f.readline()[:19].replace(":","").replace(".","").replace("-","").replace(" ","")
    
          
def is_raw_data(f):
    """ returns true if file name is of correct format, returns false otherwise """
    
    name = os.path.basename(f)
    split_name = name.split(".")  # {filename, extension}
    
    # checks that f is a log file that starts with "raw_data"
    if(split_name[1] == "log" and split_name[0][0:8] == "raw_data"):
        if(len(split_name[0]) == 8): # if file is "raw_data.log"
            return True
        elif(split_name[0][0:9] == "raw_data_"): # if the file name starts with "raw_data_"
            try:  # tries to parse the number of the file as an int
                file_num = int(split_name[0][9:])
                return True
            except:
                pass

    if(f not in incorrectly_formatted_files):
        incorrectly_formatted_files.append(f)
        log_warning("raw_data file name may be incorrectly formatted: " + name)
        
    return False

def get_files_to_compress(file_list):
    output = []
    
    for file in file_list:
        if(is_raw_data(file)):
            output.append(file)
    
    return output

def parse_line(l):
    """ returns a list of data from line l in a raw_data file. If line cannot be compressed, raises exception """
    
    # transmission type is sSN LMDscandata CoLa A Hex
    # telegram is hex --> convert to ascii --> convert to hex
    
    timestamp = int(l[:19].replace(":","").replace(".","").replace("-","").replace(" ",""))
    
    index = l.index("<") # get first < in line
    line = l[index:].replace('<',"").replace(">","")
    
    
    # convert line from hex to ascii
    ascii_line = bytes.fromhex(line).decode('ASCII')
    #print(ascii_line)
    
    # get transmission parts
    transmission_parts = ascii_line.split(" ")
    
    # this makes sure the line has the correct number of measurements
    num_data_points = int(transmission_parts[25], BASE_OF_DATA_POINTS)
    assert(len(transmission_parts)- 26 - 6 == num_data_points)
    
    # converts data_point in string with specified base to decimal int and add timestamp at end
    output = [int(point, BASE_OF_DATA_POINTS) for point in transmission_parts[26:-6]]
    output.append(timestamp)
    return output

def log_error(error_string):
    """ write string s to log file and screen """
    error = "[ERROR] " + str(datetime.now()) + " " + error_string
    log_file.write(error + "\n")
    log_file.flush() # remove this for increased performance
    print(error)

def log_warning(warning_string):
    """ write string s to log file and screen """
    warning = "[WARNING] " + str(datetime.now()) + " " + warning_string
    log_file.write(warning + "\n")
    log_file.flush() # remove this for increased performance
    if(not ERRORS_ONLY):
        print(warning)

if(__name__ == "__main__"):  # just a workaround to call functions before they are defined
    main()
