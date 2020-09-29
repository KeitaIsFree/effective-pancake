#!/usr/bin/env python3

import sys
import numpy
import time
import math
from PIL import Image

j = None

img = []
img_array = []

min_diff = None
min_i = None

lazyMode = True

image_to_merge = None
merges = 0

def smooth_func(rate):
    return math.sin((rate*2-1)*math.pi/2)/2+0.5

def load_image():
    global img, img_array, min_diff, min_i, lazyMode, image_to_merge
    if len(sys.argv) < 3:
        print('Wrong amount of arguments.')
        print('Usage: ./labelling.py [image_path_1]  [image_path_2]')
        exit()
    #if sys.argv[1] == '--disable-lazy':
    lazyMode = False
    # img1 = Image.open(sys.argv[2])
    # img[1] = Image.open(sys.argv[3])
    # else:
    #     print('Running in lazy mode; assuming overlap is less than two thirds of the width...')
    image_to_merge = len(sys.argv)-1
    k = 0
    while k < image_to_merge:
        img.append(Image.open(sys.argv[k+1]))
        img_array.append(numpy.asarray(img[k].getdata()))
        if not k == 0 and not img[k].size[1] == img[k-1].size[1]:
            print('Images with different height is not supported')
            exit()
        k += 1
    # if len(sys.argv) == 5:
    #     min_diff = float(sys.argv[3])
    #     min_i = int(sys.argv[4])
    

def stitch_image():
    global img, img_array, min_diff, min_i
    min_diff = None
    min_i = None
    sml_width = min(img[j].size[0], img[j+1].size[0])
    #search_from = (abs(img[j].size[0]-img[j+1].size[0]) if not lazyMode else int(sml_width/3))
    search_from = ( 0 if img[j].size[0] < img[j+1].size[0] else (img[j].size[0]-img[j+1].size[0]) )
    for i in range(search_from, img[j].size[0]):
        print('Trying i = '+str(i))
        total_diff = 0
        columns_calculated = 0
        for x in range(max(0, img[j].size[0]-i-math.floor(img[j+1].size[0]/6)), img[j].size[0]-i):
            for y in range(img[j].size[1]):
                total_diff += sum(numpy.absolute(numpy.subtract(img_array[j][y*img[j].size[0]+x+i], img_array[j+1][y*img[j+1].size[0]+x])))
            columns_calculated += 1
        avrg_diff = total_diff/columns_calculated
        if  min_diff == None or min_diff > avrg_diff:
            print(str(min_diff)+' is bigger than '+str(avrg_diff))
            min_diff = avrg_diff
            min_i = i
    print('Minimum diff was '+str(min_diff)+' at i = '+str(min_i))

def output_image():
    global img, img_array
    output_size = [ img[j+1].size[0] + min_i, img[j].size[1] ]
    output_array = [ 0 for _ in range(output_size[0]*output_size[1])]
    output_img = Image.new('RGB', tuple(output_size))
    for x in range(output_size[0]):
        if x < min_i:
            for y in range(img[j].size[1]):
                output_array[y*output_size[0]+x] = tuple(img_array[j][y*img[j].size[0]+x])
        elif x >= img[j].size[0]:
            for y in range(img[j].size[1]):
                output_array[y*output_size[0]+x] = tuple(img_array[j+1][y*img[j+1].size[0]+x-min_i])
        else:
            rate = smooth_func((x-min_i)/(img[j].size[0]-min_i))
            for y in range(img[j].size[1]):
                img1_pixel = [ math.floor(n * (1-rate)) for n in img_array[j][y*img[j].size[0]+x] ]
                img2_pixel = [ math.floor(n * rate) for n in img_array[j+1][y*img[j+1].size[0]+x-min_i] ]
                output_array[y*output_size[0]+x] = tuple(numpy.add(img1_pixel, img2_pixel))
    output_img.putdata(output_array)
    output_img.show()
    img[j+1] = output_img
    img_array[j+1] = output_array
    
def main():
    global merges, image_to_merge, j
    load_image()
    while merges < image_to_merge-1:
        j = merges
        # if not len(sys.argv) == 5 : 
        stitch_image()
        output_image()
        merges += 1

if __name__=='__main__':
    main()
