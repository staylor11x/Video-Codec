"""

Program to perform video compression on .yuv files!

Developer: Scott Taylor
Organisation: Robert Gordon University
Date: Jul 2023

"""

import yuvio
import numpy as np
import sys

from Frame import Frame
from Encoder import Encoder
from HuffmanCodec import HuffmanCodec
from Decoder import Decoder
from ReconstructedFrame import ReconstructedFrame
from FileSystem import FileSystem


def reconstruct_yuv_frame(frame):
    '''Reconstruct yuv frames, clip values at 0,255 range'''
    frame.Y = ReconstructedFrame.reconstruct_component(frame.Y, 288, 352).clip(0, 255).astype(np.uint8)
    frame.Cr = ReconstructedFrame.reconstruct_component(frame.Cr, 144, 176).clip(0, 255).astype(np.uint8)
    frame.Cb = ReconstructedFrame.reconstruct_component(frame.Cb, 144, 176).clip(0, 255).astype(np.uint8)

    return frame

def get_differnce_frame(predicted_frame, actual_frame):

    actual_frame.Y = actual_frame.Y.astype(np.int16)
    actual_frame.Cb = actual_frame.Cb.astype(np.int16)
    actual_frame.Cr = actual_frame.Cr.astype(np.int16)

    predicted_frame.Y = predicted_frame.Y.astype(np.int16)
    predicted_frame.Cb = predicted_frame.Cb.astype(np.int16)
    predicted_frame.Cr = predicted_frame.Cr.astype(np.int16)    

    actual_frame.Y =  actual_frame.Y  - predicted_frame.Y 
    actual_frame.Cb = actual_frame.Cb - predicted_frame.Cb
    actual_frame.Cr = actual_frame.Cr - predicted_frame.Cr

    return actual_frame

def add_differnce_frame(prev_frame, current_frame):

    current_frame.Y = np.clip(current_frame.Y + prev_frame.Y, 0,255)
    current_frame.Cr = np.clip(current_frame.Cr + prev_frame.Cr, 0,255)
    current_frame.Cb = np.clip(current_frame.Cb + prev_frame.Cb, 0,255)

    return current_frame

