import numpy as np
import cv2
import sys, getopt

debug = False


def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rotation_matrix = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rotation_matrix, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def straighten(infile, outfile):
    # load image file
    image1 = cv2.imread(infile)

    width, height, _ = image1.shape

    if debug:
        image2 = image1.copy()
        if width > 2000:
            image2 = cv2.resize(image2, (0, 0), fx=0.15, fy=0.15)

    if width > 2000:
        downsize = cv2.resize(image1, (0, 0), fx=0.15, fy=0.15)
    else:
        downsize = image1

    # convert to greyscale
    gray = cv2.cvtColor(downsize, cv2.COLOR_BGR2GRAY)
    if debug:
        cv2.imwrite('grey.jpg', gray)

    # apply gaussian blur to reduce any noise
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    if debug:
        cv2.imwrite('blur.jpg', blur)

    # find the black/white threshold
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    if debug:
        cv2.imwrite('thresh.jpg', thresh)

    # find the edges using Canny edge detection
    canny_image = cv2.Canny(thresh, 100, 200, apertureSize=3)
    if debug:
        cv2.imwrite('canny.jpg', canny_image)

    # find the lines that make up the edges
    lines = cv2.HoughLines(canny_image, 1, np.pi/180.0, 250, np.array([]))
    for line in lines:
        rho, theta = line[0]
        if debug:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))

            cv2.line(image2, (x1, y1), (x2, y2), (0, 0, 255), 2)

    if debug:
        cv2.imwrite('houghlines.jpg', image2)

    # rotate the image by the angle of the last line
    if theta>1:
        image3 = rotate_image(image1, 180 * theta / np.pi - 90)
    else:
        image3 = rotate_image(image1, 180 * theta / np.pi)


    # write the rotated image to disk
    cv2.imwrite(outfile, image3)


def main(argv):
    input_file = ''
    output_file = ''

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('straighten.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('straighten.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg

    straighten(input_file, output_file)


if __name__ == "__main__":
    main(sys.argv[1:])
