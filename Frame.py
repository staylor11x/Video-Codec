'''
    Classs to create frame objects

'''
import numpy as np

class Frame():

    def __init__(self, Y = None, Cr = None, Cb = None ):

        self.Y = np.array(Y, dtype=np.int16)
        self.Cr = np.array(Cr, dtype=np.int16) 
        self.Cb = np.array(Cb, dtype=np.int16)



    def __repr__(self):
        return (f"Y{self.Y}U{self.Cr}V{self.Cb}")   #Y, U & V used as this is easier to decode

    @staticmethod
    def adjust_range(frame):
        frame.Y -= 128
        frame.Cr -= 128
        frame.Cb -= 128


    def divide_into_blocks(self):
        self.Y = self._divide_into_blocks(self.Y)
        self.Cr = self._divide_into_blocks(self.Cr)
        self.Cb = self._divide_into_blocks(self.Cb)

    @staticmethod
    def _divide_into_blocks(component):
        #need to add some error handling in here to catch if the picture can be divided
        #evenly or if the size !=8

        height, width = component.shape
        blocks = []
        for y in range(0, height, 8):
            for x in range(0, width, 8):
                block = component[y:y+8,x:x+8]
                blocks.append(block)
        return blocks
    



