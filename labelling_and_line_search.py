#!/usr/bin/env python3

import sys
from PIL import Image
import copy

line_search_width = 64

def load_image():
    if len(sys.argv)<2:
        print('Wrong amount of arguments.\nUsage: ./labelling.py [image_path]')
        exit()
    img1 = Image.open(sys.argv[1])
    return img1
    
def search_black(img1):
    lbl_list_1 = [ [0 for _ in range(img1.size[0])] for _ in range(img1.size[1]) ]
    lbl_img1 = Image.new('L', img1.size)
    max_lbl = 0
    used_lbls = []
    clusters = {}
    for y in range(img1.size[1]):
        print('Searching at y: '+str(y))
        for x in range(img1.size[0]):
            #pixels to compare to
            cmp_pixels = []
            if y > 0:
                cmp_pixels.append((x,y-1))
            if x > 0:
                cmp_pixels.append((x-1,y))
            continued_pixels = [] #pixels that are the similar color
            nearby_lbl_values = [] #label values of those
            for cmp_pixel in cmp_pixels:
                if (img1.getpixel(cmp_pixel)[0]-img1.getpixel((x,y))[0])**2 < 8**2:
                    if (img1.getpixel(cmp_pixel)[1]-img1.getpixel((x,y))[1])**2 < 8**2:
                        if (img1.getpixel(cmp_pixel)[2]-img1.getpixel((x,y))[2])**2 < 8**2:
                            continued_pixels.append((cmp_pixel))
                            nearby_lbl_values.append(lbl_list_1[cmp_pixel[1]][cmp_pixel[0]])
            #if for each numer of nearby pixels that are similar
            if len(continued_pixels)==0:
                lbl_list_1[y][x] = 0
            elif len(continued_pixels)==1:
                if nearby_lbl_values[0]==0:
                    max_lbl += 1
                    lbl_list_1[continued_pixels[0][1]][continued_pixels[0][0]] = max_lbl
                    lbl_list_1[y][x] = max_lbl
                    used_lbls.append(max_lbl)
                    clusters[str(max_lbl)] = 1
                else:
                    lbl_list_1[y][x] = nearby_lbl_values[0]
                    clusters[str(nearby_lbl_values[0])] += 1
            elif len(continued_pixels)==2:
                if nearby_lbl_values[0] == nearby_lbl_values[1] and not nearby_lbl_values[0] == 0:
                    lbl_list_1[y][x] = nearby_lbl_values[0]
                    clusters[str(nearby_lbl_values[0])] += 1
                elif nearby_lbl_values[0] == 0 and nearby_lbl_values[1] == 0:
                    max_lbl += 1
                    lbl_list_1[continued_pixels[0][1]][continued_pixels[0][0]] = max_lbl
                    lbl_list_1[continued_pixels[1][1]][continued_pixels[1][0]] = max_lbl
                    lbl_list_1[y][x] = max_lbl
                    clusters[str(max_lbl)] = 3
                    used_lbls.append(max_lbl)
                elif nearby_lbl_values[0] == 0 or nearby_lbl_values[1] == 0:
                    label = nearby_lbl_values[0] + nearby_lbl_values[1]
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
                        for t in range(img1.size[0]):
                            if lbl_list_1[s][t]==change_from:
                                lbl_list_1[s][t] = change_to
    to_be_removed = []
    for label in used_lbls:
        if clusters[str(label)] < 64:
            clusters.pop(str(label))
            to_be_removed.append(label)
    for label in to_be_removed:
        used_lbls.remove(label)
    for y in range(img1.size[1]):
        for x in range(img1.size[0]):
            if lbl_list_1[y][x] in to_be_removed:
                lbl_list_1[y][x] = 0
            elif lbl_list_1[y][x] != 0:
                lbl_list_1[y][x] = used_lbls.index(lbl_list_1[y][x])
    for y in range(img1.size[1]):
        for x in range(img1.size[0]):
            if not lbl_list_1[y][x]==0:
                lbl_img1.putpixel((x,y), 128+(8*lbl_list_1[y][x]%128))
    print('Number of clusters :'+str(len(used_lbls)))
    lbl_img1.show()

def search_lines(img1):
    lbl_list_1 = [ [0 for _ in range(img1.size[0])] for _ in range(img1.size[1]) ]
    p = 2
    break_while = False
    lines = []
    while not break_while:
        if p >= 62:
            print('End of line search')
            break
        for i in range(2,62):
            x1 = int(img1.size[0]*i/64)
            y1 = int(img1.size[1]*p/64)
            # x1 = int(img1.size[0]/(2**p) * (1+2*i))
            # y1 = int(img1.size[1]/(2**p) * (1+2*i))
            target_lbl = lbl_list_1[y1][x1]
            if target_lbl == 0:
                print('couldn\' anchor at {}: not in cluster'.format((x1,y1)))
                continue
            looking_for_anchor = True
            while looking_for_anchor:
                print('Looking for anchor edge point at x={} y={}'.format(x1,y1))
                if y1 == 0 or y1 == img1.size[1]-1:
                    looking_for_anchor = False
                elif lbl_list_1[y1+1][x1] == target_lbl:
                    y1 += 1
                else:
                    looking_for_anchor = False
            if y1 == 0 or y1 == img1.size[1]-1:
                print('couldn\' anchor at {}: hit top or bottom'.format((x1,y1)))
                continue
            edges = []
            for k in range(-line_search_width,line_search_width):
                print('Looking for edge at x='+str((x1+k, y1)))
                if k == 0:
                    edges.append((x1, y1))
                    continue
                ye = y1
                looking_for_edge = True
                while looking_for_edge:
                    if x1+k<0 or x1+k>=img1.size[0] or ye+1>=img1.size[1] or ye < 0:
                        print('No edge found'+str((x1+k,ye))+': x1 or ye out of range')
                        break
                    if lbl_list_1[ye][x1+k] == target_lbl:
                        if lbl_list_1[ye+1][x1+k] != target_lbl:
                            edges.append((x1+k, ye))
                            looking_for_edge = False
                        else:
                            ye +=1
                    else:
                        ye -= 1
            print('Edges are: '+str(edges))
            if len(edges) < line_search_width*2*0.8:
                print('Not enough edges found')
                continue
            xmean = sum([ edge[0] for edge in edges ]) / len(edges)
            ymean = sum([ edge[1] for edge in edges ]) / len(edges)
            sxx = sum([ (edge[0]-xmean)**2 for edge in edges ])/(len(edges)-1)
            sxy = sum([ (edge[0]-xmean)*(edge[1]-ymean) for edge in edges ])/(len(edges)-1)
            a = sxy / sxx - 1
            b = ymean - (a+1)*xmean
            diff = sum([ (edge[1]-(a+1)*edge[0]-b)**2 for edge in edges])
            if diff > line_search_width*2 * 4:
                continue
            lines.append((a,b,edges[0][0]))
            
        p += 1
    img1_with_line = img1
    for line in lines:
        for i in range(line_search_width):
            img1_with_line.putpixel((line[2]+i, int((line[0]+1)*(line[2]+i)+line[1])), (255,0,0))
    img1_with_line.show()

def main():
    img = load_image()
    search_black(img)
    search_lines(img)

if __name__=='__main__':
    main()
