steps:

1. lidar collects data and stores it in /raw_data
2. compress_raw_data.py compresses this data into hdf5 files in /compressed_data 
3. process_compressed_data.py normalizes and processes this compressed data and 
		stores it in /processed_data
4. augment_data.py augments the data
5. run_classifier.py classifies vehicles in hfd5 files