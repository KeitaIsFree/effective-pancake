#!/usr/bin/env python3

import sys, math, numpy
from PIL import Image, ExifTags

def load_image():
    print('** Loading image... **')
    if len(sys.argv) != 2:
        print('Wrong amount of arguments.')
        print('Usage: ./flat-to-angular-data.py [image_path]')
        exit()
    img = Image.open(sys.argv[1])
    print('** Image loaded. **')
    return img

def interpolate(img, flatX, flatY):
    flatX += img.size[0]/2
    flatY += img.size[1]/2
    pixel_sum = [0, 0, 0]
    for y in [math.floor(flatY), math.ceil(flatY)]:
        for x in [math.floor(flatX), math.ceil(flatX)]:
            pixel_sum = numpy.add(pixel_sum, img.getpixel((x,y)))
    result = [ math.floor(dat/4) for dat in pixel_sum ]
    return tuple(result)

def exposure_adjust(img1, img2):
    img1_exif = dict(img1.getexif())
    img2_exif = dict(img2.getexif())
    for key, value in img1_exif.items():
        if ExifTags.TAGS.get(key) == 'ExposureTime':
            exposure_time_1 = value      
        if ExifTags.TAGS.get(key) == 'FNumber':
            f_number_1 = value
    for key, value in img2_exif.items():
        if ExifTags.TAGS.get(key) == 'ExposureTime':
            exposure_time_2 = value      
        if ExifTags.TAGS.get(key) == 'FNumber':
            f_number_2 = value
    print('Image taking conditions:\nImage 1 exposure: {} f_number: {}'.format(exposure_time_1, f_number_1))
    print('Image 2 exposure: {} f_number: {}'.format(exposure_time_2, f_number_2))
    f_index_1 = [1.4, 2, 2.8, 4, 5.6, 8, 11, 16, 22, 32].index(int(f_number_1))
    f_index_2 = [1.4, 2, 2.8, 4, 5.6, 8, 11, 16, 22, 32].index(int(f_number_2))
    if exposure_time_1 / 2**f_index_1 > exposure_time_2 / 2**f_index_2:
        diff = (exposure_time_1 / 2**f_index_1) / (exposure_time_2 / 2**f_index_2)
        ## REMOVE
        # diff = 2.5
        print('exposure diff: ', diff)
        new_img2 = Image.new('RGB', img2.size)
        for y in range(img2.size[1]):
            for x in range(img2.size[0]):
                adj_data = numpy.multiply(img2.getpixel((x,y)), (diff, diff, diff))
                adj_data = [ (int(data) if int(data) < 255 else 255) for data in adj_data ]
                new_img2.putpixel((x,y), tuple(adj_data))
        img2 = new_img2
    else:
        diff = (exposure_time_2 / 2**f_index_2) / (exposure_time_1 / 2**f_index_1)
        ## REMOVE 
        # diff = 2.5
        print('exposure diff: ', diff)
        new_img1 = Image.new('RGB', img1.size)
        for y in range(img1.size[1]):
            for x in range(img1.size[0]):
                adj_data = numpy.multiply(img1.getpixel((x,y)), (diff, diff, diff))
                adj_data = [ (int(data) if int(data) < 255 else 255) for data in adj_data ]
                new_img1.putpixel((x,y), tuple(adj_data))
        img1 = new_img1
    img1.show()
    img2.show()
    return img1, img2

def flat_to_angular(img, img_exif):
    # img_exif = dict(img.getexif())
    #focal length assuming a 35mm film
    for key, value in img_exif.items():
        if ExifTags.TAGS.get(key) == 'FocalLengthIn35mmFilm':
            focal_length_35 = value       
    diag_pixels = math.sqrt(img.size[0]**2 + img.size[1]**2)
    #fraction of one pixel on sensor to focal length
    pixel_to_focal_length = 35 / diag_pixels / focal_length_35 
    focal_len_in_pixels = diag_pixels*focal_length_35/35
    print('focal_len_in_pixels: {}'.format(focal_len_in_pixels))
    #print(pixel_to_focal_length*3264)
    pixel_points = []
    ver_hor_points = []
    print('='*int(img.size[1]/50), end='')
    print('|')
    for y in range(img.size[1]):
        if y%50==0:
            print('-', end='', flush=True)
        #angY = math.atan(pixel_to_focal_length * (y-img.size[1]/2))
        for x in range(img.size[0]):
            #angX = math.atan(pixel_to_focal_length * (x-img.size[0]/2))
            #converting to kyokuzahyou
            r = math.sqrt((x-img.size[0]/2)**2 + (y-img.size[1]/2)**2)
            theta = math.atan2(y-img.size[1]/2, x-img.size[0]/2)
            ang_r = focal_len_in_pixels*math.sin(math.atan(pixel_to_focal_length * r))
            #alpha = math.atan(pixel_to_focal_length*r)
            alpha = math.atan(r / focal_len_in_pixels)
            # checked #########################################
            ver = math.asin(math.sin(alpha) * math.sin(theta))
            hor = math.asin(math.sin(alpha) * math.cos(theta))
            ###################################################
            ver_hor_points.append({'ver': ver, 'hor': hor, 'data': img.getpixel((x,y))})
            
            pixel_points.append({'pos': (ang_r, theta), 'data': img.getpixel((x,y))})
            #print('(x,y): ({},{}) (ver,hor): ({},{})'.format(x, y, ver, hor))
    return pixel_points, ver_hor_points

