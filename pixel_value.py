#!/usr/local/epd-7.3-2-rh5-x86_64/bin/python2.7
#pixel_value.py image longitude latitude

from osgeo import gdal, ogr
import struct
import sys

img = sys.argv[1]
lon = sys.argv[2]
lat = sys.argv[3]

wkt = "POINT ("+lon+" "+lat+")"
point = ogr.CreateGeometryFromWkt(wkt)
mx,my = point.GetX(), point.GetY()
img = gdal.Open(img)
gt = img.GetGeoTransform()
rb = img.GetRasterBand(1)

px = int((mx - gt[0]) / gt[1])
py = int((my - gt[3]) / gt[5])
structval =  rb.ReadRaster(px, py,1,1,buf_type=gdal.GDT_Float32)

intval = struct.unpack('f' , structval)
print intval[0]

# img = '/var/www/html/htdocs/phu/data/ascii/userQuery/201218236166/CurrentLayerW_0.asc'