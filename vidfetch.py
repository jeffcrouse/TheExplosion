import requests
import sys
import urllib
from urlparse import urlparse
import os
import os.path
from subprocess import Popen, PIPE
import re
import random
import json



#
#
#
def geocode(address):
	params = urllib.urlencode({'address': address, 'sensor': 'false'})
	url = "http://maps.googleapis.com/maps/api/geocode/json?"+params
	r = requests.get(url)
	items = r.json()
	lat = items["results"][0]["geometry"]["location"]["lat"]
	lng = items["results"][0]["geometry"]["location"]["lng"]
	return (lat, lng)



#
#
#
def make_streetview_360_video(location):
	for i, heading in enumerate(range(0, 360, 2)):
		local = "%s/streetview_%03d.jpg" % (work_dir, i)
		if os.path.exists(local)==False:
			params = {'size': size, 'location': location, 'fov': 90, 'heading': heading, 'pitch': 10, 'sensor': 'false'}
			params["key"] = "AIzaSyBAtUbXjwQbKXulkh2HQWc5W2QOe5PIE40"
			url = "http://maps.googleapis.com/maps/api/streetview?"+urllib.urlencode(params)
			urllib.urlretrieve(url, local)

	cmd = "ffmpeg -f image2 -r 30 -i streetview_%03d.jpg -c:v libx264 -r 30 streetview.mp4"
	ff_process = Popen(cmd.split(' '), stdout=PIPE, cwd=work_dir)
	out, err = ff_process.communicate()


#
#
#
def make_satellite_zoom_video(search_term):
	(lat, lng) = geocode(search_term)
	center = "%s,%s" % (lat, lng)

	melt = "melt "
	for zoom in range(5, 20):
		params = urllib.urlencode({'sensor': 'false', 'maptype': 'hybrid', 'size': size, 'center': center, 'zoom': zoom})
		remote  = "http://maps.googleapis.com/maps/api/staticmap?"+params
		local = "%s/map_%03d.png" % (work_dir, zoom)
		urllib.urlretrieve(remote, local)
		cmd = u'ffmpeg -n -loop 1 -qscale 1 -f image2 -i map_%03d.png -r 30 -t 1 -an streetview_%03d.avi' % (zoom, zoom)
		ff_process = Popen(cmd.split(' '), stdout=PIPE, cwd=work_dir)
		out, err = ff_process.communicate()
		
		melt += "streetview_%03d.avi out=30 -mix 5 -mixer luma " % (zoom)

	melt += "-consumer avformat:map.avi vcodec=libxvid acodec=aac ab=448000 vb=5000k r=30 s=%s" % (size)
	melt_process = Popen(melt.split(' '), stdout=PIPE, cwd=work_dir)
	out, err = melt_process.communicate()



def make_news_frenzy():
	query = 'explosion'
	params = urllib.urlencode({'q': query, 'time': '20121218-20130426', 'output': 'json'})
	url = "http://archive.org/details/tv?"+params
	r = requests.get(url)
	items = r.json()

	melt = "melt "
	for i, item in enumerate(items[:20]):
		o = urlparse(item["video"])
		fileName, fileExtension = os.path.splitext( o.path )
		mp4 = "%s/%s%s" % (work_dir, item["identifier"], fileExtension)

		if os.path.exists(mp4)==False:
			print "Downloading %s" % (item["video"])
			urllib.urlretrieve(item["video"], mp4)
		else:
			print "Already downloaded %s" % (item["video"])

		avi = '%s/%s.avi' % (work_dir, item["identifier"])
		if os.path.exists(avi)==False:
			print "Converting to AVI %s" % (avi)
			cmd = 'ffmpeg -loglevel quiet -n -i %s -q:v 1 -r 30 %s' % (mp4, avi)
			ff_process = Popen(cmd.split(' '), stdout=PIPE, cwd=work_dir)
			out, err = ff_process.communicate()
		else:
			print "Already converted %s"  % (avi)

		frames = get_frames( avi )
		n_frames = len( frames )
		_in = random.randint(0, n_frames-20)
		_out = _in+20
		melt += "%s in=%d out=%d " % (avi, _in, _out)

	melt += "-consumer avformat:frenzy.avi vcodec=libxvid vb=5000k r=30 s=%s" % (size)
	melt_process = Popen(melt.split(' '), stdout=PIPE, cwd=work_dir)
	out, err = melt_process.communicate()



def get_youtube_videos(query, num):
	params = {'q': query, 'v': 2, 'alt': 'json', 'max-results': num}
	url = "https://gdata.youtube.com/feeds/api/videos?" + urllib.urlencode(params)
	r = requests.get(url)
	items = r.json()

	videos = []
	for entry in items["feed"]["entry"]:
		name = '%s.mp4' % (entry["title"]["$t"])
		cmd = 'youtube-dl -f 18 -t %s' % (entry["link"][0]["href"])
		dl_process = Popen(cmd.split(' '), stdout=PIPE, cwd=work_dir)
		out, err = dl_process.communicate()
		videos.append( name )

	print videos

