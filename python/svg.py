xml_header = ("<?xml version=\"1.0\" standalone=\"no\"?>\n"
              "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" "
              "\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n")

svg_header = ("<svg width=\"{}px\" height=\"{}px\" version=\"1.1\" "
              "xmlns=\"http://www.w3.org/2000/svg\">\n")
              
svg_close = "</svg>"

svg_circle = ("<circle cx=\"{}px\" cy=\"{}px\" r=\"{}px\" fill=\"#{}\" "
              "fill-opacity=\"{}\"/>\n")

svg_rectange = ("<rect x=\"{}px\" y=\"{}px\" width=\"{}px\" height=\"{}px\" "
                "fill=\"#{}\" fill-opacity=\"{}\">\n")


def openSVG(name, width, height):
    file = open(name + ".svg", 'w')

    file.write(xml_header)
    file.write(svg_header.format(width, height))

    return file


def closeSVG(file):
    file.write(svg_close)
    file.close()


def writeCircle(file, cx, cy, r, hex, opacity):
    file.write(svg_circle.format(cx, cy, r, hex, opacity))


def writeRectangle(file, x, y, width, height, hex, opacity):
    file.write(svg_rectange.format(x, y, width, height, hex, opacity))


def rgb2Hex(r, g, b):
    hex_rgb = []
    for c in (r, g, b):
        hex_c = hex(c)[2:]
        if len(hex_c) == 1:
            hex_c = '0' + hex_c

        hex_rgb.append(hex_c)

    return "".join(hex_rgb)
