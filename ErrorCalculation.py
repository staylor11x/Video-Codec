'''
    Class to handle error calcs
'''

import numpy as np

class ErrorCalculation():

    @staticmethod
    def calculate_psnr(video1, video2):
        # Ensure video dimensions are the same
        assert video1.shape == video2.shape, "Video dimensions must be the same."

        # Calculate MSE (Mean Squared Error)
        mse = np.mean((video1 - video2) ** 2)

        # Calculate the maximum pixel value
        max_pixel_value = np.max(video1)

        # Calculate PSNR using the formula: PSNR = 20 * log10(MAX) - 10 * log10(MSE)
        psnr = 20 * np.log10(max_pixel_value) - 10 * np.log10(mse)

        return psnr
