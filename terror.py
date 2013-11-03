#!/usr/bin/env python
import argparse
import sys
from TerrorVideo import TerrorVideo

#
#
#
def main(argv):

	# Deal with arguments
	parser = argparse.ArgumentParser(description='Take a directory of videos and turn them into a single large grid of videos')
	parser.add_argument('--name', default=5, type=str, help="The number of the user", required=True)
	parser.add_argument('--city', default=5, type=str, help="The city where the user is located", required=True)
	#parser.add_argument('--checkin', default=5, type=str, help="A specific place or establishment that the user has been", required=True)
	parser.add_argument('--width', default=640, type=int, help="The width of the output video")
	parser.add_argument('--height', default=480, type=int, help="The height of the output video")
	#parser.add_argument('output', type=str, help='The output name')
	args = parser.parse_args()

	name = args.name
	city = args.city
	#checkin = args.checkin
	width = args.width
	height = args.height

	vid = TerrorVideo(name, city, width, height)
	vid.create()


if __name__ == "__main__":
	main(sys.argv[1:])

