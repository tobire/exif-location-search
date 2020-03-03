import os
import sys
import concurrent.futures
from PIL import Image
from PIL.ExifTags import TAGS
from PIL import ExifTags

if len(sys.argv) != 6:
    print("Wrong usage. Required arguments: <folder> <latitude> <longitude> <latitude> <longitude>")
    sys.exit()

latMin = min(float(sys.argv[2]), float(sys.argv[4]))
latMax = max(float(sys.argv[2]), float(sys.argv[4]))
lonMin = min(float(sys.argv[3]), float(sys.argv[5]))
lonMax = max(float(sys.argv[3]), float(sys.argv[5]))


def parse_exif(image):
    result = {}
    for (key, value) in image._getexif().items():
        result[TAGS.get(key)] = value
    return result


def get_lat_long(data):
    gpsinfo = {}
    if 'GPSInfo' in data:
        for key in data['GPSInfo'].keys():
            decode = ExifTags.GPSTAGS.get(key)
            gpsinfo[decode] = data['GPSInfo'][key]
        if 'GPSLatitude' in gpsinfo and 'GPSLongitude' in gpsinfo:
            lat = gpsinfo['GPSLatitude']
            lon = gpsinfo['GPSLongitude']
            latD = lat[0][0] + lat[1][0]/60 + (lat[2][0]/(3600*lat[2][1]))
            lonD = lon[0][0] + lon[1][0]/60 + (lon[2][0]/(3600*lon[2][1]))
            return (latD, lonD)


def check_file(path, filename):
    if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".tif") or filename.endswith(".tiff"):
        exif = parse_exif(Image.open(path + "/" + filename))
        latLon = get_lat_long(exif)
        if latLon is not None:
            lat = latLon[0]
            lon = latLon[1]
            if lat >= latMin and lat <= latMax and lon >= lonMin and lon <= lonMax:
                print(filename)


with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    for file in os.listdir(os.fsencode(sys.argv[1])):
        executor.submit(check_file, sys.argv[1], os.fsdecode(file))
