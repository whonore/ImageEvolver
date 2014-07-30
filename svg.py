def openSVG(name, width, height):
    file = open(name + ".svg", 'w')
    file.write("<?xml version=\"1.0\" standalone=\"no\"?>\n"
                + "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" "
                + "\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n")
                    
    svg = ("<svg width=\"{}px\" height=\"{}px\" version=\"1.1\" "
          + "xmlns=\"http://www.w3.org/2000/svg\">\n")
    file.write(svg.format(width, height))
    
    return file
                        
def closeSVG(file):
    file.write("</svg>")
    
def writeCircle(file, x, y, r, hex, opacity):
    svg = ("<circle cx=\"{}px\" cy=\"{}px\" r=\"{}px\" fill=\"#{}\""
          + " fill-opacity=\"{}\"/>\n")
    file.write(svg.format(x, y, r, hex, opacity))
    
def rgb2Hex(r, g, b):
    hex_rgb = []
    for c in (r, g, b):
        hex_c = hex(c)[2:]
        if len(hex_c) == 1:
            hex_c = '0' + hex_c
        
        hex_rgb.append(hex_c)
    
    return "".join(hex_rgb)