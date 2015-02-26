
# Roll for the Galaxy cheat sheets

This is a small program that reads scanned images for a set of source
tiles for the board game Roll for the Galaxy and creates various cheat
sheets.  The cheet sheets can be used for play aids or help in
memorizing tile sets.

There are 55 tiles in the game each with a unique front and back side.
These are enumerated in the file <a href=""><tt>docs/tiles.csv</tt></a>

For each of these tiles there needs to be two corresponding image
files in the res/img/tiles/ directory one named dNN.xcf and one named
wNN.xcf where d and w represents the development and world
respectively and NN is the id of the tile as indicated in
`docs/tiles.csv` .  The image type can be any image type supported by
gimp. I would provide these source tiles but the game publisher has
not responded to my requests.

Layout files exist in the res/layout directory.  These are text files
that represent a single cheat sheet to create.  For each layout file,
an image file will be created in the build directory.

For example, the layout file `green.layout` looks like this:

```
w32 w28 _   w36
w52 w27 w54 w48
_   w35 w31
d43 d44 d49 d12
``

and will cause the following image to be produced:

![green-thumb](/docs/green-thumb.png)

# Requirements

In order to run this program you need:

* a unixy OS
* gimp
* the python-fu plugin for gimp
* scanned images of RftG tiles

# Running the program

Edit the file src/arrange.py and set adjust the following constants

```
# the rough tile width and height (pixels)
TILE_DIMENSION = 685

# the smallest spaces between tiles (pixels)
PAD = 10

# When tiles and their opposite side are stacked; how much to overlap
# (percentage of tile dimension)
X_OVERLAP = 0.20
Y_OVERLAP = 0.10
```

Then run `make` from the project's directory.
