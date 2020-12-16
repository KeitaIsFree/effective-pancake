#!/usr/bin/env python3

from PIL import Image
import sys
import math
import numpy

img_list = []
result = []
selected_kernel = {}
result_img = None

values = 'values'
adjust = 'adjust'
size = 'size'
edge = 'edge'
only_brightness = 'only_brightness'

ANGLE_DIFF_THRESHOLD = math.pi / 8

SOBEL_KERNEL = {
    'values': [
        [ [ 1, 0, -1 ],
          [ 2, 0, -2 ],
          [ 1, 0, -1 ] ],
        [ [ 1, 2, 1 ],
          [ 0, 0, 0 ],
          [-1, -2, -1 ] ],
    ],
    'adjust': None, #Number to divide by to adjust value, None if not to be adjusted
    'size': (3, 3),
    'edge': [ [ 0, 0, 0 ],  #For non existing pixels at edges,
            [ 0, 0, 0 ],  #use this*center_pixel
            [ 0, 0, 0 ] ],
    'only_brightness': True   #If calculate using brightness and not for each channel, True
}

GAUSSIAN_KERNEL = {
    'values': [
        [ [ 2, 4, 5, 4, 2 ],
          [ 4, 9, 12, 9, 4 ],
          [ 5, 12, 15, 12, 5],
          [ 4, 9, 12, 9, 4 ],
          [ 2, 4, 5, 4, 2 ] ],
    ],
    'size': (5, 5),
    'adjust': 155,
    'edge': [ [ 2, 4, 5, 4, 2 ],
            [ 4, 9, 12, 9, 4 ],
            [ 5, 12, 15, 12, 5],
            [ 4, 9, 12, 9, 4 ],
            [ 2, 4, 5, 4, 2 ] ],
    'only_brightness': False
}

def load_image():
    global img_list, selected_kernel, result_img
    if len(sys.argv)<3:
        print('Wrong amount of arguments.\nUsage: ./labelling.py [-g (for Gaussian) or -s (for sobel) [image_path]')
        exit()
    if sys.argv[1] == '-g':
        selected_kernel.update(GAUSSIAN_KERNEL)
    elif sys.argv[1] == '-s':
        selected_kernel.update(SOBEL_KERNEL)
    else:
        print('Kernel doesn\'t exist for '+argv[1])
        exit()
    img = Image.open(sys.argv[2])
    img_list_flat = list(img.getdata())
    for i in range(img.size[1]):
        img_list.append(img_list_flat[i * img.size[0]: (i+1) * img.size[0] ])
    #print(img_list[0][0:16])
    if selected_kernel[only_brightness]:
        result_img = Image.new('L', (img.size[0], img.size[1]))
    else:
        result_img = Image.new('RGB', (img.size[0], img.size[1]))

def apply_filter(img, kernel = selected_kernel):
    #global result, result_img
    #print('Applying filter with +'+str(kernel)+' to '+str(data_list[0:16]))
    result = [ 0 for _ in range(img.size[0]*img.size[1])]
    result_img = Image.new('RGB', (img.size[0], img.size[1]))
    img_array = numpy.asarray(img.getdata())
    print('='*math.floor(img.size[1]/10)+'|')
    for y in range(img.size[1]):
        if y % 10 == 0:
            print('|', end='', flush=True)
        for x in range(img.size[0]):
            #print('looking at x,y: '+str((x,y)))
            diff = int(kernel[size][0]/2-0.5)
            if diff <= x < img.size[0]-diff and diff <= y < img.size[1]-diff:
                pixels_in_range = [ [ img_array[y*img.size[0]+x] for kx in range(x-diff, x+diff+1) ] for ky in range(y-diff, y+diff+1) ]
            else:
                pixels_in_range = [ [ [1] for _ in range(kernel[size][0]) ] for _ in range(kernel[size][1]) ]
                for yk in range(kernel[size][1]):
                    if not 0 <= y+yk-diff < img.size[1]:
                        pixels_in_range[yk] = [ img_array[ y*img.size[0]+x ] for _ in range(kernel[size][0]) ]
                    else:
                        for xk in range(kernel[size][0]):
                            if 0 <= x+xk-diff < img.size[0]:
                                pixels_in_range[yk][xk] = img_array[(y+yk-diff)*img.size[0]+(x+xk-diff)]
                            else:
                                pixels_in_range[yk][xk] = img_array[y*img.size[0]+x]
            #print('kernel is '+str(kernel))
            #if kernel[only_brightness]:
            if not len(kernel[values]) == 1:  #if kernel has common kernel for x and y
                total = [0, 0]
                for yk in range(kernel[size][1]):
                    for xk in range(kernel[size][0]):
                        #print('adding '+str(pixels_in_range[yk][xk])+' times '+str(kernel[values][0][yk][xk]))
                        total[0] += sum(pixels_in_range[yk][xk])/3*kernel[values][0][yk][xk]
                for yk in range(kernel[size][1]):
                    for xk in range(kernel[size][0]):
                        #print('adding '+str(pixels_in_range[yk][xk])+' times '+str(kernel[values][0][yk][xk]))
                        total[1] += sum(pixels_in_range[yk][xk])/3*kernel[values][1][yk][xk]
                    #if kernel[adjust] != None:
                    #    total = total/kernel[adjust]
                value = math.sqrt(total[0]**2+total[1]**2)
                if not total[0] == 0:
                    angle = math.atan(total[1]/total[0])
                elif total[1]==0:
                    angle = math.atan(1)
                else:
                    angle = math.atan(1000000)
                result[y][x] = {
                    'value': value,
                    'angle': angle,
                }
                result_img.putpixel((x,y), int(math.sqrt(total[0]**2+total[1]**2)))
            else:
                total = [0, 0, 0]
                for yk in range(kernel[size][1]):
                    for xk in range(kernel[size][0]):
                        #print('adding '+str(pixels_in_range[yk][xk])+' times '+str(kernel[values][0][yk][xk]))
                        total[0] += pixels_in_range[yk][xk][0]*kernel[values][0][yk][xk]
                        total[1] += pixels_in_range[yk][xk][1]*kernel[values][0][yk][xk]
                        total[2] += pixels_in_range[yk][xk][2]*kernel[values][0][yk][xk]
                if kernel[adjust] != None:
                    total[0] = int(total[0]/kernel[adjust])
                    total[1] = int(total[1]/kernel[adjust])
                    total[2] = int(total[2]/kernel[adjust])
                #result[y][x] = abs(total)
                #print('putting '+ str((total[0], total[1], total[2]))+'at '+str((x,y)))
                result_img.putpixel((x,y), (total[0], total[1], total[2]))
                result[y*img.size[0]+x] = (total[0], total[1], total[2])
    print('')
    return result, result_img

