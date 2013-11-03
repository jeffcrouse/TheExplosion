import os
import os.path
import datetime
import re
import requests
import urllib
import sys
from urlparse import urlparse
from subprocess import Popen, PIPE
import random
import json
import srt
import string


class SourceVideo:
	"""Base class for all other videos"""

	def __init__(self, options):
		self.path = None
		self.options = options
		self.frames = []
		self.start_time = options["start_time"]
		self.duration = options["duration"]

	def exists(self):
		if self.path==None:
			return False
		return os.path.exists( self.path )

	#
	#
	#
	def get_info(path):
		x = y = duration = 0

		p = Popen(['ffmpeg', '-i', path], stdout=PIPE, stderr=PIPE)
		stdout, stderr = p.communicate()
		pattern = re.compile(r'Stream.*Video.*, ([0-9]+)x([0-9]+)')
		match = pattern.search(stderr)
		if match:
			x, y = map(int, match.groups()[0:2])

		pattern = re.compile(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),")
		match = pattern.search(stderr)
		if match:
			group = match.groupdict()
			duration += int(group["hours"]) * 3600
			duration += int(group["minutes"]) * 60
			duration += float(group["seconds"])
		return int(x), int(y), float(duration)

	#
	#
	#
	def get_frames( self ):
		if(len(self.frames) == 0):
			cmd = u'ffprobe -loglevel quiet -show_frames %s' % (self.path)
			ff_process = Popen(cmd.split(' '), stdout=PIPE, cwd=os.getcwd())
			out, err = ff_process.communicate()
			
			pieces = out.split(u"[/FRAME]\n")
			for piece in pieces:
				if "media_type=video" in piece:
					frame = {}
					start = re.search(r"pkt_pts_time=([\d\.]+)", piece)
					if start: frame["start"] = float( start.group(1) )
					end = re.search(r"pkt_dts_time=([\d\.]+)", piece)
					if end: frame["end"] = float( end.group(1) )
					duration = re.search(r"pkt_duration_time=([\d\.]+)", piece)
					if duration: frame["duration"] = float( duration.group(1) )
					number = re.search(r"coded_picture_number=([\d\.]+)", piece)
					if number: 
						frame["number"] = int( number.group(1) )
						self.frames.append( frame )
		return self.frames

	def convert_avi(self):
		fname, ext = os.path.splitext( self.path )
		avi = self.path.replace(ext, ".avi")
		if os.path.exists(avi)==False:
			cmd = 'ffmpeg -loglevel quiet -n -i %s -q:v 1 -r 30 %s' % (self.path, avi)
			ff_process = Popen(cmd.split(' '), stdout=PIPE)
			out, err = ff_process.communicate()

		self.path = avi



class YouTubeVideo(SourceVideo):
	"""A YouTube video specified by an ID"""

	def __init__(self, options):
		SourceVideo.__init__(self, options)
		#subtitles = "--write-sub" if options["subtitles"] else ""
		self.youtube_id = options["youtube_id"]
		self.path = '%s/%s.mp4' % (options["dir"], self.youtube_id)
		if os.path.exists( self.path )==False:
			url = "http://www.youtube.com/watch?v=%s" % (self.youtube_id)
			cmd = 'youtube-dl --no-overwrites --write-info-json -f 18 -o %%(id)s.%%(ext)s %s' % (url)
			dl_process = Popen(cmd.split(' '), stdout=PIPE, cwd=options["dir"])
			out, err = dl_process.communicate()
		
			self.srt = '%s/%s.en.srt' % (options["dir"], self.youtube_id)
			self.timecodes = None
			if os.path.exists( self.srt ):
				self.timecodes = srt.parse( self.srt )

	def set_in_out(self, word):
		if self.timecodes==None:
			return

		for timecode in self.timecodes:
			text = timecode[2]
			if word in text:
				self.start_time = (timecode[0].ms * 1000) * 30
				end_time = (timecode[1].ms * 1000) * 30
				self.duration = end_time - start_time
				return
			
			


class YouTubeQueryVideo(YouTubeVideo):
	""" YouTube video specified by a query"""

	def __init__(self, options):
		
		params = {'q': options["query"], 'v': 2, 'alt': 'json', 'max-results': 1}
		url = "https://gdata.youtube.com/feeds/api/videos?" + urllib.urlencode(params)
		r = requests.get(url)
		items = r.json()
		if "feed" not in items:
			return
		if "entry" not in items["feed"]:
			return
		if len(items["feed"]["entry"])==0:
			return

		entry = items["feed"]["entry"][0]
		options["youtube_id"] = entry["media$group"]["yt$videoid"]["$t"]
		YouTubeVideo.__init__(self, options)



class ArchiveTVQueryVideo(SourceVideo):

	def __init__(self, options):
		SourceVideo.__init__(self, options)

		query = options["query"]
		now = datetime.datetime.now()
		time = '%d%02d%02d-%d%02d%02d' % (now.year, now.month, now.day-5, now.year, now.month, now.day)
		params = urllib.urlencode({'q': query, 'time': time, 'output': 'json'})
		url = "http://archive.org/details/tv?"+params
		r = requests.get(url)
		items = r.json()
		
		if len(items) > 0:
			item = items[0]
			o = urlparse(item["video"])
			fname, ext = os.path.splitext( o.path )
			self.path = '%s/%s%s' % (options["dir"], item["identifier"], ext)
			if os.path.exists(self.path)==False:
				urllib.urlretrieve(item["video"], self.path)
	





class ImageVideo(SourceVideo):

	def __init__(self, options):
		SourceVideo.__init__(self, options)

		image_url = options["image_url"]
		basename =  ''.join(random.choice(string.lowercase) for i in range(6))

		local = '%s/%s.jpg' % (options["dir"], basename )
		if os.path.exists(local)==False:
				urllib.urlretrieve(image_url, local)
		
		self.path = '%s/%s.avi' % (options["dir"], basename )
		cmd = 'ffmpeg -loop 1 -f image2 -i %s -c:v libx264 -t 30 %s' % (local, self.path)
		ff_process = Popen(cmd.split(' '), stdout=PIPE)
		out, err = ff_process.communicate()




