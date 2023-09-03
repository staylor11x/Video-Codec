'''
    A class to handle the video encoding process
'''

import numpy as np
from scipy.fftpack import dct

class Encoder():
    
    def __init__(self, lumQ, chromQ, quality):

        self.luminance_quantisation = lumQ
        self.chrominance_quantisation = chromQ
        self.quantisation_level = quality

        self.get_quantisation_level()

    def get_quantisation_level(self):

        self.luminance_quantisation = ((100-self.quantisation_level)/50*self.luminance_quantisation).astype(np.uint8)
        #self.chrominance_quantisation = (100-self.quantisation_level)/50*self.chrominance_quantisation

    def encode(self, frame):
        for i in range(len(frame.Y)):
            frame.Y[i] = self.run_length_encode(self._flatten_matrix(frame.Y[i]))
        for i in range(len(frame.Cb)):
            frame.Cb[i] = self.run_length_encode(self._flatten_matrix(frame.Cb[i]))
        for i in range(len(frame.Cr)):
            frame.Cr[i] = self.run_length_encode(self._flatten_matrix(frame.Cr[i]))
    
        frame.Y = '\n'.join([''.join(row for row in frame.Y)])
        frame.Cb = '\n'.join([''.join(row for row in frame.Cb)])
        frame.Cr = '\n'.join([''.join(row for row in frame.Cr)])

    def dct_and_quantise(self,frame):

        for i in range(len(frame.Y)):
            frame.Y[i] = self._quantise(self._dct_2D(frame.Y[i]), self.luminance_quantisation)
        for i in range(len(frame.Cb)):
            frame.Cb[i] = self._quantise(self._dct_2D(frame.Cb[i]), self.chrominance_quantisation)
        for i in range(len(frame.Cr)):
            frame.Cr[i] = self._quantise(self._dct_2D(frame.Cr[i]), self.chrominance_quantisation)
            
    @staticmethod
    def _dct_2D(matrix):
        return dct(dct(matrix.T, norm='ortho').T, norm='ortho')
    
    @staticmethod
    def _quantise(matrix, quantisation_table):
        quantised_matrix = np.round(matrix/quantisation_table).astype(np.int8)
        return quantised_matrix
    
    def run_length_encode(self, array):
        '''run length encode the data'''   
        encoded = ""
        count = 1
        prev_value = array[0]

        for i in range(1, len(array)):
            if array[i] == prev_value:
                count += 1
            else:
                encoded = encoded + str(count) + "x" + str(prev_value) + ","
                count = 1
                prev_value = array[i]

        encoded = encoded + str(count) + "x" + str(prev_value) + ","
        return encoded

    @staticmethod
    def _flatten_matrix(matrix):
        '''itterate over the matrix diagonally using bionmial dist principles'''

        rows, cols = matrix.shape
        result = []

        for k in range(rows + cols - 1):
            if k % 2 == 0:
                i = min(k, rows - 1)
                j = k - i
                while i >= 0 and j < cols:
                    result.append(matrix[i][j])
                    i -= 1
                    j += 1
            else:
                j = min(k, cols - 1)
                i = k - j
                while j >= 0 and i < rows:
                    result.append(matrix[i][j])
                    i += 1
                    j -= 1

        return result


        
