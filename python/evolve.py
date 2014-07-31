import sys
import os
import random
import time

import pygame
from PIL import Image

import svg
import html


def getOriginal(file):
    """Create the grid of the reference image's pixel values."""
    im = Image.open(file)

    global orig_width, orig_height
    orig_width, orig_height = im.size
    for x in range(orig_width):
        original.append([])
        for y in range(orig_height):
            original[-1].append(im.getpixel((x, y)))

    im.close()


def randomize():
    """Create a list of random circles."""
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
    """Draw the circles to the pygame screen. Create an svg image if
    write == True.
    """
    screen.fill((255, 255, 255))
    if write:
        file = svg.openSVG(html_path + name + "/" + str(generation),
                           orig_width, orig_height)

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

    if write:
        pygame.display.update()
        svg.closeSVG(file)


def getFitness(screen):
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


def mutate():
    """Choose 1-4 circles and randomize one of their features."""
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


# if __name__ == " __main__":
pygame.init()

html_path = "../html/"
img_path = "../images/"
img, ext = sys.argv[1].split(".")
max_gens = int(sys.argv[2])
gen_gap = int(sys.argv[3])
num_circles = int(sys.argv[4])

orig_width = 0
orig_height = 0
original = []
circles = []

if not os.path.exists(html_path + img):
    os.mkdir(html_path + img)
movie = html.openHTML(html_path + img + "/movie", img + "." + ext)
html.writeLoop(movie, max_gens, gen_gap)
html.closeHTML(movie)

getOriginal(img_path + img + "." + ext)
randomize()
screen = pygame.display.set_mode((orig_width, orig_height))
pygame.display.set_caption("Genetic Image Evolver")

drawGen(screen)
last_fit = old_fit = getFitness(screen)

start_time = 0
time.clock()

for gen in range(0, max_gens + 1):
    circles_old = [c for c in circles]
    mutate()
    drawGen(screen)
    new_fit = getFitness(screen)

    if new_fit > old_fit:
        circles = [c for c in circles_old]
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

        start_time = time.clock()
        last_fit = old_fit

        drawGen(screen, True, img, gen)
    else:
        drawGen(screen)
