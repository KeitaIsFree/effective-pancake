from PIL import Image

def tilt_image(img, rate):
    new_img = Image.new('RGB', img.size)
    max_diff = img.size[1] / 2 * (rate-1)
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if y > img.size[1] / 2:
                max_y = img.size[1]/2 + max_diff*((img.size[0]/2-x)/(img.size[0]/2))
                y_adj = int((y-img.size[1]/2)/(img.size[1]/2) * max_y + img.size[1]/2) 
                if y_adj < 0:
                    y_adj = 0
                elif y_adj >= img.size[1]:
                    y_adj = img.size[1] - 1
                new_img.putpixel((x, y_adj), img.getpixel((x,y)))
            else:
                max_y = img.size[1]/2 + max_diff*((img.size[0]/2-x)/(img.size[0]/2))
                y_adj = int((y-img.size[1]/2)/(img.size[1]/2) * max_y + img.size[1]/2)
                if y_adj < 0:
                    y_adj = 0
                elif y_adj >= img.size[1]:
                    y_adj = img.size[1] - 1
                new_img.putpixel((x, y_adj), img.getpixel((x,y)))
    # new_img.show()
    return new_img
