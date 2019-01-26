# make sure only copying measurement values, not extraneous info

"""
 lidar sensor outputs uncompressed data files named raw_data_XYZ.log where XYZ is a natural number with up to three digits.
 These files are originally stored in /raw_data.
 
 For each raw_data_XYZ.log file, this program:
 (1) creates a new file "YYYY_MM_DD_HH_MM_SS_compressed_data.log" where YYYY_MM_DD_HH_MM_SS is the date and time
 the data was taken.
 (2) compresses the data from raw_data_XYZ.log into new file
 (3) stores new file in directory /compressed_data
 (4) deletes the original raw_data_XYZ.log file
 
 This program also logs all errors in data_compressor_error_log.log and to screen
 
 input_file is of format "raw_data_XYZ.log" where XYZ is a natural number
 output_file is of format "YYYY_MM_DD_HH_MM_SS_compressed_data.log"
 
 File setup:
 
 workspace
    |-> raw_data
    |   |-> raw_data_XYZ.log files
    |    
    |-> data_compressor.py
    |
    |-> compressed_data (created by this program)
    |   |-> YYYY_MM_DD_HH:MM:SS_compressed_data.log
    |
    |-> data_compressor_error_log.log (created by this program)
        

"""

import os
from time import sleep
from datetime import datetime

input_directory = "raw_data"
output_directory = "compressed_data"
log_file_name = "data_compressor_error_log.log"
TIME_INTERVAL_MIN = 10;  # time in minutes to let files complete writing before processing, 2x lidar output interval suggested



log_file = open(log_file_name, "a+")  # opens the log file (or creates it if it does not exist)
incorrectly_formatted_files = [] # so repeated warnings don't flood error log
if not os.path.exists(output_directory): # make output_directory if it doesn't exist
    os.makedirs(output_directory)


def main():
    # files that have been in /raw_data directory for over TIME_INTERVAL_MIN minutes
    files_to_compress = []  # use dictionary if tons and tons of files
    
    while(True):
        
        # loop through all files that have been in /raw_data directory for over TIME_INTERVAL_MIN minutes
        for data_file in files_to_compress: 
            
            # if a "raw_data_XYZ.log" file
            if(is_raw_data(data_file)): 
                
                # try to compress input file
                try:
                    
                    # try to open the input file
                    input_file_name = os.path.join(input_directory, data_file)
                    try:
                        input_file = open(input_file_name, "r")
                    except:
                        log_error("could not open input file: " + input_file_name)
                        continue  # skip loop iteration so file is not deleted
                    
                    # get first timestamp of data
                    line = input_file.readline()
                    date = line[0:10].replace("-", "_")
                    time = line[11:19].replace(":", "_") # windows does not allow ":" in filenames
                    
                    # try to create the output file
                    output_file_name = os.path.join(output_directory, date + "_" + time + "_compressed_data.log")
                    try:
                        output_file = open(output_file_name, "w+") 
                    except:
                        log_error("could not create output file: " + output_file_name + "\n" + "from input file: " + input_file_name)
                        continue  # skip loop iteration so file is not deleted
                
                    # loop through input file, compress each line, and write to output file
                    while(line != ""):
                        
                        # try to compress line
                        try:
                            compressed_line = compress_line(line)
                        except:
                            log_error("could not parse line: " + line  + "in file: " + input_file_name)
                            raise 
                        
                        if(compressed_line == ""):
                            line = input_file.readline()
                            continue
                        
                        # try to write compressed line to output_file   
                        try:
                            output_file.write(compressed_line + "\n")
                        except:
                            log_error("could not write compressed line to file: " + output_file_name)
                            raise
                        
                        line = input_file.readline()
                        
                # else log error to log_file and skip data_file
                except:
                    log_error("could not compress file: " + input_file_name)
                    continue  # skip loop iteration so file is not deleted
                    
                # try to delete data_file to free space
                try:
                    input_file.close()
                    os.remove(input_file_name)
                except Exception as e:
                    print(repr(e))
                    log_warning("could not delete file: " + input_file_name)
                                  
        # get all files in directory
        files_to_compress = os.listdir(input_directory) 
        
        # sleeps for TIME_INTERVAL_MIN
        sleep(60 * TIME_INTERVAL_MIN);

            
def is_raw_data(f):  # returns true if file name is of correct format, returns false otherwise
    
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
                if(f not in incorrectly_formatted_files):
                    log_warning("raw_data file name may be incorrectly formatted: " + name)
                    incorrectly_formatted_files.append(f)
                return False

    return False

        
def compress_line(l):  # returns a compressed line from raw_data file. If line cannot be compressed, throws exception
    
    # find index of the first '<'
    index = 23
    while(index < len(l)):
        if(l[index] != '<'):
            index += 1
        else:
            break
    
    if(index == len(l)): # if no '<' in line
        return ""
    else:
        # set output equal to the timestamp of line
        output = l[:23]
        
        # get data points as strings
        data_points = l[index+1:-2].split("><")
        
        for data in data_points:
            output += " " + data
        
        return output

def log_error(error_string):  # write string s to log file and screen
    error = "[ERROR] " + str(datetime.now()) + " " + error_string + "\n"
    log_file.write(error)
    log_file.flush() # remove this for increased performance
    print(error,)

def log_warning(warning_string):  # write string s to log file and screen
    warning = "[WARNING] " + str(datetime.now()) + " " + warning_string + "\n"
    log_file.write(warning)
    log_file.flush() # remove this for increased performance
    print(warning,)


if(__name__ == "__main__"):  # just a workaround to call functions before they are defined
    main()
    
