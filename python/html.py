html_header = "<!DOCTYPE html>\n<html>\n<body>\n"

html_imgs = "<img src=\"{}\" />\n<img id=\"evolving\" src=\"\" />\n"

html_close = "</body>\n</html>"

html_script = ("<script>\n"
               "   var img_num = 0\n"
               "   setInterval(function(){{showNext()}}, 1 / {})\n"
               "\n"
               "   function showNext() {{\n"
               "     img_num += {}\n"
               "     if (img_num > {}) {{\n"
               "       img_num = 0\n"
               "     }}\n"
               "\n"
               "     document.getElementById(\"evolving\").src = "
               " {} + \"/\" + img_num + \".svg\";\n"
               "   }}\n"
               "</script>\n")


def openHTML(name, reference_img):
    file = open(name + ".html", 'w')

    file.write(html_header)
    file.write(html_imgs.format(reference_img))

    return file


def closeHTML(file):
    file.write(html_close)
    file.close()


def writeLoop(file, img_name, max_gen, gen_gap, frame_rate=12):
    file.write(html_script.format(frame_rate, gen_gap, max_gen, img_name))