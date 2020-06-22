from PIL import Image
import sys
import pygame

pygame.init()

path = sys.argv[1]

try:
    image = Image.open(path)
except IOError:
    pass

mSequence = list(image.getdata())
with_reds = mSequence.copy()

pyImage = pygame.image.load(path)
pyImageRect = pyImage.get_rect()
dif = [0,0,0]

size = image.size
screen = pygame.display.set_mode(size)

for i in range(size[0]+5, len(mSequence)-size[0]-5):
    for j in [-1, 1, 2, -2, -size[0], size[0], -size[0]+1,-size[0]-1, size[0]+1, size[0]-1]:
        dif = [mSequence[i][0]-mSequence[i+j][0], mSequence[i][1]-mSequence[i+j][1], mSequence[i][2]-mSequence[i+j][2]]
        for x in dif:
            if x^2 >= 50:
                with_reds[i] = (255,0,0)

#cleaning up random red spots
for i in range(size[0]+4, len(mSequence)-size[0]-4):
    red_near = 0
    for j in [-2, -1, 1, 2,-3, 3, -4, 4, -size[0], -size[0]+1, -size[0], size[0]-1, size[0]-1, size[0], size[0]+1]:
        if with_reds[i+j] == (255,0,0):
            red_near+=1
    if not red_near>1:
        with_reds[i] = mSequence[i]

#checking lines
for i in range(size[0], len(mSequence)-size[0]*10):
    if not with_reds[i] == (255,0,0):
        continue
    should_be_reset = True
    #for j in [(1,0), (1,1), (1,2), (1,3), (2,1), (2,3), (3,1), (3,2), (-1,1), (-1,2), (-1,3), (-2,1), (-2,3), (-3,1), (-3,2)]:
    for j in [(1,0), (1,1), (1,2), (2,1), (-1,1), (-1,2), (-2,1), (0,1)]:
        k = 1
        while(True):
            if i+k*j[0]+k*j[1]*size[0]>=len(mSequence):
                break
            if not with_reds[i+k*j[0]+k*j[1]*size[0]]==(255,0,0):
                if (k>100):
                    print(k)
                    should_be_reset=False
                break
            k+=1
    if should_be_reset:
        with_reds[i] = mSequence[i]
    else:
        print('line here!');
        
while 1:
    for i in range(len(with_reds)):
        screen.set_at((i%size[0], i//size[0]), with_reds[i])
    pygame.display.flip()
