#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *
import csv
import os
import os.path
import re
import math

# the rough tile width and height (pixels)
TILE_DIMENSION = 685

# the smallest spaces between tiles (pixels)
PAD = 10
BIG_PAD = PAD * 6

# When tiles and their opposite side are stacked; how much to overlap
# (percentage of tile dimension)
X_OVERLAP = 0.20
Y_OVERLAP = 0.10

X_OFFSET = int(X_OVERLAP * TILE_DIMENSION)
Y_OFFSET = int(Y_OVERLAP * TILE_DIMENSION)

# true if the id of the tile should be displayed in the generated
# image
SHOW_ID_ON_IMAGE = True

# source tile file extension
SRC_TILE_FILE_EXTENSION = "xcf"

# loads file as image, returns the layer
def loadTile(tile, description):
    f = "../res/img/tiles/"+tile+"."+SRC_TILE_FILE_EXTENSION
    if os.path.exists(f):
        image = pdb.gimp_file_load(f, f)
        layer = image.layers[0]
        # crop the corners a bit
        # select whole image, chop off square of corners, add circle selection
        # chop inverse
        R = 0.05 # radius of corner circle as percentage of tile dimensions
        r = TILE_DIMENSION * R
        pdb.gimp_image_select_round_rectangle(image, 2, 0, 0, image.width, image.height, r, r)
        pdb.gimp_selection_invert(image)
        pdb.gimp_edit_clear(layer)
        return layer
    else:
        # if the image file does not exist then generate a placeholder
        # image
        image = gimp.Image(1, 1, RGB)

        background = gimp.Layer(image, "Background", TILE_DIMENSION, TILE_DIMENSION,
                            RGB_IMAGE, 100, NORMAL_MODE)
        COLOR_GRAY = (195,195,195)
        pdb.gimp_context_set_background(COLOR_GRAY)
        background.fill(BACKGROUND_FILL)
        image.add_layer(background, 0)

        TEXT_SIZE = int(TILE_DIMENSION / 5.7)
        float=pdb.gimp_text_fontname(
            image, background, 0, 0, description,
            0,   #border
            True, #anitalias
            TEXT_SIZE,   #size
            PIXELS, #GIMP_PIXELS
            "Sans")
        pdb.gimp_text_layer_resize(float, TILE_DIMENSION, TILE_DIMENSION)
        pdb.gimp_floating_sel_anchor(float)

        return image.layers[0]

# returns a map of tiles and layers
# all = { 'id' : { 
#                  'development' : { 
#                                    'cost':int, 
#                                    'name':text, 
#                                    'layer':gimpLayer 
#                                  },
#                  'world':      : {
#                                     'cost':int, 
#                                     'name':text, 
#                                     'layer':gimpLayer
#                                  }
#                }
#       }
def loadAll():
    all = {}
    with open('../docs/tiles.csv') as csvfile:
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

# returns a structured representation of the text layout file as a list of lists
# type = 'd' or 'd'
# id = int
# ll = [
#        [ (type1, id2), None, (type2, id2) ... ]
#      ]
def loadLayout(fname):
    rows = []
    linenum = 1
    with open(fname) as f:
        for line in f:
            line = line.strip()
            row = []
            for tok in re.split(r' +', line):
                if tok == '_':
                    row.append(None)
                else:
                    m = re.match(r'^(d|w)(\d\d)$', tok)
                    if m:
                        type = m.group(1)
                        id = int(m.group(2))
                        if id < 1 or id > 55:
                            raise Exception(fname+"("+str(linenum)+"): id out of range '"+tok+"' line "+line)
                        row.append((type, id))
                    else:
                        raise Exception(fname+"("+str(linenum)+"): bad token '"+tok+"' line "+line)
            if len(row) != 0:
                rows.append(row)
                linenum += 1
    return rows

# displays the tile with the front overlaid on the back
def drawTile(type, id, all, image, x, y):
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

    if SHOW_ID_ON_IMAGE:
        DX = X_OFFSET
        DY = Y_OFFSET
        tLayer = gimp.Layer(image, "text"+str(id), DX, DY, RGBA_IMAGE, 100, NORMAL_MODE)
        image.add_layer(tLayer, 0)
        pdb.gimp_selection_all(image)
        pdb.gimp_edit_clear(tLayer)

        TEXT_SIZE = 50
        COLOR_WHITE = (255, 255, 255)
        pdb.gimp_context_set_foreground(COLOR_WHITE)
        float=pdb.gimp_text_fontname(
            image, tLayer, 0, 0, str(id),
            0,   #border
            True, #anitalias
            TEXT_SIZE,   #size
            PIXELS, #GIMP_PIXELS
            "Sans")
        pdb.gimp_text_layer_resize(float, DX, DY)
        pdb.gimp_floating_sel_anchor(float)

        tLayer.set_offsets(x, y+TILE_DIMENSION)
    
# create and save an image for a given layout file
def layItOut(all, srcFname, dstFnameNoExtension):
    ll = loadLayout(srcFname)

    image = gimp.Image(1, 1, RGB)
    y = BIG_PAD
    ROW_HEIGHT = TILE_DIMENSION + Y_OFFSET + BIG_PAD
    for row in ll:
        x = BIG_PAD
        if len(row)==1 and row[0] is None:
            y += ROW_HEIGHT / 2
        else:
            for tup in row:
                if tup is not None:
                    drawTile(tup[0], tup[1], all, image, x, y)
                x += TILE_DIMENSION + X_OFFSET + BIG_PAD
            y += ROW_HEIGHT

    # resize image to layers plus padding
    pdb.gimp_image_resize_to_layers(image)
    pdb.gimp_image_resize(image, image.width + BIG_PAD*2, image.height + BIG_PAD*2, BIG_PAD, BIG_PAD)

    # add a black background
    bg = gimp.Layer(image, "Background", image.width, image.height, 0, 100, 0)
    image.add_layer(bg, len(image.layers))

    drawable = pdb.gimp_image_get_active_layer(image)
    imagefile = dstFnameNoExtension+".xcf"
    pdb.gimp_file_save(image, drawable, imagefile,  imagefile)

    pdb.gimp_image_merge_visible_layers(image, 2)
    pdb.gimp_image_scale(image, image.width / 3, image.height / 3)
    drawable = pdb.gimp_image_get_active_layer(image)
    imagefile = dstFnameNoExtension+".png"
    pdb.gimp_file_save(image, drawable, imagefile,  imagefile)

    pdb.gimp_image_delete(image)

# iterate through each layout file and produce an image
def allLayouts():
    all = loadAll()

    for root, dirs, files in os.walk('../res/layout'):
        m = re.match(r'^../res/layout/?(.*)$', root)
        if not m:
            raise Exception("path problem root: "+root)
        dstDir = os.path.join('../build/rftg-cheat', m.group(1))

        # create the dirs if they don't exist
        for d in dirs:
            newDir = os.path.join(dstDir, d)
            if not os.path.exists(newDir):
                os.mkdir(newDir)
        # create the layout for each file
        for f in files:
            m = re.match(r'^(.+).layout$', f)
            if m:
                layItOut(all, os.path.join(root, f), os.path.join(dstDir, m.group(1)))

allLayouts()
