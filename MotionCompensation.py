''''
    Class to handle the motion compenstaion algorithms
'''

import numpy as np

class MotionCompensation():

    def __init__(self, search_window_size=8, block_size=8):
        
        self.search_window_size = search_window_size
        self.block_size = block_size
    

    def compute_motion_vectors(self, previous_frame, current_frame):
        height, width = current_frame.shape
        motion_vectors = np.zeros((height // self.block_size, width // self.block_size, 2), dtype=np.int32)

        for y in range(0, height, self.block_size):
            for x in range(0, width, self.block_size):
                best_sad = float('inf')
                best_dx, best_dy = 0, 0

                for dy in range(-self.search_window_size, self.search_window_size + 1):
                    for dx in range(-self.search_window_size, self.search_window_size + 1):
                        if y + dy < 0 or y + dy + self.block_size > height or x + dx < 0 or x + dx + self.block_size > width:
                            continue

                        current_block = current_frame[y:y + self.block_size, x:x + self.block_size]
                        previous_block = previous_frame[y + dy:y + dy + self.block_size, x + dx:x + dx + self.block_size]

                        sad = np.sum(np.abs(current_block - previous_block))
                        if sad < best_sad:
                            best_sad = sad
                            best_dx, best_dy = dx, dy

                block_y, block_x = y // self.block_size, x // self.block_size
                motion_vectors[block_y, block_x, 0] = best_dx
                motion_vectors[block_y, block_x, 1] = best_dy

        return motion_vectors
    
    def get_predicted_frame(self,previous_frame, motion_vectors):
        height, width = previous_frame.shape
        predicted_frame = np.zeros_like(previous_frame)

        for block_y in range(height // self.block_size):
            for block_x in range(width // self.block_size):
                dx, dy = motion_vectors[block_y, block_x]
                start_y = block_y * self.block_size
                start_x = block_x * self.block_size
                end_y = start_y + self.block_size
                end_x = start_x + self.block_size

                predicted_frame[start_y:end_y, start_x:end_x] = previous_frame[start_y + dy:end_y + dy, start_x + dx:end_x + dx]

        return predicted_frame
    
    @staticmethod
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

    @staticmethod
    def add_differnce_frame(prev_frame, current_frame):

        current_frame.Y = np.clip(current_frame.Y + prev_frame.Y, 0,255)
        current_frame.Cr = np.clip(current_frame.Cr + prev_frame.Cr, 0,255)
        current_frame.Cb = np.clip(current_frame.Cb + prev_frame.Cb, 0,255)

        return current_frame