def crude_draw_vh(vh, shift = 0):
    new_img = Image.new('RGB', (400, 400))
    for point in vh:
        adjusted_hor = point['hor'] + math.asin(math.cos(point['ver'])*math.sin(shift))
        x = int(400*adjusted_hor + 200)
        y = int(400*point['ver'] + 200)
        if x > 0 and x < 400:
            if y > 0 and y < 400:
                new_img.putpixel((x, y), point['data'])
    new_img.show()
    return new_img

def merge_vh_points(vh_l, vh_r, shift):
    new_vh = []
    for vh in vh_l:
        new_vh.append({'ver': vh['ver'], 'hor': vh['hor']-shift, 'data': vh['data'] })
    for vh in vh_r:
        new_vh.append({'ver': vh['ver'], 'hor': vh['hor']+shift, 'data': vh['data'] })
    return new_vh
    
def draw_ang_img(pixel_points, img):
    img_exif = dict(img.getexif())
    for key, value in img_exif.items():
        if ExifTags.TAGS.get(key) == 'FocalLengthIn35mmFilm':
            focal_length_35 = value           
    diag_pixels = math.sqrt(img.size[0]**2 + img.size[1]**2)
    angImgSize = img.size
    angImg = Image.new('RGB', angImgSize)
    focal_len_in_pixels = diag_pixels*focal_length_35/35
    pixel_to_focal_length = 35 / diag_pixels / focal_length_35 
    print(focal_len_in_pixels)
    for pixel in pixel_points:
        angImgX = int(pixel['pos'][0] * math.cos(pixel['pos'][1]) + angImgSize[0]/2)
        angImgY = int(pixel['pos'][0] * math.sin(pixel['pos'][1]) + angImgSize[1]/2)
        if angImgX <0 or angImgX >= angImgSize[0]:
            continue
        if angImgY <0 or angImgY >= angImgSize[1]:
            continue
        angImg.putpixel((angImgX, angImgY), pixel['data'])
    angImg.show()
    return angImg
    
def draw_ver_hor_img(ver_hor_points, img, img_exif, shift = 0):    
    #img_exif = dict(img.getexif())
    for key, value in img_exif.items():
        if ExifTags.TAGS.get(key) == 'FocalLengthIn35mmFilm':
            focal_length_35 = value           
    diag_pixels = math.sqrt(img.size[0]**2 + img.size[1]**2)
    focal_len_in_pixels = diag_pixels*focal_length_35/35
    #vhImgSize = (img.size[0], img.size[1])
    vhImgSize = (img.size[0], img.size[1])
    vhImg = Image.new('RGB', vhImgSize)
    vh_img_point_count = [ [ 0 for _ in range(vhImgSize[0]) ] for _ in range(vhImgSize[1]) ]
    middle_shift = focal_len_in_pixels * math.sin(shift)
    for ver_hor in ver_hor_points:
        adjusted_hor = ver_hor['hor'] + math.asin(math.cos(ver_hor['ver'])*math.sin(shift))
        vhImgX = focal_len_in_pixels * math.tan(math.asin(math.sin(adjusted_hor)/math.cos(ver_hor['ver']))) + vhImgSize[0]/2 - middle_shift
        vhImgY = focal_len_in_pixels * math.tan(math.asin(math.sin(ver_hor['ver'])/math.cos(adjusted_hor))) + vhImgSize[1]/2
        vhImgX = int(vhImgX)
        vhImgY = int(vhImgY)
        if vhImgX <0 or vhImgX >= vhImgSize[0]:
            #print('OUT OF RANGE PIXEL')
            continue
        if vhImgY <0 or vhImgY >= vhImgSize[1]:
            #print('OUT OF RANGE PIXEL')
            continue
        if vh_img_point_count[vhImgY][vhImgX]==0:
            vhImg.putpixel((vhImgX, vhImgY), ver_hor['data'])
            vh_img_point_count[vhImgY][vhImgX] += 1
        else:
            old_pixel = vhImg.getpixel((vhImgX, vhImgY))
            point_count = vh_img_point_count[vhImgY][vhImgX]
            new_pixel = numpy.add(numpy.multiply(old_pixel, (point_count, point_count, point_count)), ver_hor['data']) / (point_count + 1)
            new_pixel = tuple([ int(dat) for dat in new_pixel ])
            vhImg.putpixel((vhImgX, vhImgY), new_pixel)
            vh_img_point_count[vhImgY][vhImgX] += 1
    vhImg.show()
    return vhImg
    
def main():

    img = load_image()
    img_exif = dict(img.getexif())
        
    # vh = xy_img2vh_img(img, img_exif)
    # crude_draw_vh(vh)
    # draw_vh(vh, img, img_exif)
    pixel_points, ver_hor_points = flat_to_angular(img, img_exif)
    #crude_draw_vh(ver_hor_points, math.pi/8)
    # draw_ang_img(pixel_points, img)
    draw_ver_hor_img(ver_hor_points, img, img_exif, math.pi/8)

if __name__=='__main__':
    main()
