#!/usr/bin/env python3

import sys
import numpy
import time
import math
from PIL import Image


def smooth_func(rate):
    return math.sin((rate*2-1)*math.pi/2)/2+0.5

def load_image():
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
    search_from = ( math.floor(img_l.size[0]/2) if img_l.size[0] < img_r.size[0] else (img_l.size[0]-math.floor(img_r.size[0]/2)) )
    print('-'*int((img_l.size[0]-search_from)/10)+'|')
    for i in range(search_from, img_l.size[0]):
        if i % 10 == 0:
            print('|', end='', flush=True)
        total_diff = 0
        pixels_calculated = 0
        for x in range(max(0, img_l.size[0]-i-math.floor(img_r.size[0]/6)), img_l.size[0]-i):
            for y in range(img_l.size[1]):
                if numpy.sum(img_array_l[y*img_l.size[0]+x+i]) != 0 or numpy.sum(img_array_r[y*img_r.size[0]+x]) != 0:
                    total_diff += sum(numpy.absolute(numpy.subtract(img_array_l[y*img_l.size[0]+x+i], img_array_r[y*img_r.size[0]+x])))
                    pixels_calculated += 1
        avrg_diff = total_diff/pixels_calculated
        if  min_diff == None or min_diff > avrg_diff:
            #print(str(min_diff)+' is bigger than '+str(avrg_diff))
            min_diff = avrg_diff
            min_i = i
    #print('Minimum diff was '+str(min_diff)+' at i = '+str(min_i))
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
                output_array[y*output_size[0]+x] = tuple(numpy.add(img1_pixel, img2_pixel))
    output_img.putdata(output_array)
    #output_img.show()
    return output_img
    #img_array[j] = output_array

    
def skew(angle, img):
    output_img = Image.new('RGB', img.size)
    angle_rate = math.tan(angle)
    print('-'*int(img.size[0]/10)+'|')
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

    
def main():
    #TODO: image_to_merge
    image_to_merge = 2
    merges = 0
    j = None
    image_to_merge, img = load_image()
    while merges < image_to_merge-1:
        j = merges
        # if not len(sys.argv) == 5 :
        best_img = None
        best_diff = None
        for angle in range(10, 15):
            print('Attempting with theta = '+str(angle)+' degrees')
            angle *= math.pi / 180
            skew_img_l = skew(angle, img[j]) if j == 0 else img[j]
            skew_img_r = skew(angle, img[j+1])
            min_diff, min_i = stitch_image(skew_img_l, skew_img_r)
            new_img = output_image(skew_img_l, skew_img_r, min_diff, min_i)
            if best_diff==None or min_diff<best_diff:
                best_img = new_img
                best_diff = min_diff
        img[j+1] = best_img
        merges += 1
    img[merges].show()

if __name__=='__main__':
    main()
