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
from tempfile import mkstemp
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from vidtools import YouTubeVideo, YouTubeQueryVideo, ArchiveTVQueryVideo, ImageVideo


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


def makeTextVideo( path, lines, y_start, width=640, height=480 ):

	_, temp_path = mkstemp(suffix = '.png')
	image = Image.new("RGB", (width, height), (0, 0, 0))
	draw = ImageDraw.Draw(image)
	padding = 1.2
	y = y_start
	for line in lines:
		w = width+1
		h = 0
		while w > width-15:
			fontPath = line["font"]
			font = ImageFont.truetype(fontPath, line["size"])
			size = font.getsize( line["text"] )
			w = size[0]
			h = size[1]
			line["size"]-=1
		x = (width/2.0) - (w/2.0)
		draw.text((x, y), line["text"], (255, 0, 0), font=font)
		y += h * padding
	image.save(temp_path)
	cmd = u'ffmpeg -y -loglevel quiet -loop 1 -qscale 1 -f image2 -i %s -r 30 -t 10 -an %s' % (temp_path, path)
	ff_process = Popen(cmd.split(' '), stdout=PIPE)
	out, err = ff_process.communicate()
	os.remove( temp_path )
	return path


#  /$$$$$$$$                                                /$$    /$$ /$$       /$$                    
# |__  $$__/                                               | $$   | $$|__/      | $$                    
#    | $$  /$$$$$$   /$$$$$$   /$$$$$$   /$$$$$$   /$$$$$$ | $$   | $$ /$$  /$$$$$$$  /$$$$$$   /$$$$$$ 
#    | $$ /$$__  $$ /$$__  $$ /$$__  $$ /$$__  $$ /$$__  $$|  $$ / $$/| $$ /$$__  $$ /$$__  $$ /$$__  $$
#    | $$| $$$$$$$$| $$  \__/| $$  \__/| $$  \ $$| $$  \__/ \  $$ $$/ | $$| $$  | $$| $$$$$$$$| $$  \ $$
#    | $$| $$_____/| $$      | $$      | $$  | $$| $$        \  $$$/  | $$| $$  | $$| $$_____/| $$  | $$
#    | $$|  $$$$$$$| $$      | $$      |  $$$$$$/| $$         \  $/   | $$|  $$$$$$$|  $$$$$$$|  $$$$$$/
#    |__/ \_______/|__/      |__/       \______/ |__/          \_/    |__/ \_______/ \_______/ \______/ 
                                                                                                      
