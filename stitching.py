#!/usr/bin/env python3

import sys
import numpy
import time
import math
from PIL import Image

from convolution import *
from labelling_and_line_search import *
from flat_to_angular_data import *
from tilt import *


def smooth_func(rate):
    return math.sin((rate*2-1)*math.pi/2)/2+0.5

def load_image():
    print('** Loading images... **')
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
    img = []
    while k < image_to_merge:
        print('Image '+sys.argv[k+1]+' loaded.')
        img.append(Image.open(sys.argv[k+1]))
        #img_array.append(numpy.asarray(img[k].getdata()))
        if not k == 0 and not img[k].size[1] == img[k-1].size[1]:
            print('Images with different height is not supported')
            exit()
        k += 1
    # if len(sys.argv) == 5:
    #     min_diff = float(sys.argv[3])
    #     min_i = int(sys.argv[4])
    return image_to_merge, img

def stitch_image(img_l, img_r):
    img_array_l = numpy.asarray(img_l.getdata())
    img_array_r = numpy.asarray(img_r.getdata())
    min_diff = None
    min_i = None
    sml_width = min(img_l.size[0], img_r.size[0])
    #search_from = (abs(img_l.size[0]-img_r.size[0]) if not lazyMode else int(sml_width/3))
    #search_from = ( math.floor(img_l.size[0]/2) if img_l.size[0] <= img_r.size[0] else (img_l.size[0]-math.floor(img_r.size[0]/2)) )
    search_from = int(img_l.size[0]/3)
    search_to = img_l.size[0]
    print('Stitching...')
    print('='*math.floor((search_to-search_from)/10)+'|')
    #for i in range(search_from, img_l.size[0], 10):
    for i in range(search_from, search_to):
        if i % 10 == 0:
            print('|', end='', flush=True)
        total_diff = 0
        pixels_calculated = 0
        #for x in range(max(0, img_l.size[0]-i-math.floor(img_r.size[0]/6)), img_l.size[0]-i):
        for x in range(img_l.size[0]-i):
            if pixels_calculated > img_l.size[0]*20:
                break
            for y in range(img_l.size[1]):
                if pixels_calculated > img_l.size[0]*20:
                    break
                if numpy.sum(img_array_l[y*img_l.size[0]+x+i]) != 0 and numpy.sum(img_array_r[y*img_r.size[0]+x]) != 0:
                    total_diff += sum(numpy.absolute(numpy.subtract(img_array_l[y*img_l.size[0]+x+i], img_array_r[y*img_r.size[0]+x])))
                    pixels_calculated += 1
        #if pixels_calculated < img_l.size[0]*2:
        if pixels_calculated == 0:
            #print("Calculated pixels: {}Not enough pixels calculated".format(pixels_calculated))
            continue
        avrg_diff = total_diff/pixels_calculated
        if  min_diff == None or min_diff > avrg_diff:
            #print(str(min_diff)+' is bigger than '+str(avrg_diff))
            min_diff = avrg_diff
            min_i = i
    print('\nMinimum diff was '+str(min_diff)+' at i = '+str(min_i))
    print('')
    return min_diff, min_i

def output_image(img_l, img_r, min_diff, min_i):
    img_array_l = numpy.asarray(img_l.getdata())
    img_array_r = numpy.asarray(img_r.getdata())
    output_size = [ img_r.size[0] + min_i, img_l.size[1] ]
    output_array = [ 0 for _ in range(output_size[0]*output_size[1])]
    output_img = Image.new('RGB', tuple(output_size))
    for x in range(output_size[0]):
        if x < min_i:
            for y in range(img_l.size[1]):
                output_array[y*output_size[0]+x] = tuple(img_array_l[y*img_l.size[0]+x])
        elif x >= img_l.size[0]:
            for y in range(img_l.size[1]):
                output_array[y*output_size[0]+x] = tuple(img_array_r[y*img_r.size[0]+x-min_i])
        else:
            rate = smooth_func((x-min_i)/(img_l.size[0]-min_i))
            for y in range(img_l.size[1]):
                img1_pixel = [ math.floor(n * (1-rate)) for n in img_array_l[y*img_l.size[0]+x] ]
                img2_pixel = [ math.floor(n * rate) for n in img_array_r[y*img_r.size[0]+x-min_i] ]
                if numpy.sum(img_array_l[y*img_l.size[0]+x])==0:
                    output_array[y*output_size[0]+x] = tuple(img_array_r[y*img_r.size[0]+x-min_i])
                elif numpy.sum(img_array_r[y*img_r.size[0]+x-min_i])==0:
                    output_array[y*output_size[0]+x] = tuple(img_array_l[y*img_l.size[0]+x])
                elif numpy.sum(img_array_r[y*img_r.size[0]+x-min_i])==0 and numpy.sum(img_array_l[y*img_l.size[0]+x])==0:
                    output_array[y*output_size[0]+x] = (0,0,0)
                else:
                    output_array[y*output_size[0]+x] = tuple(numpy.add(img1_pixel, img2_pixel))
    output_img.putdata(output_array)
    #output_img.show()
    return output_img
    #img_array[j] = output_array

    
