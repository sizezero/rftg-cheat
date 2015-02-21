#!/bin/bash

gimp -idf --batch-interpreter python-fu-eval -b 'execfile("arrange.py")' -b 'pdb.gimp_quit(1)'
