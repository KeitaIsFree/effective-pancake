#!/usr/bin/env python3

from PIL import Image
import sys
import math

img_list = []
result = []
selected_kernel = {}
result_img = None

values = 'values'
adjust = 'adjust'
size = 'size'
edge = 'edge'
only_brightness = 'only_brightness'

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

def apply_filter(kernel = selected_kernel, data_list = img_list):
    global result, result_img
    print('Applying filter with +'+str(kernel)+' to '+str(data_list[0:16]))
    result = [ [ [0] for _ in range(len(data_list[0])) ] for _ in range(len(data_list)) ]
    for y in range(len(data_list)):
        for x in range(len(data_list[0])):
            print('looking at x,y: '+str((x,y)))
            diff = int(kernel[size][0]/2-0.5)
            if diff <= x < len(data_list[0])-diff and diff <= y < len(data_list)-diff:
                data_list_in_use = [ row[x-diff: x+diff+1] for row in data_list[y-diff: y+diff+1] ]
            else:
                data_list_in_use = [ [ [1] for _ in range(kernel[size][0]) ] for _ in range(kernel[size][1]) ]
                for yk in range(kernel[size][1]):
                    if not 0 <= y+yk-diff < len(data_list):
                        data_list_in_use[yk] = [ data_list[y][x] for _ in range(kernel[size][0]) ]
                    else:
                        for xk in range(kernel[size][0]):
                            if 0 <= x+xk-diff < len(data_list[0]):
                                data_list_in_use[yk][xk] = data_list[y+yk-diff][x+xk-diff]
                            else:
                                data_list_in_use[yk][xk] = data_list[y][x]
            print('kernel is '+str(kernel))
            #if kernel[only_brightness]:
            if True:
                if not len(kernel[values]) == 1:  #if kernel has common kernel for x and y
                    total = [0, 0]
                    for yk in range(kernel[size][1]):
                        for xk in range(kernel[size][0]):
                            print('adding '+str(data_list_in_use[yk][xk])+' times '+str(kernel[values][0][yk][xk]))
                            total[0] += sum(data_list_in_use[yk][xk])/3*kernel[values][0][yk][xk]
                    for yk in range(kernel[size][1]):
                        for xk in range(kernel[size][0]):
                            print('adding '+str(data_list_in_use[yk][xk])+' times '+str(kernel[values][0][yk][xk]))
                            total[1] += sum(data_list_in_use[yk][xk])/3*kernel[values][1][yk][xk]
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
                            print('adding '+str(data_list_in_use[yk][xk])+' times '+str(kernel[values][0][yk][xk]))
                            total[0] += data_list_in_use[yk][xk][0]*kernel[values][0][yk][xk]
                            total[1] += data_list_in_use[yk][xk][1]*kernel[values][0][yk][xk]
                            total[2] += data_list_in_use[yk][xk][2]*kernel[values][0][yk][xk]
                    if kernel[adjust] != None:
                        total[0] = int(total[0]/kernel[adjust])
                        total[1] = int(total[1]/kernel[adjust])
                        total[2] = int(total[2]/kernel[adjust])
                    #result[y][x] = abs(total)
                    print('putting '+ str((total[0], total[1], total[2]))+'at '+str((x,y)))
                    result_img.putpixel((x,y), (total[0], total[1], total[2]))
                    result[y][x] = (total[0], total[1], total[2])
    return result

def show():
    global result_img
    result_img.show()
                
def main():
    load_image()
    apply_filter()
    show()

if __name__=='__main__':
    main()
