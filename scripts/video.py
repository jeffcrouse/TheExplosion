#!/usr/bin/env python
import requests
import datetime
import sys
import urllib
from urlparse import urlparse
import os
import os.path

location = "Boulder, Colorado"
lat = 40.014468
lon = -105.272026
work = "julia vandenoever photography"


def main(argv):

	url = "http://archive.org/details/tv?q=exposion&time=20121218-20130426&output=json"
	r = requests.get(url)
	items = r.json()
	for item in items:
		remote = item["video"]
		o = urlparse(item["video"])
		fileName, fileExtension = os.path.splitext( o.path )
		local = "videos/%s.%s" % (item["identifier"], fileExtension)
		urllib.urlretrieve(remote, local)



	url = "http://maps.googleapis.com/maps/api/staticmap?center=40.714728,-73.998672&zoom=12&size=400x400&maptype=hybrid&sensor=true_or_false"



	cmd = "melt intro.avi out=100 color:black out=50 -mix 50 -mixer luma "
	cmd += "%s out=300 -mix 50 -mixer luma " % (outroClip)
	cmd += "color:black out=50 -mix 50 -mixer luma "
	cmd += "-consumer avformat:%s vcodec=libxvid acodec=aac ab=448000 vb=5000k r=30 s=640x480" % (mix01) 


if __name__ == "__main__":
	main(sys.argv[1:])

