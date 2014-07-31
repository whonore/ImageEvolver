import copy
import os
import random
import re
import shutil
import sys
import time

import pygame
from PIL import Image

import html
import svg


DATA = False
MAX_MUTATIONS = 4
RESOLUTION = 1


class Shape():
    def __init__(self, max_width, max_height):
        self.type = random.choice(("circle", "square"))

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


def randomize(orig_width, orig_height, num_shapes):
    """Create a list of random shapes."""
    shapes = []
    for i in range(num_shapes):
        shapes.append(Shape(orig_width, orig_height))

    return shapes


def loadSVG(html_path, img, generation):
    """Recreate a list of shapes from an svg file."""
    shapes = []
    with open(html_path + img + "/" + str(generation) + ".svg") as file:
        for line in file:
            if line.startswith("<circle"):
                shapes.append(Shape(0, 0))
                finder = re.compile("cx=\"(-?\d+.?\d*)px\" "
                                    + "cy=\"(-?\d+.?\d*)px\" "
                                    + "r=\"(\d+.?\d*)px\" "
                                    + "fill=\"#([0-9a-fA-F]{6})\" "
                                    + "fill-opacity=\"(\d+.?\d*)\"")
                shapes[-1].type = "circle"
                shapes[-1].x = int(finder.search(line).group(1))
                shapes[-1].y = int(finder.search(line).group(2))
                shapes[-1].rad = int(finder.search(line).group(3))

                r, g, b = svg.hex2rgb(finder.search(line).group(4))
                shapes[-1].r = r
                shapes[-1].g = g
                shapes[-1].b = b

                shapes[-1].a = float(finder.search(line).group(5))
            elif line.startswith("<rect"):
                shapes.append(Shape(0, 0))
                finder = re.compile("x=\"(-?\d+.?\d*)px\" "
                                    + "y=\"(-?\d+.?\d*)px\" "
                                    + "width=\"(\d+.?\d*)px\" "
                                    + "height=\"(\d+.?\d*)px\" "
                                    + "fill=\"#([0-9a-fA-F]{6})\" "
                                    + "fill-opacity=\"(\d+.?\d*)\"")
                shapes[-1].type = "square"
                shapes[-1].x = int(finder.search(line).group(1))
                shapes[-1].y = int(finder.search(line).group(2))
                shapes[-1].length = int(finder.search(line).group(3))

                r, g, b = svg.hex2rgb(finder.search(line).group(5))
                shapes[-1].r = r
                shapes[-1].g = g
                shapes[-1].b = b

                shapes[-1].a = float(finder.search(line).group(6))

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
                                svg.rgb2hex(s.r, s.g, s.b), s.a)
        else:
            surf = pygame.Surface((s.length, s.length), pygame.SRCALPHA)
            surf.fill((s.r, s.g, s.b, s.a * 255))
            screen.blit(surf, (s.x, s.y))

            if write:
                svg.writeRectangle(file, s.x, s.y, s.length, s.length,
                                   svg.rgb2hex(s.r, s.g, s.b), s.a)

    if write:
        pygame.display.update()
        svg.closeSVG(file)


def getFitness(screen, original, orig_width, orig_height):
    """Calculate the sum of the square of the difference in color at each
    pixel."""
    dif = 0

    for x in range(random.randrange(RESOLUTION), orig_width, RESOLUTION):
        for y in range(random.randrange(RESOLUTION), orig_height, RESOLUTION):
            orig_px = original[x][y]
            new_px = screen.get_at((x, y))

            for i in range(3):
                dif += (RESOLUTION * (orig_px[i] - new_px[i])) ** 2

    return dif


def mutate(shapes, orig_width, orig_height):
    """Choose 1-4 shapes and randomize one of their features."""
    num_mutations = random.randint(1, MAX_MUTATIONS)

    for i in range(num_mutations):
        random.choice(shapes).mutate(orig_width, orig_height)


def parseArgs(args):
    """Parse command line arguments and return the input file and mode."""
    global DATA
    global MAX_MUTATIONS
    global RESOLUTION
    gen_gap = 100
    num_shapes = 256
    start_gen = 0

    args.pop(0)
    if '-d' in args:
        DATA = True
    if '-g' in args:
        idx = args.index('-g')
        gen_gap = int(args[idx + 1])
        args.pop(idx)
        args.pop(idx)
    if '-l' in args:
        idx = args.index('-l')
        start_gen = int(args[idx + 1])
        args.pop(idx)
        args.pop(idx)
    if '-m' in args:
        idx = args.index('-m')
        MAX_MUTATIONS = int(args[idx + 1])
        args.pop(idx)
        args.pop(idx)
    if '-r' in args:
        idx = args.index('-r')
        RESOLUTION = int(args[idx + 1])
        args.pop(idx)
        args.pop(idx)
    if '-s' in args:
        idx = args.index('-s')
        num_shapes = int(args[idx + 1])
        args.pop(idx)
        args.pop(idx)

    try:
        img, ext = args[0].split(".")
        max_gens = int(args[1])
    except IndexError:
        sys.exit("Input the file to evolve and max_gens.\n"
                 + "Options:\n"
                 + "  -d for data collection\n"
                 + "  -g to set generations to store\n"
                 + "  -l to load a generation\n"
                 + "  -m to set max mutations\n"
                 + "  -r to set the resolution to check\n"
                 + "  -s to set the number of shapes\n")

    return (img, ext, max_gens, gen_gap, num_shapes, start_gen)


if __name__ == "__main__":
    pygame.init()

    html_path = "../html/"
    img_path = "../images/"
    args = parseArgs(sys.argv)
    img = args[0]
    ext = args[1]
    max_gens = args[2]
    gen_gap = args[3]
    num_shapes = args[4]
    start_gen = args[5]

    if not os.path.exists(html_path + img):
        os.mkdir(html_path + img)
        shutil.copy(img_path + img + "." + ext, html_path + img)
    movie = html.openHTML(html_path + img + "/movie", img + "." + ext)
    html.writeLoop(movie, max_gens, gen_gap)
    html.closeHTML(movie)

    original = getOriginal(img_path + img + "." + ext)
    orig_width = len(original)
    orig_height = len(original[0])

    if start_gen == 0:
        shapes = randomize(orig_width, orig_height, num_shapes)
    else:
        shapes = loadSVG(html_path, img, start_gen)

    screen = pygame.display.set_mode((orig_width, orig_height))
    pygame.display.set_caption("Genetic Image Evolver")

    drawGen(screen, orig_width, orig_height)
    old_fit = getFitness(screen, original, orig_width, orig_height)
    last_fit = old_fit

    start_time = 0
    time.clock()

    if DATA:
        with open(img + '_data.csv', 'w') as data:
            data.write("Generation,Distance,% Improvement")

    for gen in range(start_gen, max_gens + 1):
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

            if DATA:
                with open('data.csv', 'a') as data:
                    data.write("\n" + str(gen) + "," + str(old_fit)
                               + "," + str(fit_dif / last_fit))

            start_time = time.clock()
            last_fit = old_fit

            drawGen(screen, orig_width, orig_height, True, img, gen)
        else:
            drawGen(screen, orig_width, orig_height)
