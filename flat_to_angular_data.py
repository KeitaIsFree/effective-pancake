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

# def flat_to_angular_show(img):
#     img_exif = dict(img.getexif())
#     #focal length assuming a 35mm film
#     for key, value in img_exif.items():
#         if ExifTags.TAGS.get(key) == 'FocalLengthIn35mmFilm':
#             focal_length_35 = value           
#     diag_pixels = math.sqrt(img.size[0]**2 + img.size[1]**2)
#     #fraction of one pixel on sensor to focal length
#     pixel_to_focal_length = 35 / diag_pixels / focal_length_35
#     #####################################################################
#     # TODO: support images without FocalLengthIn35mmFilm exif tag       #
#     #####################################################################
#     angImgSize = (720, 720)
#     angImg = Image.new('RGB',  angImgSize, '#ffffff')
#     for angImgY in range(-int(angImgSize[1]/2), int(angImgSize[1]/2)):
#         angY = angImgY / angImgSize[1] * 90
#         flatY = math.tan(angY/180*math.pi) * focal_length_35 / 35 * diag_pixels
#         if math.floor(flatY) < -(img.size[1]/2) or math.ceil(flatY) >= img.size[1] / 2:
#             continue
#         #print('angImgY: {}, angY: {}, flatY: {}'.format(angImgY, angY, flatY))
#         for angImgX in range(-int(angImgSize[0]/2), int(angImgSize[0]/2)):
#             angX = angImgX / angImgSize[0] * 90
#             flatX = math.tan(angX/180*math.pi) * focal_length_35 / 35 * diag_pixels
#             if math.floor(flatX) < -(img.size[0]/2) or math.ceil(flatX) >= img.size[0] / 2:
#                 continue
#             #print('angImgX: {}, angX: {}, flatX: {}'.format(angImgX, angX, flatX))
#             print('flatX, flatY: {}, {}'.format(flatX, flatY))
#             pixeldata = interpolate(img, flatX, flatY)
#             angImg.putpixel((angImgX+int(angImgSize[0]/2), angImgY+int(angImgSize[1]/2)), pixeldata)
#     angImg.show()

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

def flat_to_angular(img):
    img_exif = dict(img.getexif())
    #focal length assuming a 35mm film
    for key, value in img_exif.items():
        if ExifTags.TAGS.get(key) == 'FocalLengthIn35mmFilm':
            focal_length_35 = value       
    diag_pixels = math.sqrt(img.size[0]**2 + img.size[1]**2)
    #fraction of one pixel on sensor to focal length
    pixel_to_focal_length = 35 / diag_pixels / focal_length_35 
    focus_len_in_pixels = diag_pixels*focal_length_35/35
    #print(pixel_to_focal_length*3264)
    pixel_points = []
    lat_lon_points = []
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
            ang_r = focus_len_in_pixels*math.sin(math.atan(pixel_to_focal_length * r))
            #alpha = math.atan(pixel_to_focal_length*r)
            alpha = math.atan(r / focus_len_in_pixels)
            lat = math.asin(math.sin(alpha) * math.sin(theta))
            lon = math.asin(math.sin(alpha) * math.cos(theta))
            lat_lon_points.append({'lat': lat, 'lon': lon, 'data': img.getpixel((x,y))})
            pixel_points.append({'pos': (ang_r, theta), 'data': img.getpixel((x,y))})
            #print('angX, angY: {}, {}'.format(angX, angY))
    return pixel_points, lat_lon_points

def merge_ll_points(ll_l, ll_r, angle): # angle is the angle between centers of two images
    for ll in ll_r:
        ll_l.append({'lat': ll['lat'], 'lon': ll['lon']+angle, 'data': ll['data'] })
    return ll_l
    
def draw_ang_img(pixel_points, img):
    img_exif = dict(img.getexif())
    for key, value in img_exif.items():
        if ExifTags.TAGS.get(key) == 'FocalLengthIn35mmFilm':
            focal_length_35 = value           
    diag_pixels = math.sqrt(img.size[0]**2 + img.size[1]**2)
    angImgSize = img.size
    angImg = Image.new('RGB', angImgSize)
    focus_len_in_pixels = diag_pixels*focal_length_35/35
    pixel_to_focal_length = 35 / diag_pixels / focal_length_35 
    print(focus_len_in_pixels)
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
    
def draw_lat_lon_img(lat_lon_points, img, shift = 0):    
    img_exif = dict(img.getexif())
    for key, value in img_exif.items():
        if ExifTags.TAGS.get(key) == 'FocalLengthIn35mmFilm':
            focal_length_35 = value           
    diag_pixels = math.sqrt(img.size[0]**2 + img.size[1]**2)
    focus_len_in_pixels = diag_pixels*focal_length_35/35
    llImgSize = (img.size[0], img.size[1])
    llImg = Image.new('RGB', llImgSize)
    ll_img_point_count = [ [ 0 for _ in range(llImgSize[0]) ] for _ in range(llImgSize[1]) ]
    middle_shift = focus_len_in_pixels * math.sin(shift)
    for lat_lon in lat_lon_points:
        # llImgX = int(focus_len_in_pixels * math.tan(lat_lon['lon']+shift) + llImgSize[0]/2 - middle_shift)
        # llImgY = int(focus_len_in_pixels * math.tan(lat_lon['lat']) + llImgSize[1]/2)
        # these are coordinates of projection of the specified point onto plane which is focus_len away from center  
        # llImgX = int(focus_len_in_pixels * math.tan(lat_lon['lon']+shift) + llImgSize[0]/2 - middle_shift)
        # llImgX = int(focus_len_in_pixels * math.tan(lat_lon['lon']+shift)*0.5 + llImgSize[0]/2)
        # llImgY = int(focus_len_in_pixels * math.tan(lat_lon['lat'])*0.5 + llImgSize[1]/2)
        theta = math.atan2(math.sin(lat_lon['lat']), math.sin(lat_lon['lon'] + shift))
        alpha = math.asin(math.sin(lat_lon['lon'] + shift) / math.cos(theta))
        llImgX = int(focus_len_in_pixels / math.cos(alpha) * math.sin(alpha) * math.cos(theta) + llImgSize[0]/2 - middle_shift) 
        llImgY = int(focus_len_in_pixels / math.cos(alpha) * math.sin(alpha) * math.sin(theta) + llImgSize[1]/2)
        if llImgX <0 or llImgX >= llImgSize[0]:
            continue
        if llImgY <0 or llImgY >= llImgSize[1]:
            continue
        if ll_img_point_count[llImgY][llImgX]==0:
            llImg.putpixel((llImgX, llImgY), lat_lon['data'])
            ll_img_point_count[llImgY][llImgX] += 1
        else:
            old_pixel = llImg.getpixel((llImgX, llImgY))
            point_count = ll_img_point_count[llImgY][llImgX]
            new_pixel = numpy.add(numpy.multiply(old_pixel, (point_count, point_count, point_count)), lat_lon['data']) / (point_count + 1)
            new_pixel = tuple([ int(dat) for dat in new_pixel ])
            llImg.putpixel((llImgX, llImgY), new_pixel)
            ll_img_point_count[llImgY][llImgX] += 1
    llImg.show()
    return llImg
    
def main():
    img = load_image()
    pixel_points, lat_lon_points = flat_to_angular(img)
    #draw_ang_img(pixel_points, img)
    draw_lat_lon_img(lat_lon_points, img, -math.pi/8)

if __name__=='__main__':
    main()
