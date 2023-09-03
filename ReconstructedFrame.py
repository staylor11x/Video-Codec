'''
    Class to create reconstucted frame objects
'''

import numpy as np

class ReconstructedFrame():

    def __init__(self, Y=None, U=None, V=None):

        self.Y = Y
        self.Cr = U
        self.Cb = V

    @staticmethod
    def reconstruct_component(blocks, height, width):
        '''reconstruct the frame from the 8x8 blocks'''

        component = np.zeros((height, width))
        block_idx = 0

        for y in range(0, height, 8):
            for x in range(0, width, 8):
                block = blocks[block_idx]
                component[y:y+8,x:x+8] = block
                block_idx +=1

        return component + 128
    
    @staticmethod
    def reconstruct_yuv_frame(frame):
        '''Reconstruct yuv frames, clip values at 0,255 range'''
        frame.Y = ReconstructedFrame.reconstruct_component(frame.Y, 288, 352).clip(0, 255).astype(np.uint8)
        frame.Cr = ReconstructedFrame.reconstruct_component(frame.Cr, 144, 176).clip(0, 255).astype(np.uint8)
        frame.Cb = ReconstructedFrame.reconstruct_component(frame.Cb, 144, 176).clip(0, 255).astype(np.uint8)

        return frame