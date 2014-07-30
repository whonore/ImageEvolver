import sys
import random
import pygame
import time
from PIL import Image
import svg

pygame.init()

orig_width = 0
orig_height = 0
original = []

num_circles = 128
circles = []
generation = 1

def getOriginal(file):
    im = Image.open(file)
    
    global orig_width, orig_height
    orig_width, orig_height = im.size
    for x in range(orig_width):
        original.append([])
        for y in range(orig_height):
            original[-1].append(im.getpixel((x, y)))
            
    im.close()
        
def randomize():
    # x, y, radius, r, g, b, a
    for i in range(num_circles):
        circles.append((random.randint(0, orig_width),
                        random.randint(0, orig_height),
                        random.randint(0, min(orig_width, orig_height) // 2),
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.random()))                        
        
def drawGen(screen, write=False, name=None, generation=None):
    screen.fill((255, 255, 255))
    if write:
        file = svg.openSVG(str(generation) + "_" + name, orig_width, orig_height)
            
    for c in circles:
        x = c[0]
        y = c[1]
        rad = c[2]
        r = c[3]
        g = c[4]
        b = c[5]
        a = c[6]

        surf = pygame.Surface((2 * rad, 2 * rad), pygame.SRCALPHA)
        pygame.draw.circle(surf, (r, g, b, a * 255), (rad, rad), rad)
        screen.blit(surf, (x - rad, y - rad))
        
        if write:
            svg.writeCircle(file, x, y, rad, svg.rgb2Hex(r, g, b), a)
    
    pygame.display.update()
    if write:
        svg.closeSVG(file)
    
def getFitness(screen):
    dif = 0
    for x in range(orig_width):
        for y in range(orig_height):
            orig_px = original[x][y]
            new_px = screen.get_at((x, y))
            
            for i in range(3):
                dif += (orig_px[i] - new_px[i]) ** 2
    
    return dif
    
def mutate():
    num_mutations = random.randint(1, 4)
    feature = random.randint(0, 6)
    
    for i in range(num_mutations):
        if feature == 0:
            new_feat = random.randint(0, orig_width)
        elif feature == 1:
            new_feat = random.randint(0, orig_height)
        elif feature == 2:
            new_feat = random.randint(0, min(orig_width, orig_height) // 2)
        elif 3 <= feature <= 5:
            new_feat = random.randint(0, 255)
        else:
            new_feat = random.random()
        
        circle_idx = random.randint(0, len(circles) - 1)
        new_circle = list(circles[circle_idx])
        new_circle[feature] = new_feat
        circles[circle_idx] = tuple(new_circle)

img, ext = sys.argv[1].split(".")
max_gens = int(sys.argv[2])
gen_gap = 100

getOriginal(img + "." + ext)
randomize()
screen = pygame.display.set_mode((orig_width, orig_height))
pygame.display.set_caption("Genetic Image Evolver")

drawGen(screen)
old_fit = getFitness(screen)
last_fit = old_fit
start_time = 0
time.clock()
    
for gen in range(1, max_gens + 1):
    pygame.display.set_caption("Genetic Image Evolver Generation: {}".format(gen))
    circles_old = [c for c in circles]
    mutate()
    drawGen(screen)
    new_fit = getFitness(screen)
    
    if new_fit > old_fit:
        circles = [c for c in circles_old]
    else:
        old_fit = new_fit

    if gen % gen_gap == 0:
        print("Generation: {}".format(gen))
        print("Distance: {:,}".format(old_fit))
        print("% Improvement: {:.2%}".format((old_fit - last_fit) / last_fit)
        print("Time / gen: {:.2f}".format((time.clock() - start_time) / gen_gap))
        print()
        start_time = time.clock()
        last_fit = old_fit
        
        drawGen(screen, True, img, gen)
    else:
        drawGen(screen)