def label():
    global result, img_list
    lbl_list_1 = [ [0 for _ in range(len(img_list[0]))] for _ in range(len(img_list[1])) ]
    lbl_img1 = Image.new('L', (len(img_list[0]), len(img_list)))
    max_lbl = 0
    used_lbls = []
    clusters = {}
    for y in range(len(img_list)):
        print('Searching at y: '+str(y))
        for x in range(len(img_list[0])):
            if result[y][x]["value"] < 250:
                continue
            #pixels to compare to
            cmp_pixels = []
            if y > 0:
                cmp_pixels.append((x,y-1))
            if x > 0:
                cmp_pixels.append((x-1,y))
            continued_pixels = [] #pixels that are the similar color
            continued_lbl_values = [] #label values of those
            for cmp_pixel in cmp_pixels:
                if -ANGLE_DIFF_THRESHOLD < result[cmp_pixel[1]][cmp_pixel[0]]["angle"] - result[y][x]["angle"] < ANGLE_DIFF_THRESHOLD:
                    continued_pixels.append((cmp_pixel))
                    continued_lbl_values.append(lbl_list_1[cmp_pixel[1]][cmp_pixel[0]])
            #if for each numer of nearby pixels that are similar
            if len(continued_pixels)==0:
                lbl_list_1[y][x] = 0
            elif len(continued_pixels)==1:
                if continued_lbl_values[0]==0:
                    max_lbl += 1
                    lbl_list_1[continued_pixels[0][1]][continued_pixels[0][0]] = max_lbl
                    lbl_list_1[y][x] = max_lbl
                    used_lbls.append(max_lbl)
                    clusters[str(max_lbl)] = 1
                else:
                    lbl_list_1[y][x] = continued_lbl_values[0]
                    clusters[str(continued_lbl_values[0])] += 1
            elif len(continued_pixels)==2:
                if continued_lbl_values[0] == continued_lbl_values[1] and not continued_lbl_values[0] == 0:
                    lbl_list_1[y][x] = continued_lbl_values[0]
                    clusters[str(continued_lbl_values[0])] += 1
                elif continued_lbl_values[0] == 0 and continued_lbl_values[1] == 0:
                    max_lbl += 1
                    lbl_list_1[continued_pixels[0][1]][continued_pixels[0][0]] = max_lbl
                    lbl_list_1[continued_pixels[1][1]][continued_pixels[1][0]] = max_lbl
                    lbl_list_1[y][x] = max_lbl
                    clusters[str(max_lbl)] = 3
                    used_lbls.append(max_lbl)
                elif continued_lbl_values[0] == 0 or continued_lbl_values[1] == 0:
                    label = continued_lbl_values[0] + continued_lbl_values[1]
                    lbl_list_1[continued_pixels[0][1]][continued_pixels[0][0]] = label
                    lbl_list_1[continued_pixels[1][1]][continued_pixels[1][0]] = label
                    lbl_list_1[y][x] = label
                    clusters[str(label)] += 2
                else :
                    lbl_list_1[y][x] = lbl_list_1[continued_pixels[0][1]][continued_pixels[0][0]]
                    #All pixels with the same label as (x-1,y) must be changed to the same label as (x,y-1)
                    change_from = lbl_list_1[continued_pixels[1][1]][continued_pixels[1][0]]
                    used_lbls.remove(change_from)
                    change_to = lbl_list_1[continued_pixels[0][1]][continued_pixels[0][0]]
                    clusters[str(change_to)] += (clusters[str(change_from)] + 1)
                    clusters.pop(str(change_from))
                    for s in range(y+1):
                        for t in range(len(img_list[0])):
                            if lbl_list_1[s][t]==change_from:
                                lbl_list_1[s][t] = change_to
    to_be_removed = []
    for label in used_lbls:
        if clusters[str(label)] < 256:
            clusters.pop(str(label))
            to_be_removed.append(label)
    for label in to_be_removed:
        used_lbls.remove(label)
    for y in range(len(img_list[1])):
        for x in range(len(img_list[0])):
            if lbl_list_1[y][x] in to_be_removed:
                lbl_list_1[y][x] = 0
            elif lbl_list_1[y][x] != 0:
                lbl_list_1[y][x] = used_lbls.index(lbl_list_1[y][x])
    for y in range(len(img_list[1])):
        for x in range(len(img_list[0])):
            if not lbl_list_1[y][x]==0:
                lbl_img1.putpixel((x,y), 255)
    print('Number of clusters :'+str(len(used_lbls)))
    lbl_img1.show()

def show():
    global result_img
    result_img.show()
                
def main():
    load_image()
    apply_filter()
    label()
    show()

if __name__=='__main__':
    main()
