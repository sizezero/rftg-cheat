#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *
import csv
import os.path

# loads file as image
def load(tile, description):
    f = "../img/src/tiles/"+tile+".xcf"
    if os.path.exists(f):
        return pdb.gimp_file_load(f, f).layers[0]
    else:
        image = gimp.Image(1, 1, RGB)
        # TODO make this look like a tile
        background = gimp.Layer(image, "Background", 685, 685,
                            RGB_IMAGE, 100, NORMAL_MODE)
        pdb.gimp_context_set_background((195,195,195))
        background.fill(BACKGROUND_FILL)
        image.add_layer(background, 0)

        fontname = "-bitstream-charter-medium-r-normal--12-120-75-75-p-68-iso8859-1[65 70 80_90]"
        float=pdb.gimp_text_fontname(
                            image,
                            None,
                            0,
                            0,
                            'some text',
                            0,   #border
                            True, #anitalias
                            60,   #size
                            PIXELS, #GIMP_PIXELS
                            "Sans")
        #pdb.gimp_floating_sel_anchor(float)
        #pdb.gimp_text_layer_set_color(texture, fontcolor)
        #image.add_layer(textlayer, 0)
        pdb.gimp_image_merge_visible_layers(image, 2) # clip to bottom layer

        return image.layers[0]

# returns a map of tiles and layers
def loadAll():
    all = {}
    with open('../docs/roll.csv') as csvfile:
        reader = csv.reader(csvfile)
        # ignore two header lines
        reader.next()
        reader.next()
        for row in reader:
            id = int(row[0])
            w = { 'cost':int(row[1]), 'name':row[2], 'layer':load("w%02d" % id, row[2]) }
            d = { 'cost':int(row[3]), 'name':row[4], 'layer':load("d%02d" % id, row[4]) }
            all[id] = { 'development':d, 'world':w }
    return all

def arrange():
    all = loadAll()

    # stick all tiles vertically in a giant image
    
    image = gimp.Image(1, 1, RGB)
    pad = 10
    y = pad
    id = 1
    while id in all:
        r = all[id]

        d = r['development']
        layD = pdb.gimp_layer_new_from_drawable(d['layer'], image)
        image.add_layer(layD, 0)
        layD.set_offsets(pad, y)

        w = r['world']
        layW = pdb.gimp_layer_new_from_drawable(w['layer'], image)
        image.add_layer(layW, 0)
        layW.set_offsets(pad+layD.width+pad, y)

        y += pad+max(layD.height, layW.height)
        id += 1

    pdb.gimp_image_resize_to_layers(image)
    drawable = pdb.gimp_image_get_active_layer(image)
    imagefile = "../img/dst/test1.xcf"
    pdb.gimp_file_save(image, drawable, imagefile,  imagefile)

arrange()