class TerrorVideo:

	"""Class that represents a single terror video"""


	#
	#
	#
	def __init__(self, name, city, width, height):

		self.name = name
		self.city = city
		#self.checkin = checkin
		self.size = "%sx%s" % (width, height)
		
		(self.lat, self.lng) = geocode(city)

		now = datetime.datetime.now()

		# Create working directory for this name
		self.slug = re.sub(r'\W+','-',name.lower())
		self.id = '%s-%s' % (self.slug, now.strftime("%Y-%m-%d"))
		self.work_dir = "%s/projects/%s" % (os.path.dirname(os.path.realpath(__file__)), self.id)
		if not os.path.exists(self.work_dir):
			os.makedirs(self.work_dir)
		
		self.sources = []

		print 'Creating video %s' % (self.id)


	#
	#
	#
	def create(self):

		options = {"dir": self.work_dir, "duration": 1, "start_time": 0, "query": ""}

		#ACT 1
		options["youtube_id"] = "Z7TpWSJeI_4" # President Obama addresses Boston Attack
		options["start_time"] = 3.39 * 60
		options["duration"] = 12
		self.sources.append( YouTubeVideo(options) )

		options["query"] = 'Aerial footage of %s' % (self.city)
		options["start_time"] = None
		options["duration"] = 2 
		self.sources.append( YouTubeQueryVideo(options) )

		options["youtube_id"] = "B_Gb6i5DF9k" # Systematic House-to-House Raids in Locked-Down Watertown, Mass
		options["duration"] = 4
		self.sources.append( YouTubeVideo(options) )

		options["query"] = "russian meteor explosion dashboard"
		options["duration"] = 1
		self.sources.append( YouTubeQueryVideo(options) )

		options["youtube_id"] = "IjYghdfi0PQ" # Person falling from world trade center
		options["start_time"] = 2.25 * 60
		options["duration"] = 1
		self.sources.append( YouTubeVideo(options) )

		# options["youtube_id"] = "Bf2vaRBIrdw" # Boston marathon bombing suspect killed in shoot-out.
		# options["duration"] = 4
		# self.sources.append( YouTubeVideo(options) )

		options["query"] = "al qaeda expert"
		options["start_time"] = None
		options["duration"] = 1
		self.sources.append( ArchiveTVQueryVideo(options) )

		options["youtube_id"] = "RFA7mJZPXGU" # CELL PHONE FOOTAGE of WACO fertilizer plant explosion
		options["start_time"] = 28
		options["duration"] = 12
		self.sources.append( YouTubeVideo(options) )

		options["query"] = "terrorism expert"
		options["duration"] = 2
		options["start_time"] = None
		self.sources.append( ArchiveTVQueryVideo(options) )

		options["query"] = "terrorism expert fox"
		options["duration"] = 2
		options["start_time"] = None
		self.sources.append( ArchiveTVQueryVideo(options) )

		options["query"] = "terrorism expert nbc"
		options["duration"] = 2
		options["start_time"] = None
		self.sources.append( ArchiveTVQueryVideo(options) )

		options["query"] = "terrorism expert cbs"
		options["duration"] = 2
		options["start_time"] = None
		self.sources.append( ArchiveTVQueryVideo(options) )


		# ACT 2
		options["query"] = "first footage of bombing suspect"
		options["duration"] = 2
		options["start_time"] = None
		self.sources.append( ArchiveTVQueryVideo(options) )

		options["query"] = "swat team going house to house"
		options["duration"] = 5
		self.sources.append( ArchiveTVQueryVideo(options) )

		options["query"] = "from the scene of the explosion"
		options["duration"] = 1
		self.sources.append( ArchiveTVQueryVideo(options) )

		options["query"] = "combat footage taliban raid"
		options["duration"] = 1
		self.sources.append( YouTubeQueryVideo(options) )

		options["query"] = "who is responsible for bomb"
		options["duration"] = 5
		self.sources.append( ArchiveTVQueryVideo(options) )

		options["query"] = 'cell phone footage of bomb'
		options["duration"] = 2
		self.sources.append( ArchiveTVQueryVideo(options) )

		options["query"] = 'why do terrorists'
		options["duration"] = 2
		self.sources.append( ArchiveTVQueryVideo(options) )

		options["youtube_id"] = "RwkAAxbhvL4" # Homeland security advisory team
		options["duration"] = 4
		self.sources.append( YouTubeVideo(options) )

		options["query"] = "Alex Jones conspiracy"
		options["duration"] = 4
		self.sources.append( YouTubeQueryVideo(options) )

		options["query"] = "quran terrorism"
		options["duration"] = 2
		self.sources.append( YouTubeQueryVideo(options) )

		options["query"] = "terror alert america"
		options["duration"] = 1
		self.sources.append( YouTubeQueryVideo(options) )

		options["youtube_id"] = "NpUKM0MFNaM"
		options["duration"] = 1
		self.sources.append( YouTubeVideo(options) )



		# ACT 3
		options["query"] = "Weapons of mass destruction, cc"
		options["duration"] = 2
		self.sources.append( YouTubeQueryVideo(options) )

		options["youtube_id"] = "LLCF7vPanrY" # nuclear explosion time lapse
		options["start_time"] = 5.66 * 60
		options["duration"] = 5
		self.sources.append( YouTubeVideo(options) )

		options["youtube_id"] = "b7wOSuDOXM0" # Police hunting for pieces of pressure cooker bomb
		options["start_time"] = 29
		options["duration"] = 12
		self.sources.append( YouTubeVideo(options) )

		options["query"] = 'Al Qaeda, Muslim, Suspect, Manhunt, Jihad'
		options["start_time"] = None
		options["duration"] = 3
		self.sources.append( YouTubeQueryVideo(options) )

		options["youtube_id"] = "I20uavLBJ1A" # Bill O'Reilly Blasts Nihad Awad
		options["start_time"] = 21
		options["duration"] = 6
		self.sources.append( YouTubeVideo(options) )

		options["query"] = "stump speech al qaeda"
		options["start_time"] = None
		options["duration"] = 2
		self.sources.append( YouTubeQueryVideo(options) )

		options["query"] = "senate terrorism"
		options["start_time"] = None
		options["duration"] = 2
		self.sources.append( YouTubeQueryVideo(options) )

		options["query"] = "congress terrorism"
		options["start_time"] = None
		options["duration"] = 2
		self.sources.append( YouTubeQueryVideo(options) )

		options["youtube_id"] = '5uM1uJ145fA' # Bomb Vest? Running from Explosion w Backpack Disintegrated
		options["start_time"] = 2.03 * 60
		options["duration"] = 5
		self.sources.append( YouTubeVideo(options) )

		options["youtube_id"] = 'lR9C5mR-rN' # NY Post Bag Men
		options["start_time"] = 9
		options["duration"] = 3
		self.sources.append( YouTubeVideo(options) )

		options["youtube_id"] = '5uM1uJ145fA'
		options["start_time"] = 1.2 * 60
		options["duration"] = 5
		self.sources.append( YouTubeVideo(options) )

		options["query"] = "police enter watertown homes"
		options["start_time"] = None
		options["duration"] = 2
		self.sources.append( ArchiveTVQueryVideo(options) )

		options["youtube_id"] = 'IOsyEzHIV3c'
		options["start_time"] = None
		options["duration"] = 0.5
		self.sources.append( YouTubeVideo(options) )

		options["youtube_id"] = '-WYxw-STkrI'
		options["start_time"] = 4 * 60
		options["duration"] = 2
		self.sources.append( YouTubeVideo(options) )

		options["youtube_id"] = 'O3KK2ELZW8Q' # survivor describes blast
		options["start_time"] = 5.5 * 60
		options["duration"] = 2
		self.sources.append( YouTubeVideo(options) )

		options["youtube_id"] = 'avCFLxk_zjc' # survivor describes blast
		options["start_time"] = None
		options["duration"] = 0.5
		self.sources.append( YouTubeVideo(options) )

		options["youtube_id"] = '5Ftl4nOSytc'	# terrorism bomb compilation
		options["start_time"] = 6
		options["duration"] = 1
		self.sources.append( YouTubeVideo(options) )

		options["query"] = 'Emergency Broadcasting System'
		options["start_time"] = None
		options["duration"] = 5
		self.sources.append( YouTubeQueryVideo(options) )

		options["youtube_id"] = 'ufS6bUW1m58'	# Drone Predator Strike
		options["start_time"] = 1.21 * 60
		options["duration"] = 1
		self.sources.append( YouTubeVideo(options) )

		options["youtube_id"] = 'xVMRKyCrwHU' #K urdish Mountain Warrior VS Arabic Desert Camel Driver
		options["start_time"] = None
		options["duration"] = 0.5
		self.sources.append( YouTubeVideo(options) )

		options["youtube_id"] = 'r0KW3al96TQ'
		options["start_time"] = None
		options["duration"] = 0.5
		self.sources.append( YouTubeVideo(options) )

		options["youtube_id"] = 'OHHDuETZYEc'
		options["start_time"] = None
		options["duration"] = 0.5
		self.sources.append( YouTubeVideo(options) )

		options["youtube_id"] = 'TdIiyBFlPr8' # People running from world trade center 
		options["start_time"] = 5
		options["duration"] = 0.5
		self.sources.append( YouTubeVideo(options) )

		options["youtube_id"] = "Z-DSFrGnQrk" # Beyonce National Anthem
		options["start_time"] = 2.75 * 60
		options["duration"] = 19
		self.sources.append( YouTubeVideo(options) )




		self.edit()



	#
	#
	#
	def edit(self):

		intro = '%s/intro.avi' % (self.work_dir )
		introLines = [
			{"text": "Terror Engine", "size": 48, "font": "HelveticaNeueLTCom-Md.ttf"},
			{"text": "generated for "+self.name, "size": 24, "font": "HelveticaNeueLTCom-Md.ttf"},
			{"text": "from "+self.city, "size": 24, "font": "HelveticaNeueLTCom-Md.ttf"},
		]
		makeTextVideo( intro, introLines, 120 )


		cmd = "melt %s out=100 color:black out=100 -mix 50 -mixer luma " % (intro)
		for i, source in enumerate(self.sources):
			if source.exists()==True:
				source.convert_avi()
				n_frames = len( source.get_frames() )
				_duration = source.duration * 30
				if _duration > n_frames:
					_in = 0
					_out = n_frames
				elif source.start_time==None:
					_in = random.randint(0, n_frames-_duration)
					_out = _in+_duration
				else:
					_in = source.start_time * 30
					_out = _in+_duration
				
				cmd += "%s in=%d out=%d -mix 5 -mixer luma " % (source.path, _in, _out)
			else:
				print "Warning: failed to load source %d" % (i)

		cmd += "color:black out=50 -mix 50 -mixer luma "
		cmd += "-consumer avformat:output.avi vb=5000k r=30 s=%s" % (self.size)
		print cmd
		melt_process = Popen(cmd.split(' '), stdout=PIPE, cwd=self.work_dir)
		out, err = melt_process.communicate()


	#
	#
	#
	def make_streetview_360_video(self):
		for i, heading in enumerate(range(0, 360, 2)):
			local = "%s/streetview_%03d.jpg" % (self.work_dir, i)
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
	# def make_satellite_zoom_video(self):
	# 	(lat, lng) = geocode(search_term)
	# 	center = "%s,%s" % (lat, lng)

	# 	melt = "melt "
	# 	for zoom in range(5, 20):
	# 		params = urllib.urlencode({'sensor': 'false', 'maptype': 'hybrid', 'size': size, 'center': center, 'zoom': zoom})
	# 		remote  = "http://maps.googleapis.com/maps/api/staticmap?"+params
	# 		local = "%s/map_%03d.png" % (work_dir, zoom)
	# 		urllib.urlretrieve(remote, local)
	# 		cmd = u'ffmpeg -n -loop 1 -qscale 1 -f image2 -i map_%03d.png -r 30 -t 1 -an streetview_%03d.avi' % (zoom, zoom)
	# 		ff_process = Popen(cmd.split(' '), stdout=PIPE, cwd=work_dir)
	# 		out, err = ff_process.communicate()
			
	# 		melt += "streetview_%03d.avi out=30 -mix 5 -mixer luma " % (zoom)

	# 	melt += "-consumer avformat:map.avi vcodec=libxvid acodec=aac ab=448000 vb=5000k r=30 s=%s" % (size)
	# 	melt_process = Popen(melt.split(' '), stdout=PIPE, cwd=work_dir)
	# 	out, err = melt_process.communicate()




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
