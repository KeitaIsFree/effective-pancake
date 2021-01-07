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

def xy_img2vh_img(img, img_exif):
    #img_exif = dict(img.getexif())
    for key, value in img_exif.items():
        if ExifTags.TAGS.get(key) == 'FocalLengthIn35mmFilm':
            focal_length_35 = value
    if not focal_length_35:
        print('focal_length not found')
    diag_pixels = math.sqrt(img.size[0]**2 + img.size[1]**2)
    #fraction of one pixel on sensor to focal length
    pixel_to_focal_length = 35 / diag_pixels / focal_length_35 
    focal_len_in_pixels = diag_pixels*focal_length_35/35
    vh_points = []
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            h = math.atan((x-img.size[0]/2)/focal_len_in_pixels)
            v = math.atan((y-img.size[1]/2)/focal_len_in_pixels)
            vh_points.append({
                'pos': (v,h),
                'value': img.getpixel((x,y))
                });
            # print('(x,y): ({},{}), (v,h): ({},{})'.format(x,y,v,h))
            # test_xy_vh((x,y), (v,h), focal_len_in_pixels, img.size)
            # test_xy_vh((50,50), (math.pi/4, math.pi/4), 25, (50, 50))
    return vh_points

def crude_draw_vh(vh):
    new_img = Image.new('RGB', (2000, 2000))
    for point in vh:
        x = int(1000*point['pos'][0])
        y = int(1000*point['pos'][1])
        new_img.putpixel((x, y), point['value'])
    new_img.show()

# def crude_draw_vh(vh, focal_len_in_pixels):
#     new_img = Image.new('RGB', (1000, 1000))
#     for point in vh:
#         theta = math.atan2(math.sin(point['pos'][0]), math.sin(point['pos'][1]))
#         alpha = math.asin(math.sin(point['pos'][1]) / math.cos(theta))
#         vhImgX = int(focal_len_in_pixels / math.cos(alpha) * math.sin(alpha) * math.cos(theta) + new_img.size[0]/2) 
#         vhImgY = int(focal_len_in_pixels / math.cos(alpha) * math.sin(alpha) * math.sin(theta) + new_img.size[1]/2)
#         new_img.putpixel((vhImgX, vhImgY), point['value'])
#     new_img.show()

def draw_vh(vh, img, img_exif, shift=0):
    drawed_count = [ [ 0 for _ in range(img.size[0]) ] for _ in range(img.size[1])]
    #img_exif = dict(img.getexif())
    for key, value in img_exif.items():
        if ExifTags.TAGS.get(key) == 'FocalLengthIn35mmFilm':
            focal_length_35 = value
    diag_pixels = math.sqrt(img.size[0]**2 + img.size[1]**2)
    #fraction of one pixel on sensor to focal length
    pixel_to_focal_length = 35 / diag_pixels / focal_length_35 
    focal_len_in_pixels = diag_pixels*focal_length_35/35
    new_img = Image.new('RGB', img.size)
    middle_shift = focal_len_in_pixels * math.sin(shift)
    for point in vh:
        x = focal_len_in_pixels * math.sin(point['pos'][1]+shift) * math.cos(point['pos'][0]) + img.size[0]/2 - middle_shift
        y = focal_len_in_pixels * math.sin(point['pos'][0]) * math.cos(point['pos'][1]+shift) + img.size[1]/2
        x = int(x)
        y = int(y)
        if not (x >= 0 and x < img.size[0]):
            continue
        if not(y >= 0 and y < img.size[1]):
            continue
        if drawed_count[y][x] == 0:
            new_img.putpixel((int(x), int(y)), point['value'])
            drawed_count[y][x] += 1
        else:
            new_pixel = [ int((point['value'][i] + int(new_img.getpixel((x,y))[i]) * drawed_count[y][x]) / (drawed_count[y][x]+1)) for i in range(3) ]
            new_img.putpixel((int(x), int(y)), tuple(new_pixel))
            drawed_count[y][x] += 1
    new_img.show()
    return new_img

