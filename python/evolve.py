import copy
import os
import random
import shutil
import sys
import time

import pygame
from PIL import Image

import html
import svg


class Shape():
    def __init__(self, type, max_width, max_height):
        self.type = type
        
        self.x = random.randint(0, max_width)
        self.y = random.randint(0, max_height)
        
        min_dim = min(max_width, max_height)
        self.rad = random.randint(0, min_dim // 2)
        self.length = 2 * self.rad
            
        self.r = random.randint(0, 255)
        self.g = random.randint(0, 255)
        self.b = random.randint(0, 255)
        self.a = random.random()
        
    def mutate(self, max_width, max_height):
        feature = random.randint(0, 7)
        #feature = random.randint(1, 7)
            
        if feature == 0:
            if self.type == "circle":
                self.type = "square"
                self.x -= self.rad
                self.y -= self.rad
            else:
                self.type = "circle"
                self.x += self.rad
                self.y += self.rad
        elif feature == 1:
            self.x = random.randint(0, max_width)
        elif feature == 2:
            self.y = random.randint(0, max_height)
        elif feature == 3:
            min_dim = min(max_width, max_height)
            self.rad = random.randint(0, min_dim // 2)
            self.length = 2 * self.rad
        elif feature == 4:
            self.r = random.randint(0, 255)
        elif feature == 5:
            self.g = random.randint(0, 255)
        elif feature == 6:
            self.b = random.randint(0, 255)      
        else:
            self.a = random.random()


def getOriginal(picture):
    """Create the grid of the reference image's pixel values."""
    im = Image.open(picture)
    original = []    
    orig_width, orig_height = im.size
    
    for x in range(orig_width):
        original.append([])
        for y in range(orig_height):
            original[-1].append(im.getpixel((x, y)))

    im.close()
    
    return original


def randomize(orig_width, orig_height):
    """Create a list of random shapes."""
    shapes = []
    for i in range(num_shapes):
        type = ("circle", "square")[random.randint(0, 1)]
        #type = "square"
        shapes.append(Shape(type, orig_width, orig_height))
                        
    return shapes


def drawGen(screen, orig_width, orig_height, write=False, name=None, 
            generation=None):
    """Draw the shapes to the pygame screen. Create an svg image if
    write == True.
    """
    screen.fill((255, 255, 255))
    if write:
        file = svg.openSVG(html_path + name + "/" + str(generation),
                           orig_width, orig_height)

    for s in shapes:
        if s.type == "circle":
            surf = pygame.Surface((2 * s.rad, 2 * s.rad), pygame.SRCALPHA)
            pygame.draw.circle(surf, (s.r, s.g, s.b, s.a * 255), 
                               (s.rad, s.rad), s.rad)
            screen.blit(surf, (s.x - s.rad, s.y - s.rad))

            if write:
                svg.writeCircle(file, s.x, s.y, s.rad, 
                                svg.rgb2Hex(s.r, s.g, s.b), s.a)
        else:
            surf = pygame.Surface((s.length, s.length), pygame.SRCALPHA)
            surf.fill((s.r, s.g, s.b, s.a * 255))
            screen.blit(surf, (s.x, s.y))
            
            if write:
                svg.writeRectangle(file, s.x, s.y, s.length, s.length,
                                   svg.rgb2Hex(s.r, s.g, s.b), s.a)

    if write:
        pygame.display.update()
        svg.closeSVG(file)


def getFitness(screen, original, orig_width, orig_height):
    """Calculate the sum of the square of the difference in color at each
    pixel."""
    dif = 0
    
    for x in range(orig_width):
        for y in range(orig_height):
            orig_px = original[x][y]
            new_px = screen.get_at((x, y))

            for i in range(3):
                dif += (orig_px[i] - new_px[i]) ** 2

    return dif


def mutate(shapes, orig_width, orig_height):
    """Choose 1-4 shapes and randomize one of their features."""
    num_mutations = random.randint(1, 4)

    for i in range(num_mutations):
        random.choice(shapes).mutate(orig_width, orig_height)


if __name__ == "__main__":
    pygame.init()

    html_path = "../html/"
    img_path = "../images/"
    img, ext = sys.argv[1].split(".")
    max_gens = int(sys.argv[2])
    gen_gap = int(sys.argv[3])
    num_shapes = int(sys.argv[4])

    if not os.path.exists(html_path + img):
        os.mkdir(html_path + img)
        shutil.copy(img_path + img + "." + ext, html_path + img)
    movie = html.openHTML(html_path + img + "/movie", img + "." + ext)
    html.writeLoop(movie, max_gens, gen_gap)
    html.closeHTML(movie)

    original = getOriginal(img_path + img + "." + ext)
    orig_width = len(original)
    orig_height = len(original[0])
    
    shapes = randomize(orig_width, orig_height)
    
    screen = pygame.display.set_mode((orig_width, orig_height))
    pygame.display.set_caption("Genetic Image Evolver")

    drawGen(screen, orig_width, orig_height)
    last_fit = old_fit = getFitness(screen, original, orig_width, orig_height)

    start_time = 0
    time.clock()
    
    #with open('data.csv', 'w') as data:
    #    data.write("Generation,Distance,% Improvement")

    for gen in range(0, max_gens + 1):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                
        shapes_old = copy.deepcopy(shapes)
        mutate(shapes, orig_width, orig_height)
        drawGen(screen, orig_width, orig_height)
        new_fit = getFitness(screen, original, orig_width, orig_height)

        if new_fit > old_fit:
            shapes = copy.deepcopy(shapes_old)
        else:
            old_fit = new_fit

        if gen % gen_gap == 0:
            time_passed = time.clock() - start_time
            fit_dif = last_fit - old_fit

            print("Generation: {}".format(gen))
            print("Distance: {:,}".format(old_fit))
            print("% Improvement: {:.2%}".format(fit_dif / last_fit))
            print("Time / gen: {:.2f}".format((time_passed) / gen_gap))
            print()
            
            #with open('data.csv', 'a') as data:
            #    data.write("\n" + str(gen) + "," + str(old_fit) + "," + str(fit_dif / last_fit))

            start_time = time.clock()
            last_fit = old_fit

            drawGen(screen, orig_width, orig_height, True, img, gen)
        else:
            drawGen(screen, orig_width, orig_height)
