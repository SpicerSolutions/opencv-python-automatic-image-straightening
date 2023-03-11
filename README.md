# opencv-python-automatic-image-straightening

The code uses opencv to detect the edges of an image and then rotate the image to straight.

The process is achieved using canny edge detection and hough lines. The resulting angle used to correct the rotation of the image.

usage:

python3 straighten.py -i "input file" -o "output file"
