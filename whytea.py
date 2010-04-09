#!/usr/bin/python
#-*- coding: utf-8 -*-

import httplib, urllib, re
import sys, os, subprocess, getpass

def print_usage():
	print '''
	whytea - Download youtube videos and encode them as ogg vorbis. Requires ffmpeg.

		Usage: whytea <url of video>

		sztomi, 2010'''

def parse_commandline():
	if len(sys.argv) != 2:
		print_usage()	
	m = re.search('[?&]v=([^&#]*)', sys.argv[1])
	return m.group(1)
	

# url, info = get_videoinfo('iMvHEijEwUw')
def get_videoinfo(videoID):
	params = urllib.urlencode({'video_id':videoID})
	conn = httplib.HTTPConnection("www.youtube.com")
	conn.request("GET","/get_video_info?&%s" % params)
	response = conn.getresponse()
	data = response.read()
	video_info = dict((k,urllib.unquote_plus(v)) for k,v in
                               (nvp.split('=') for nvp in data.split('&')))
	conn.request('GET','/get_video?video_id=%s&t=%s' % ( video_info['video_id'],video_info['token']))
	response = conn.getresponse()
	direct_url = response.getheader('location')
	return direct_url,video_info

def prgbar(percent):
	return '[' + '=' * (percent / 5) + ' ' * (20 - percent / 5) + ']'

def dlProgress(count, blockSize, totalSize):
	percent = int(count*blockSize*100/totalSize)
	sys.stdout.write("\rDownloading file " + prgbar(percent) + " %d%%" % percent)
	sys.stdout.flush()

id = parse_commandline()
url, info = get_videoinfo(id)
tempname = '/tmp/whytea_tmp_%s' % getpass.getuser()
print info['title']
urllib.urlretrieve(url, tempname, reporthook=dlProgress)
print
print 'Invoking ffmpeg...'
title = info['title'].replace(' ', '_')

p = subprocess.Popen('ffmpeg -i %s -vn -ac 2 -aq 70 -acodec vorbis %s.ogg' % (tempname, title), shell=True)
os.waitpid(p.pid, 0)

os.remove(tempname)

