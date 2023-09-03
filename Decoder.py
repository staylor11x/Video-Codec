'''
    Class to handle video decoding
'''

from ReconstructedFrame import ReconstructedFrame
import numpy as np
from scipy.fftpack import idct

class Decoder():

    def __init__(self, lumQ, chromQ, quality):

        self.luminance_quantisation = lumQ
        self.chrominance_quantisation = chromQ
        self.quantisation_level = quality

        self.get_quantisation_level()

    def get_quantisation_level(self):
        
        self.luminance_quantisation = ((100-self.quantisation_level)/50*self.luminance_quantisation).astype(np.uint8)
        #self.chrominance_quantisation = (100-self.quantisation_level)/50*self.chrominance_quantisation

    def decode(self, frame):
        
        frame.Y = np.array(self._run_length_decode(frame.Y))
        frame.Cr = np.array(self._run_length_decode(frame.Cr))
        frame.Cb = np.array(self._run_length_decode(frame.Cb))
    
        temp_Y = []        
        temp_Cr = []
        temp_Cb = []
        for i in range(0,len(frame.Y),64):
            temp_Y.append(self._unflatten_matrix(frame.Y[i:i+64]))
        for i in range(0,len(frame.Cr),64):
            temp_Cr.append(self._unflatten_matrix(frame.Cr[i:i+64]))
        for i in range(0, len(frame.Cb),64):
            temp_Cb.append(self._unflatten_matrix(frame.Cb[i:i+64]))

        frame.Y =  np.array(temp_Y)
        frame.Cb = np.array(temp_Cb)
        frame.Cr = np.array(temp_Cr)

    def idct_and_unquantise(self,frame):

        for i in range(0, len(frame.Y)):
            frame.Y[i] = self._reverse_dct_2D(self._unquantize(frame.Y[i], self.luminance_quantisation)).astype(np.int16) 
        for i in range(0, len(frame.Cr)):
            frame.Cr[i] = self._reverse_dct_2D(self._unquantize(frame.Cr[i], self.chrominance_quantisation)).astype(np.int16)
        for i in range(0, len(frame.Cb)):
            frame.Cb[i] = self._reverse_dct_2D(self._unquantize(frame.Cb[i], self.chrominance_quantisation)).astype(np.int16)

    @staticmethod
    def _unquantize(matrix, quantisation_table):
        return matrix*quantisation_table
    
    @staticmethod
    def _reverse_dct_2D(matrix):
        return idct(idct(matrix.T, norm='ortho').T, norm='ortho')

    @staticmethod
    def _run_length_decode(encoded):
        decoded = []
        pairs = encoded.split(",")

        for pair in pairs:
            if pair:
                count, value = pair.split("x")
                for i in range(0,int(count)):
                    decoded.append(int(value))
        return decoded

    @staticmethod
    def _convert_to_object(string):
        frames = []
        len_string = len(string)
        Y_indices = [i+1 for i in range(len_string) if string[i] == "Y"]
        U_indices = [i+1 for i in range(len_string) if string[i] == "U"]
        V_indices = [i+1 for i in range(len_string) if string[i] == "V"]

        for i in range(len(Y_indices)):
            Y = string[Y_indices[i]:U_indices[i]-1]
            U = string[U_indices[i]:V_indices[i]-1]
            V = string[V_indices[i]:Y_indices[i+1]-1] if i < len(Y_indices) - 1 else string[V_indices[i]:]
            frames.append(ReconstructedFrame(Y, U, V))

        return frames
    
    @staticmethod
    def _unflatten_matrix(array):

        rows = cols = 8
        matrix = np.zeros((rows, cols), dtype=int)
        index = 0

        for k in range(rows + cols - 1):
            if k % 2 == 0:
                i = min(k, rows - 1)
                j = k - i
                while i >= 0 and j < cols:
                    matrix[i][j] = array[index]
                    index += 1
                    i -= 1
                    j += 1
            else:
                j = min(k, cols - 1)
                i = k - j
                while j >= 0 and i < rows:
                    matrix[i][j] = array[index]
                    index += 1
                    i += 1
                    j -= 1

        return matrix