def skew(angle, img):
    output_img = Image.new('RGB', img.size)
    angle_rate = math.tan(angle)
    print('='*math.floor(img.size[0]/10)+'|')
    for x in range(math.floor(img.size[0])):
        #print('now working on x = '+str(x))
        if x % 10 == 0:
            print('|', end='', flush=True)
        x_rate = 1 - x / (img.size[0]/2) if x > img.size[0]/2 else  x / (img.size[0]/2) - 1
        shrink_rate = 1 / (1+angle_rate**2*x_rate**2) **2
        #print('shrink rate is '+str(shrink_rate))
        #print(shrink_rate*img.size[1])
        for y in range(img.size[1]):
            #print('now working on y = '+str(y))
            if abs(y) >= abs(shrink_rate*(img.size[1]-1)):
                y_offset = int((img.size[1] - img.size[1] * shrink_rate) / 2)
                #output_img.putpixel((x, y+y_offset), (0, 0, 0))
            else:
                #print(y/shrink_rate)
                y_floor = math.floor(y/shrink_rate)
                floor_pixel = img.getpixel((x, y_floor))
                ceil_pixel = img.getpixel((x, y_floor+1))
                result_pixel = numpy.divide(numpy.add(floor_pixel, ceil_pixel), (2, 2 , 2))
                result_pixel = [ int(n) for n in result_pixel ]
                y_offset = int((img.size[1] - img.size[1] * shrink_rate) / 2)
                #print(y_offset)
                output_img.putpixel((x, y+y_offset), tuple(result_pixel))
                #new_image[y][x] = old_image[math.floor(y/shrink_rate)][x] + old_image[math.ceil(y/shrink_rate)][x]
    #output_img.show()
    print('')
    return output_img

def stitch_crude_vh(vh0, vh1):
    shift = math.atan(270/816)
    vh_img_0 = crude_draw_vh(vh0, -shift)
    vh_img_1 = crude_draw_vh(vh1, shift)
    min_diff, min_i = stitch_image(vh_img_0, vh_img_1)
    output = output_image(vh_img_0, vh_img_1, min_diff, min_i)
    output.show()
    
def main():

    image_to_merge, img = load_image()
    img_exif0 = dict(img[0].getexif())
    img_exif1 = dict(img[1].getexif())
    img[0], img[1] = exposure_adjust(img[0], img[1])
    # vh_0 = xy_img2vh_img(img[0], img_exif0)
    # vh_1 = xy_img2vh_img(img[1], img_exif1)
    # new_vh = merge_vh(vh_0, vh_1, math.atan(280/816))
    # new_img = Image.new('RGB', (img[0].size[0], img[0].size[1]))
    # draw_vh(new_vh, new_img, img_exif0)
    # img[0] = draw_vh(vh_0, img[0], img_exif0, math.atan(120/816))
    # img[1] = draw_vh(vh_1, img[1], img_exif1, -math.atan(120/816))
    
    pixel_points_0, vh_points_0 = flat_to_angular(img[0], img_exif0)
    print()
    pixel_points_1,vh_points_1 = flat_to_angular(img[1], img_exif1)

    #stitch_crude_vh(vh_points_0, vh_points_1)

    overall_min_i = 0
    overall_min_diff = None
    best_shift = 0
    
    shift = math.atan(280/816)
    img[0] = draw_ver_hor_img(vh_points_0, img[0], img_exif0, -shift)
    img[1] = draw_ver_hor_img(vh_points_1, img[1], img_exif1, shift)
    min_diff, min_i = stitch_image(img[0], img[1])
    print(min_diff, min_i)
    output = output_image(img[0], img[1], min_diff, min_i)
    output.show()
    
    # img[0] = draw_ver_hor_img(vh_points_0, img[0], img_exif0, -best_shift)
    # img[1] = draw_ver_hor_img(vh_points_1, img[1], img_exif1, best_shift)
    # output = output_image(img[0], img[1], overall_min_diff, overall_min_i)
    # output.show()

if __name__=='__main__':
    main()
