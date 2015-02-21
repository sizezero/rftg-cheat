#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *

# loads file as image
def load(filename):
    return pdb.gimp_file_load(filename, filename)

# returns a map of images
def loadAll():
    d = {}
    for i in ['h1', 'h2', 'h3']:
        d[i]=load(i+".xcf").layers[0]
    return d

def arrange():
    d = loadAll()
    image = gimp.Image(1, 1, RGB)

    background = gimp.Layer(image, "Background", 100, 100,
                            RGB_IMAGE, 100, NORMAL_MODE)
    background.fill(BACKGROUND_FILL)
    image.add_layer(background, 0)

    mh = 0
    for i in ['h3', 'h2', 'h1']:
        mh = max(mh, d[i].height)

    pad = 5
    x = pad
    for i in ['h3', 'h2', 'h1']:
        lay = pdb.gimp_layer_new_from_drawable(d[i], image)
        image.add_layer(lay, 0)
        lay.set_offsets(x, (mh-lay.height)/2)
        x += lay.width + pad

    #image.resize(100, 100, 0, 0)
    pdb.gimp_image_resize_to_layers(image)

    drawable = pdb.gimp_image_get_active_layer(image)
    imagefile = "/home/kleemann/gimp/test1.xcf"
    pdb.gimp_file_save(image, drawable, imagefile,  imagefile)


arrange()
