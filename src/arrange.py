#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *
import csv
import os
import os.path
import re

tileWidth = 685

# loads file as image
def loadTile(tile, description):
    f = "../res/img/tiles/"+tile+".xcf"
    if os.path.exists(f):
        return pdb.gimp_file_load(f, f).layers[0]
    else:
        image = gimp.Image(1, 1, RGB)

        background = gimp.Layer(image, "Background", tileWidth, tileWidth,
                            RGB_IMAGE, 100, NORMAL_MODE)
        pdb.gimp_context_set_background((195,195,195))
        background.fill(BACKGROUND_FILL)
        image.add_layer(background, 0)

        float=pdb.gimp_text_fontname(
                            image,
                            background,
                            0,
                            0,
                            description,
                            0,   #border
                            True, #anitalias
                            120,   #size
                            PIXELS, #GIMP_PIXELS
                            "Sans")
        pdb.gimp_text_layer_resize(float, tileWidth, tileWidth)
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
            row = []
            for tok in re.split(r' +', line):
                if tok == '_':
                    row.append(None)
                else:
                    m = re.match(r'^(d|w)(\d\d)$', tok)
                    if m:
                        row.append(int(m.group(2)))
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
    imagefile = "../build/test1.xcf"
    pdb.gimp_file_save(image, drawable, imagefile,  imagefile)

def testLayoutLoader():
    ll = loadLayout("test1")
    with open('../build/test1.out', 'w') as f:
        f.write(str(ll))

def layItOut(all, base):
    ll = loadLayout(base)

    image = gimp.Image(1, 1, RGB)
    pad = 10
    bigPad = pad * 3
    x = bigPad
    y = bigPad
    for row in ll:
        for id in row:
            if id is None:
                x += tileWidth*2 + pad + bigPad
            else:
                r = all[id]

                d = r['development']
                layD = pdb.gimp_layer_new_from_drawable(d['layer'], image)
                image.add_layer(layD, 0)
                layD.set_offsets(x, y)
                x += tileWidth + pad

                w = r['world']
                layW = pdb.gimp_layer_new_from_drawable(w['layer'], image)
                image.add_layer(layW, 0)
                layW.set_offsets(x, y)
                x += tileWidth + bigPad

        x = bigPad
        y += tileWidth + pad

    pdb.gimp_image_resize_to_layers(image)
    drawable = pdb.gimp_image_get_active_layer(image)
    imagefile = "../build/test1.xcf"
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
