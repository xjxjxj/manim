import os
import itertools as it
from PIL import Image
from constants import *

#TODO, Cleanup and refactor this file.

def tex_to_image(expression, 
                 size = "\HUGE",
                 template_tex_file = TEMPLATE_TEX_FILE):
    """
    Returns list of images for correpsonding with a list of expressions
    """
    return_list = isinstance(expression, list)
    simple_tex = "".join(expression)
    if return_list:
        expression = tex_expression_list_as_string(expression)
    exp_hash  = str(hash(expression + size))
    image_dir = os.path.join(TEX_IMAGE_DIR, exp_hash)
    if os.path.exists(image_dir):
        result = [
            Image.open(os.path.join(image_dir, png_file)).convert('RGB')
            for png_file in sorted(
                os.listdir(image_dir), 
                cmp_enumerated_files
            )
        ]
    else:
        filestem = os.path.join(TEX_DIR, exp_hash)
        if not os.path.exists(filestem + ".tex"):
            print "Writing %s at size %s to %s.tex"%(
                simple_tex, size, filestem
            )
            with open(template_tex_file, "r") as infile:
                body = infile.read()
                body = body.replace(SIZE_TO_REPLACE, size)
                body = body.replace(TEX_TEXT_TO_REPLACE, expression)
            with open(filestem + ".tex", "w") as outfile:
                outfile.write(body)
        if not os.path.exists(filestem + ".dvi"):
            commands = [
                "latex", 
                "-interaction=batchmode", 
                "-output-directory=" + TEX_DIR,
                filestem + ".tex",
                "> /dev/null"
            ]
            #TODO, Error check
            os.system(" ".join(commands))
        result = dvi_to_png(filestem + ".dvi")
    return result if return_list else result[0]

def tex_expression_list_as_string(expression):
    return "\n".join([
        "\onslide<%d>{"%count + exp + "}"
        for count, exp in zip(it.count(1), expression)
    ])

def dvi_to_png(filename, regen_if_exists = False):
    """
    Converts a dvi, which potentially has multiple slides, into a 
    directory full of enumerated pngs corresponding with these slides.
    Returns a list of PIL Image objects for these images sorted as they
    where in the dvi
    """
    possible_paths = [
        filename,
        os.path.join(TEX_DIR, filename),
        os.path.join(TEX_DIR, filename + ".dvi"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            directory, filename = os.path.split(path)
            name = filename.split(".")[0]
            images_dir = os.path.join(TEX_IMAGE_DIR, name)
            if not os.path.exists(images_dir):
                os.mkdir(images_dir)
            if os.listdir(images_dir) == [] or regen_if_exists:
                commands = [
                    "convert",
                    "-density",
                    str(PDF_DENSITY),
                    path,
                    "-size",
                    str(DEFAULT_WIDTH) + "x" + str(DEFAULT_HEIGHT),
                    os.path.join(images_dir, name + ".png")
                ]
                os.system(" ".join(commands))
            image_paths = [
                os.path.join(images_dir, name)
                for name in os.listdir(images_dir)
                if name.endswith(".png")
            ]
            image_paths.sort(cmp_enumerated_files)
            return [Image.open(path).convert('RGB') for path in image_paths]
    raise IOError("File not Found")

def cmp_enumerated_files(name1, name2):
    num1, num2 = [
        int(name.split(".")[0].split("-")[-1]) 
        for name in (name1, name2)
    ]
    return num1 - num2















