#!/usr/bin/env python2

from __future__ import with_statement
import argparse,feedparser,shutil,os,socket,sys,time,json
import urllib2, urllib
from font_colors import font_colors

#name of config file where all keys get stored
config = '~/.config/getrel/getrel.json'

def init_configparser(filename):
	filename = os.path.expanduser(filename)
	if not os.path.isfile(filename):
		print 'please run auth_xrel first'
		exit(-42)

	with open(filename, 'r') as cfg:
		config = json.loads(cfg.read())

	if len(config['hosts']) == 0:
		print 'Hosts list is empty - edit config at: %s.' % (filename)
		sys.exit(1)

	return config

def init_argparse(config):
	from optparse import OptionParser
	import os

	parser = OptionParser()
	parser.add_option('--query', '-q', help='search string', dest='query')
	parser.add_option('--provider', '-p', help='alias of provider', dest='provider', default=None)
	parser.add_option('--group', '-g', help='group #', dest='group', default='')
	parser.add_option('--category', '-c', help='sabnzbd category for nzb', default='Default')
	parser.add_option('--limit', '-l', help='maximum number of results', dest='limit', type='int', default=15)
	parser.add_option('--maxage', '-m', help='maximum age of results in days', dest='maxage', type='int', default=1500)
	parser.add_option('--offset', help='results offset from 0', dest='offset', type='int', default=0)
	parser.add_option('--output', '-o', help='output dir', dest='output', default=os.getcwdu())

	parser.add_option('--first', '-f', action='store_true', help='grab first result without prompt', default=False)
	parser.add_option('--download', '-d', action='store_true', help='do not send to sab even if set in ini', default=False)
	parser.add_option('--sleep', '-s', help='number of seconds to wait between requests', default=0.5)

	(options, args) = parser.parse_args()
	args = vars(options)
	#return check_args(args, config)
	return args

def check_args(args, config):
	if 'sabnzbd' in config:
		try:
			args['sabnzbd_nzbkey'] = config['sabnzbd']['api']
			args['sabnzbd_url'] = config['sabnzbd']['url']
		except:
			print 'could not read api or url from config'

	for h in config['hosts']:
		 firsthost = h
		 break

	if not args['query']:
		print 'Specify search query using --query QUERY'
		sys.exit(-2)
	else:
		args['query'] = '&q=' + args['query']

	if len(args['group']) > 0:
		args['group'] = '&cat=' + args['group']

	if args['provider'] is None:
		url = config['hosts'][firsthost]['url']
		api = config['hosts'][firsthost]['api']
		args['provider'] = [url, api]
	else:
		try:
			config['hosts'][args['provider']]
		except:
			print 'Provider %r not found in config.' % args['provider']
			sys.exit(1)
		args['provider'] = config['hosts'][args['provider']].split(';')

	if len(args['provider'][1]) != 32:
		print 'API key for %r is incorrect length - edit config file.' % (args['provider'][0])
		sys.exit(1)

	if 'sabnzbd_nzbkey' in args:
		if len(args['sabnzbd_nzbkey']) != 32:
			print 'NZB key for SABnzbd+ is incorrect length - edit config file.'
			sys.exit(1)

	args['limit'] = '&limit=%d' % args['limit']
	args['maxage'] = '&maxage=%d' % args['maxage']
	args['offset'] = '&offset=%d' % args['offset']

	return args

def sendtosab(link, title, url, nzbkey, category):
	try:
		socket.setdefaulttimeout(30)
		api = '%s/api?mode=addurl&apikey=%s&nzbname=%s&name=%s&cat=%s' % (url, nzbkey, title.replace(' ', '_'), urllib.quote(link), urllib.quote(category))
		urllib2.urlopen(urllib2.Request(api.replace('//api?', '/api?')))
	except:
		print 'could not add nzb'
		return False

	print '%s%s%s successfully sent to SABnzbd at: %s' % (font_colors.f_green, title, font_colors.f_reset, url)
	return True


def getnzb(link, title, output):
	if not os.path.isdir(output):
		try:
			os.makedirs(output)
		except:
			return False

	output = os.path.join(output, title.replace(' ', '_') + '.nzb')

	try:
		socket.setdefaulttimeout(30)
		urllib.urlretrieve(link, output)
	except:
		return False

	if os.path.getsize(output) == 0 or not os.path.isfile(output):
		print 'Error downloading: %s' % (title)
		try:
			os.unlink(output)
		except:
			return False

	print '%s%s%s downloaded successfully' % (font_colors.f_green, title, font_colors.f_reset)
	return True

def main(args):
	#print '%s using...' % args['provider'][0]

	try:
		url = '%s/api?t=search%s&apikey=%s%s%s%s%s' % (args['provider'][0], args['group'], args['provider'][1], args['limit'], args['maxage'], args['offset'], args['query'])
		apiresponse = feedparser.parse(url.replace('//api?t', '/api?t').replace(' ', '%20'))
	except:
		return False

	results = len(apiresponse.entries)
	if apiresponse.entries is None or results == 0:
		print '%s%s%s not found...' % (font_colors.f_red, args['query'][3:], font_colors.f_reset)
		return False

	if args['first'] == True:
		if args['download'] == False and 'sabnzbd_url' in args:
			if sendtosab(apiresponse.entries[0]['link'], args['query'][3:], args['sabnzbd_url'], args['sabnzbd_nzbkey'], args['category']) == False:
				return False
		else:
			if getnzb(apiresponse.entries[0]['link'], args['query'][3:], args['output']) == False:
				return False
		return True

	print '\t%d results for %s.\n' % (results, args['query'][3:], )

	i = 0
	for r in apiresponse.entries:
		print '[%s]\t%s\n\t   %s -- %s\n' % ((i+1), r['title'], r['category'], r['published'])
		i += 1

	rs = raw_input('enter number(s) to download: ')
	if len(rs) == 0:
		return False

	rs = rs.split(' ')
	get = []
	for n in rs:
		if n.strip() == '':
			continue
		if '-' in n:
			n = n.split('-')
			for i in xrange(int(n[0]), (int(n[1])+1)):
				get.append((i-1))
		else:
			get.append((int(n)-1))

	for i in get:
		if i > results:
			 continue
		if args['download'] == False and args['sabnzbd_url'] is not None:
			if sendtosab(apiresponse.entries[i]['link'], args['query'][3:], args['sabnzbd_url'], args['sabnzbd_nzbkey'], args['category']) == False:
				return False
		else:
			if getnzb(apiresponse.entries[i]['link'], args['query'][3:], args['output']) == False:
				return False
		time.sleep(args['sleep'])

	return True

		
if __name__ == '__main__':
	config_args = init_argparse(config)
	parsed_config = init_configparser(config)
	checked_args = check_args(config_args, parsed_config)
	if main(checked_args) == False:
		sys.exit(1)
