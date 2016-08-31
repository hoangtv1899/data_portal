#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7

import subprocess
import os
import sys
from PIL import Image
import numpy as np
import ogr

inputFile = sys.argv[1]

im = Image.open(inputFile)
array = np.array(im)
array = array[array != -99]
print "max: %.2f" % array.max()
print "min: %.2f" % array.min()
print "mean: %.2f" % array.mean()
print "median: %.2f" % np.median(array)