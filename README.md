# Video-Codec
EN5502 MEng Coursework for video encoding and decoding.


This code is designed to show how a video coding algorithm is implemented from the ground up, I am aware that it is horrifically inefficient and should under no circumstances ever be used, ever.

The basic Process is:

- Feed in video sequence
- Perform motion compensation
- Take DCT of frame
- Quantize frame
- Encode and save to file (Optional and unfinished)
- Inverse Quantize frame
- Take IDCT of frame
- Perform motion compensation on reconstructed frame

Done! You will have ruined a perfectly good video...

Never got to fully finish the algorithm as it doesn’t properly decode the binary information fully. It is incredible to see how much space can be saved with some simple compression however!