def merge_vh(vh1, vh2, shift):
    new_vh = []
    for point in vh1:
        new_vh.append({
            'pos': (point['pos'][0], point['pos'][1]+shift),
            'value': point['value']
        });
    for point in vh2:
        new_vh.append({
            'pos': (point['pos'][0], point['pos'][1]-shift),
            'value': point['value']
        });
    return new_vh

def test_xy_vh(xy, vh, f, imgsize):
    x, y = xy
    v, h = vh
    if f*math.tan(v)+imgsize[1]/2==y:
        print('V v')
    else:
        print('V ERROR')
        print('Calculated y: ', f*math.tan(v)+imgsize[1]/2)
        print('Actual y: ', y)
    if f*math.tan(h)+imgsize[0]/2==x:
        print('H v')
    else:
        print('H ERROR')
        print('Calculated x: ', f*math.tan(h)+imgsize[0]/2)
        print('Actual x: ', x)
        
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
            ang_r = focal_len_in_pixels*math.sin(math.atan(pixel_to_focal_length * r))
            #alpha = math.atan(pixel_to_focal_length*r)
            alpha = math.atan(r / focal_len_in_pixels)
            # checked #########################################
            lat = math.asin(math.sin(alpha) * math.sin(theta))
            lon = math.asin(math.sin(alpha) * math.cos(theta))
            ###################################################
            lat_lon_points.append({'lat': lat, 'lon': lon, 'data': img.getpixel((x,y))})
            pixel_points.append({'pos': (ang_r, theta), 'data': img.getpixel((x,y))})
            #print('(x,y): ({},{}) (lat,lon): ({},{})'.format(x, y, lat, lon))
    return pixel_points, lat_lon_points

def crude_draw_ll(ll):
    new_img = Image.new('RGB', (2000, 2000))
    for point in ll:
        x = int(1000*point['lon'] + 1000)
        y = int(1000*point['lat'] + 1000)
        new_img.putpixel((x, y), point['data'])
    new_img.show()

def merge_ll_points(ll_l, ll_r, shift):
    new_ll = []
    for ll in ll_l:
        new_ll.append({'lat': ll['lat'], 'lon': ll['lon']-shift, 'data': ll['data'] })
    for ll in ll_r:
        new_ll.append({'lat': ll['lat'], 'lon': ll['lon']+shift, 'data': ll['data'] })
    return new_ll
    
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
    
def draw_lat_lon_img(lat_lon_points, img, img_exif, shift = 0):    
    #img_exif = dict(img.getexif())
    for key, value in img_exif.items():
        if ExifTags.TAGS.get(key) == 'FocalLengthIn35mmFilm':
            focal_length_35 = value           
    diag_pixels = math.sqrt(img.size[0]**2 + img.size[1]**2)
    focal_len_in_pixels = diag_pixels*focal_length_35/35
    llImgSize = (img.size[0], img.size[1])
    llImg = Image.new('RGB', llImgSize)
    ll_img_point_count = [ [ 0 for _ in range(llImgSize[0]) ] for _ in range(llImgSize[1]) ]
    middle_shift = focal_len_in_pixels * math.sin(shift)
    for lat_lon in lat_lon_points:
        llImgX = focal_len_in_pixels * math.tan(math.asin(math.sin(lat_lon['lon']+shift)/math.cos(lat_lon['lat']))) + llImgSize[0]/2 - middle_shift
        llImgY = focal_len_in_pixels * math.tan(math.asin(math.sin(lat_lon['lat'])/math.cos(lat_lon['lon']+shift))) + llImgSize[1]/2
        llImgX = int(llImgX)
        llImgY = int(llImgY)
        if llImgX <0 or llImgX >= llImgSize[0]:
            #print('OUT OF RANGE PIXEL')
            continue
        if llImgY <0 or llImgY >= llImgSize[1]:
            #print('OUT OF RANGE PIXEL')
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
    img_exif = dict(img.getexif())
        
    # vh = xy_img2vh_img(img, img_exif)
    # crude_draw_vh(vh)
    # draw_vh(vh, img, img_exif)
    pixel_points, lat_lon_points = flat_to_angular(img, img_exif)
    #crude_draw_ll(lat_lon_points)
    # draw_ang_img(pixel_points, img)
    draw_lat_lon_img(lat_lon_points, img, img_exif, math.pi/8)

if __name__=='__main__':
    main()
