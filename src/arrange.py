#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *
import csv
import os
import os.path
import re

# the rough tile width and height
TILE_SIZE = 685

# small spaces between tiles
PAD = 10

# When tiles and their opposite side are stacked; how much to overlap
X_OVERLAP = 0.20
Y_OVERLAP = 0.10

# loads file as image, returns the layer
def loadTile(tile, description):
    f = "../res/img/tiles/"+tile+".xcf"
    if os.path.exists(f):
        return pdb.gimp_file_load(f, f).layers[0]
    else:
        image = gimp.Image(1, 1, RGB)

        background = gimp.Layer(image, "Background", TILE_SIZE, TILE_SIZE,
                            RGB_IMAGE, 100, NORMAL_MODE)
        COLOR_GRAY = (195,195,195)
        pdb.gimp_context_set_background(COLOR_GRAY)
        background.fill(BACKGROUND_FILL)
        image.add_layer(background, 0)

        TEXT_SIZE = int(TILE_SIZE / 5.7)
        float=pdb.gimp_text_fontname(
                            image,
                            background,
                            0,
                            0,
                            description,
                            0,   #border
                            True, #anitalias
                            TEXT_SIZE,   #size
                            PIXELS, #GIMP_PIXELS
                            "Sans")
        pdb.gimp_text_layer_resize(float, TILE_SIZE, TILE_SIZE)
        pdb.gimp_floating_sel_anchor(float)

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
            w = { 'cost':int(row[1]), 'name':row[2], 'layer':loadTile("w%02d" % id, row[2]) }
            d = { 'cost':int(row[3]), 'name':row[4], 'layer':loadTile("d%02d" % id, row[4]) }
            all[id] = { 'development':d, 'world':w }
    return all

# returns a list of lists of None and Layout
def loadLayout(layoutBase):
    rows = []
    linenum = 1
    with open("../res/layout/"+layoutBase+".layout") as f:
        for line in f:
            line = line.strip()
            row = []
            for tok in re.split(r' +', line):
                if tok == '_':
                    row.append(None)
                else:
                    m = re.match(r'^(d|w)(\d\d)$', tok)
                    if m:
                        row.append((m.group(1), int(m.group(2))))
                    else:
                        raise Exception(layoutBase+"("+str(linenum)+"): bad token '"+tok+"' line "+line)
            if len(row) != 0:
                rows.append(row)
                linenum += 1
    return rows

def arrange():
    all = loadAll()

    # stick all tiles vertically in a giant image
    
    image = gimp.Image(1, 1, RGB)
    y = PAD
    id = 1
    while id in all:
        r = all[id]

        d = r['development']
        layD = pdb.gimp_layer_new_from_drawable(d['layer'], image)
        image.add_layer(layD, 0)
        layD.set_offsets(PAD, y)

        w = r['world']
        layW = pdb.gimp_layer_new_from_drawable(w['layer'], image)
        image.add_layer(layW, 0)
        layW.set_offsets(PAD+layD.width+PAD, y)

        y += PAD+max(layD.height, layW.height)
        id += 1

    pdb.gimp_image_resize_to_layers(image)
    drawable = pdb.gimp_image_get_active_layer(image)
    imagefile = "../build/test1.xcf"
    pdb.gimp_file_save(image, drawable, imagefile,  imagefile)

def testLayoutLoader():
    ll = loadLayout("test1")
    with open('../build/test1.out', 'w') as f:
        f.write(str(ll))

# create and save an image for a given layout file
def layItOut(all, base):
    ll = loadLayout(base)

    image = gimp.Image(1, 1, RGB)
    BIG_PAD = PAD * 6
    y = BIG_PAD
    X_OFFSET = int(X_OVERLAP * TILE_SIZE)
    Y_OFFSET = int(Y_OVERLAP * TILE_SIZE)
    ROW_HEIGHT = TILE_SIZE + Y_OFFSET + BIG_PAD
    for row in ll:
        x = BIG_PAD
        if len(row)==1 and row[0] is None:
            y += ROW_HEIGHT / 2
        else:
            for tup in row:
                if tup is None:
                    x += TILE_SIZE + X_OFFSET + BIG_PAD
                else:
                    type = tup[0]
                    id = tup[1]
                    r = all[id]
                    if type=='d':
                        backLayer = r['world']['layer']
                        frontLayer = r['development']['layer']
                    else:
                        frontLayer = r['world']['layer']
                        backLayer = r['development']['layer']

                    layBack = pdb.gimp_layer_new_from_drawable(backLayer, image)
                    image.add_layer(layBack, 0)
                    layBack.set_offsets(x, y)

                    layFront = pdb.gimp_layer_new_from_drawable(frontLayer, image)
                    image.add_layer(layFront, 0)
                    layFront.set_offsets(x+X_OFFSET, y+Y_OFFSET)
                    x += TILE_SIZE + X_OFFSET + BIG_PAD

            y += ROW_HEIGHT

    # resize image to layers plus padding
    pdb.gimp_image_resize_to_layers(image)
    pdb.gimp_image_resize(image, image.width + BIG_PAD*2, image.height + BIG_PAD*2, BIG_PAD, BIG_PAD)

    # add a black background
    bg = gimp.Layer(image, "Background", image.width, image.height, 0, 100, 0)
    image.add_layer(bg, len(image.layers))

    drawable = pdb.gimp_image_get_active_layer(image)
    imagefile = "../build/"+base+".xcf"
    pdb.gimp_file_save(image, drawable, imagefile,  imagefile)

def allLayouts():
    all = loadAll()

    for f in os.listdir('../res/layout'):
        m = re.match(r'^(.+).layout$', f)
        if m:
            layItOut(all, m.group(1))

#arrange()
#testLayoutLoader()
allLayouts()
