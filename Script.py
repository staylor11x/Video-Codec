"""

Program to perform video compression on .yuv files!

Developer: Scott Taylor
Organisation: Robert Gordon University
Date: Jul 2023


Bugs:

The program can throw an error when reading from the binary file, when doing so it adds arbitrarily adds/removes zeroes
    -- Error in FileSystem --> open_binary_file
This does not affect the main function of the program.
"""

import yuvio

from Frame import Frame
from Encoder import Encoder
from HuffmanCodec import HuffmanCodec
from Decoder import Decoder
from ReconstructedFrame import ReconstructedFrame as rf
from FileSystem import FileSystem as fs
from MotionCompensation import MotionCompensation
from ErrorCalculation import ErrorCalculation as ec

'''read in Quantization Tables'''
#from: https://fotoforensics.com/tutorial.php?tt=estq#:~:text=JPEG's%20lossy%20compression%20is%20due,responsible%20for%20the%20picture's%20quality.
Luminance_Quantization = fs.dataframe_to_nparray("Quantization Tables.xlsx", sheetname="Luminance")
Chrominance_Quantization = fs.dataframe_to_nparray("Quantization Tables.xlsx", sheetname="Chrominance")

'''Initalise Objects and Variables'''

#The Original Video Sequence
frames = []

#The Encoded Video Sequence
new_yuv_frames = []

#Final YUV frames saved to file (after run length and huffman encoding)
final_frames = []

#String to store raw encoded data
stringified_object = ''

#block size for motion estimation
block_size = 8

#search area for motion estimation
search_area = 8

#quality (Determines the quantisation level)
quality = 40

#Class to handle video encoding
encoder = Encoder(Luminance_Quantization,Chrominance_Quantization,quality)

#Class to handle video decoding
decoder = Decoder(Luminance_Quantization,Chrominance_Quantization,quality)

#Class to handle huffman encoding and decoding
HuffmanEncoder = HuffmanCodec()

#Class to handle motion compensation
MotionCompensation = MotionCompensation(search_area,block_size)

'''________________Start of Program________________'''

filename = "akiyo_cif"
path = "VideoSamples/"
#Read YUV frames from file
yuv_frames = yuvio.mimread(path + filename + ".yuv", 352, 288, "yuv420p");

#Get the reference frame
referance_frame = Frame(yuv_frames[0].y, yuv_frames[0].u, yuv_frames[0].v)

#Encode the referance frame
Frame.adjust_range(referance_frame)
Frame.divide_into_blocks(referance_frame)
encoder.dct_and_quantise(referance_frame)

#Run length encode the data and store in string
encoder.encode(referance_frame)
stringified_object += repr(referance_frame)     
decoder.decode(referance_frame)

#Decode the first frame
decoder.idct_and_unquantise(referance_frame)

#Reconstruct the first frame
referance_frame = rf.reconstruct_yuv_frame(referance_frame)
new_yuv_frames.append(yuvio.frame((referance_frame.Y,referance_frame.Cr,referance_frame.Cb),"yuv420p"))


#create the rest of the frame objects
for i in range(1,4):
    frames.append(Frame(yuv_frames[i].y, yuv_frames[i].u, yuv_frames[i].v))

#encode the rest of the frames
for i in range(len(frames)):

    #calculate motion vectors and perform motion estimation
    motion_vectors = MotionCompensation.compute_motion_vectors(referance_frame.Y,frames[i].Y)
    predicted_Y = MotionCompensation.get_predicted_frame(referance_frame.Y,motion_vectors)
    predicted_frame = Frame(predicted_Y,frames[i].Cr,frames[i].Cb)
    difference_frame = MotionCompensation.get_differnce_frame(predicted_frame,frames[i])

    Frame.adjust_range(difference_frame)
    Frame.divide_into_blocks(difference_frame)
    encoder.dct_and_quantise(difference_frame)

    #<---- Encoded Data ---->
    encoder.encode(difference_frame)
    stringified_object += repr(difference_frame) # + motion vectors
    decoder.decode(difference_frame)  

    #Reconstruct the frame
    decoder.idct_and_unquantise(difference_frame)
    rf.reconstruct_yuv_frame(difference_frame)

    predicted_Y = MotionCompensation.get_predicted_frame(referance_frame.Y,motion_vectors)    

    predicted_frame = MotionCompensation.add_differnce_frame(predicted_frame,difference_frame)

    new_yuv_frames.append(yuvio.frame((predicted_frame.Y,predicted_frame.Cr,predicted_frame.Cb),"yuv420p"))


#write frames to YUV file 
fs.write_yuv_file(f"GeneratedFiles/{filename}_Q{quality}_SA{search_area}_Compressed.yuv",new_yuv_frames)


'''Inspect a frame for PSNR'''
frame_number = 3
psnr = ec.calculate_psnr(yuv_frames[frame_number].y,new_yuv_frames[frame_number].y)
print("PSNR: ", psnr)



'''_____________Still in Development_____________'''

#Save the run length encoded data
fs.save_to_file(f"GeneratedFiles/{filename}_Q{quality}_SA{search_area}_RunLengthEncoded.txt",stringified_object)

#Huffman encode the data
encoded_data, tree = HuffmanEncoder.huffman_encoding(stringified_object)

#Save the Huffman Encoded Data
fs.save_binary_file(f"GeneratedFiles/{filename}_Q{quality}_SA{search_area}_HuffmanEncoded.bin",encoded_data)

#open the file
unpacked_data = fs.open_binary_file(f"GeneratedFiles/{filename}_Q{quality}_SA{search_area}_HuffmanEncoded.bin")

#Decode the data
decoded_output = HuffmanCodec.huffman_decoding(unpacked_data, tree)

#check the encoded and decoded data string are the same
if(HuffmanCodec._find_first_difference(stringified_object,decoded_output)):
    print("Files are the same, encoding and decoding completed sucessfully!")
else:
    raise Exception("Error in encoding and decoding string, strings do not match")

#Reconstruct and decode the frames
reconstructed_frames = decoder._convert_to_object(decoded_output)

#Construct the Yuv Frames
for i in range(len(reconstructed_frames)):
    decoder.decode(reconstructed_frames[i])
    decoder.idct_and_unquantise(reconstructed_frames[i])
    reconstructed_frames[i] = rf.reconstruct_yuv_frame(reconstructed_frames[i])
    final_frames.append(yuvio.frame((reconstructed_frames[i].Y,reconstructed_frames[i].Cr,reconstructed_frames[i].Cb),"yuv420p"))


'''This is where you compute the motion estimation & add difference frame
    --Maybe this will be done one day!
'''

#Write to YUV file
#fs.write_yuv_file(f"GeneratedFiles/{filename}_Q{quality}_Uncompressed_decompressed.yuv", final_frames)