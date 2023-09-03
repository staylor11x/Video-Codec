'''
    Class to handle file system operations
'''

import yuvio
import pandas as pd

class FileSystem():


    def __init__(self):
        pass

    @staticmethod
    def write_yuv_file(filename, frames, width=352, height=288, file_format="yuv420p"):
        writer = yuvio.get_writer(filename, width, height, file_format)

        for i in range(len(frames)):
            writer.write(frames[i])

    @staticmethod
    def save_to_file(filename, data):
        with open(filename, 'w') as file:
            file.write(data)

    @staticmethod
    def dataframe_to_nparray(path, sheetname):
        df = pd.read_excel(path, sheet_name=sheetname, header=None)
        np_array = df.values

        return np_array
    
    @staticmethod
    def save_binary_file(filename,data):
        packed_data = int(data, 2).to_bytes((len(data) + 7) // 8, byteorder='big')
        with open(filename, "wb") as file:
            file.write(packed_data)

    @staticmethod
    def open_binary_file(filename):

        with open(filename,"rb") as file:
            packed_data_in = file.read()

        unpacked_data = ''.join(format(byte, '08b') for byte in packed_data_in)
        unpacked_data = unpacked_data.lstrip('0')
        unpacked_data = '0'*1 + unpacked_data   #this is horrendous, short term fix

        #for some reason two 0s are added at the start at some point during this save/load process
        #unpacked_data = unpacked_data[2:]

        return unpacked_data