#!/usr/bin/env python3

import sys
import numpy
import time
import math
from PIL import Image

img1 = None
img2 = None

img1_array = None
img2_array = None

min_diff = None
min_i = None

lazyMode = True

image_merged = 0
image_to_merge = None

def smooth_func(rate):
    return math.sin((rate*2-1)*math.pi/2)/2+0.5

def load_image():
    global img1, img2, img1_array, img2_array, min_diff, min_i, lazyMode, image_to_merge
    if len(sys.argv) < 3:
        print('Wrong amount of arguments.')
        print('Usage: ./labelling.py [image_path_1]  [image_path_2]')
        exit()
    #if sys.argv[1] == '--disable-lazy':
    lazyMode = False
    # img1 = Image.open(sys.argv[2])
    # img2 = Image.open(sys.argv[3])
    # else:
    #     print('Running in lazy mode; assuming overlap is less than two thirds of the width...')
    image_to_merge = len(sys.argv)-1
    img1 = Image.open(sys.argv[1])
    img2 = Image.open(sys.argv[2])
    img1_array = numpy.asarray(img1.getdata())
    img2_array = numpy.asarray(img2.getdata())
    # if len(sys.argv) == 5:
    #     min_diff = float(sys.argv[3])
    #     min_i = int(sys.argv[4])
    if not img1.size[1] == img2.size[1]:
        print('Images with different height is not supported')
        exit()

def stitch_image():
    global img1_array, img2_array, min_diff, min_i
    min_diff = None
    min_i = None
    sml_width = min(img1.size[0], img2.size[0])
    #search_from = (abs(img1.size[0]-img2.size[0]) if not lazyMode else int(sml_width/3))
    search_from = ( 0 if img1.size[0] < img2.size[0] else (img1.size[0]-img2.size[0]) )
    for i in range(search_from, img1.size[0]):
        print('Trying i = '+str(i))
        total_diff = 0
        for x in range(img1.size[0]-i):
            for y in range(img1.size[1]):
                total_diff += sum(numpy.absolute(numpy.subtract(img1_array[y*img1.size[0]+x+i], img2_array[y*img2.size[0]+x])))
        avrg_diff = total_diff/(img1.size[0]-i)
        if  min_diff == None or min_diff > avrg_diff:
            print(str(min_diff)+' is bigger than '+str(avrg_diff))
            min_diff = avrg_diff
            min_i = i
    print('Minimum diff was '+str(min_diff)+' at i = '+str(min_i))

def output_image():
    output_size = [ img2.size[1] + min_i, img1.size[1] ]
    output_array = [ 0 for _ in range(output_size[0]*output_size[1])]
    output_img = Image.new('RGB', tuple(output_size))
    for x in range(output_size[0]):
        if x < min_i:
            for y in range(img1.size[1]):
                output_array[y*output_size[0]+x] = tuple(img1_array[y*img1.size[0]+x])
        elif x >= img1.size[0]:
            for y in range(img1.size[1]):
                output_array[y*output_size[0]+x] = tuple(img2_array[y*img2.size[0]+x-min_i])
        else:
            rate = smooth_func((x-min_i)/(img1.size[0]-min_i))
            for y in range(img1.size[1]):
                img1_pixel = [ math.floor(n * (1-rate)) for n in img1_array[y*img1.size[0]+x] ]
                img2_pixel = [ math.floor(n * rate) for n in img2_array[y*img2.size[0]+x-min_i] ]
                output_array[y*output_size[0]+x] = tuple(numpy.add(img1_pixel, img2_pixel))
    output_img.putdata(output_array)
    output_img.show()
    
def main():
    while image_merged < image_to_merge:
    load_image()
    #if not len(sys.argv) == 5 :
    stitch_image()
    output_image()

if __name__=='__main__':
    main()