def compute_motion_vectors(previous_frame, current_frame, block_size, search_window_size):
    height, width = current_frame.shape
    motion_vectors = np.zeros((height // block_size, width // block_size, 2), dtype=np.int32)

    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            best_sad = float('inf')
            best_dx, best_dy = 0, 0

            for dy in range(-search_window_size, search_window_size + 1):
                for dx in range(-search_window_size, search_window_size + 1):
                    if y + dy < 0 or y + dy + block_size > height or x + dx < 0 or x + dx + block_size > width:
                        continue

                    current_block = current_frame[y:y + block_size, x:x + block_size]
                    previous_block = previous_frame[y + dy:y + dy + block_size, x + dx:x + dx + block_size]

                    sad = np.sum(np.abs(current_block - previous_block))
                    if sad < best_sad:
                        best_sad = sad
                        best_dx, best_dy = dx, dy

            block_y, block_x = y // block_size, x // block_size
            motion_vectors[block_y, block_x, 0] = best_dx
            motion_vectors[block_y, block_x, 1] = best_dy

    return motion_vectors

def motion_compensation(previous_frame, motion_vectors, block_size):
    height, width = previous_frame.shape
    predicted_frame = np.zeros_like(previous_frame)

    for block_y in range(height // block_size):
        for block_x in range(width // block_size):
            dx, dy = motion_vectors[block_y, block_x]
            start_y = block_y * block_size
            start_x = block_x * block_size
            end_y = start_y + block_size
            end_x = start_x + block_size

            predicted_frame[start_y:end_y, start_x:end_x] = previous_frame[start_y + dy:end_y + dy, start_x + dx:end_x + dx]

    return predicted_frame

def save_encoded_video(frame):
    pass



'''read in Quantization Tables'''
#from: https://fotoforensics.com/tutorial.php?tt=estq#:~:text=JPEG's%20lossy%20compression%20is%20due,responsible%20for%20the%20picture's%20quality.
Luminance_Quantization = FileSystem.dataframe_to_nparray("Quantization Tables.xlsx", sheetname="Luminance")
Chrominance_Quantization = FileSystem.dataframe_to_nparray("Quantization Tables.xlsx", sheetname="Chrominance")

'''Initalise Objects and Variables'''
frames = []
new_yuv_frames = []
residual_frames = []
stringified_object = ''
encoder = Encoder(Luminance_Quantization,Chrominance_Quantization)
decoder = Decoder(Luminance_Quantization,Chrominance_Quantization)
HuffmanEncoder = HuffmanCodec()

'''read yuv frames from file'''
yuv_frames = yuvio.mimread("akiyo_cif.yuv", 352, 288, "yuv420p");

'''Get the first frame'''
first_frame = Frame(yuv_frames[0].y, yuv_frames[0].u, yuv_frames[0].v)

'''encode the first frame'''
Frame.adjust_range(first_frame)
Frame.divide_into_blocks(first_frame)
encoder.dct_and_quantise(first_frame)

'''Store Encoded data'''
encoder.encode(first_frame)
stringified_object += repr(first_frame)     #this is where we store the raw string
decoder.decode(first_frame)

'''Decode the first frame'''
decoder.idct_and_unquantise(first_frame)

'''reconstruct the frame'''
first_frame = reconstruct_yuv_frame(first_frame)
new_yuv_frames.append(yuvio.frame((first_frame.Y,first_frame.Cr,first_frame.Cb),"yuv420p"))


'''Create the rest of the frame objects'''
for i in range(1,25):
    frames.append(Frame(yuv_frames[i].y, yuv_frames[i].u, yuv_frames[i].v))

for i in range(len(frames)):

    motion_vectors = compute_motion_vectors(first_frame.Y,frames[i].Y, 8, 8)
    predicted_Y = motion_compensation(first_frame.Y, motion_vectors,8)
    predicted_frame = Frame(predicted_Y,frames[i].Cr,frames[i].Cb)

    residual_frame = get_differnce_frame(predicted_frame,frames[i])

    Frame.adjust_range(predicted_frame)
    Frame.divide_into_blocks(predicted_frame)
    encoder.dct_and_quantise(predicted_frame)

    #<---- save the video to a file ---->
    encoder.encode(predicted_frame)
    stringified_object += repr(predicted_frame)
    decoder.decode(predicted_frame)  

    decoder.idct_and_unquantise(predicted_frame)
    reconstruct_yuv_frame(predicted_frame)

    predicted_frame = add_differnce_frame(predicted_frame,residual_frame)

    new_yuv_frames.append(yuvio.frame((predicted_frame.Y,predicted_frame.Cr,predicted_frame.Cb),"yuv420p"))


'''Write frames to .yuv file'''
FileSystem.write_yuv_file("Compressed.yuv",new_yuv_frames)

'''save uncompressed file'''
FileSystem.save_to_file("Compressed_Dev.txt",stringified_object)

'''huffman encode the data'''
encoded_data, tree = HuffmanEncoder.huffman_encoding(stringified_object)

'''save the compressed file'''
FileSystem.save_binary_file("SuperCompressed_Dev.bin",encoded_data)

'''open the file'''
unpacked_data = FileSystem.open_binary_file("SuperCompressed_Dev.bin")

'''Decode the file'''
decoded_output = HuffmanCodec.huffman_decoding(unpacked_data, tree)

'''check the encoded and decoeded strings are the same'''
if(HuffmanCodec._find_first_difference(stringified_object,decoded_output)):
    print("Files are the same, encoding and decoding completed sucessfully!")
else:
    print("Error in encoding and decoding string")

'''Reconstruct and decode the frames'''
reconstructed_frames = decoder._convert_to_object(decoded_output)

'''reconstruct yuv frames'''
final_frames = []
for i in range(len(reconstructed_frames)):
    decoder.decode(reconstructed_frames[i])
    decoder.idct_and_unquantise(reconstructed_frames[i])
    reconstructed_frames[i] = reconstruct_yuv_frame(reconstructed_frames[i])
    final_frames.append(yuvio.frame((reconstructed_frames[i].Y,reconstructed_frames[i].Cr,reconstructed_frames[i].Cb),"yuv420p"))


'''Write frames to .yuv file'''
FileSystem.write_yuv_file("Uncompressed_decompressed.yuv", final_frames)

