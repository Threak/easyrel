#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import os.path
import oauth2 as oauth
import json

import clnns

config_file = '~/.config/clnns/clnns.json'
nzb_path = '~/Software/clnns/nzbs'

def decode_json(resp):

	fav_dict = json.loads(resp)

	fav_list = []

	for fav in fav_dict['payload']:
		#print fav
		#if there are no releases in any list, the key 'releases' does not exist
		if ('releases' not in fav):
			continue
		if (fav['releases']):
			#print fav['releases']
			for dirname in fav['releases']:
				fav_list.append(dirname['dirname'])

	return fav_list

def get_new(list_id, config_file):
	with open(config_file, 'r') as f:
		config_dict = json.loads(f.read())

	config_xrel = config_dict['xrel']
	consumer_key = config_xrel['consumer_key']
	consumer_secret = config_xrel['consumer_secret']
	oauth_token = config_xrel['oauth_token']
	oauth_token_secret = config_xrel['oauth_token_secret']
	url = "http://api.xrel.to/api/favs/list_entries.json?id=%s&get_releases=true" % str(list_id)
	consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
	token = oauth.Token(key=oauth_token, secret=oauth_token_secret)
	client = oauth.Client(consumer, token)
	
	resp, content = client.request(url)
	favs = content[11:-3]
	return decode_json(favs)

config_file = os.path.expanduser(config_file)
try:
	with open(config_file, 'r') as f:
		config_dict = json.loads(f.read())
except IOError:
	print 'please run auth_xrel first'
	exit(-42)

config_xrel = config_dict['xrel']

consumer_key = config_xrel['consumer_key']
consumer_secret = config_xrel['consumer_secret']
oauth_token = config_xrel['oauth_token']
oauth_token_secret = config_xrel['oauth_token_secret']
url = 'http://api.xrel.to/api/favs/lists.json'
consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
token = oauth.Token(key=oauth_token, secret=oauth_token_secret)
client = oauth.Client(consumer, token)
resp, content = client.request(url)

favdict = {}
favlists = json.loads(content[11:-3])['payload']
nzb_path = os.path.expanduser(nzb_path)
for favlist in favlists:
	listname = favlist['name']
	if listname in config_dict['skip_lists']:
		continue
	listid = favlist['id']
	new_dir = os.path.join(nzb_path, listname)
	if not os.path.exists(new_dir):
		os.makedirs(new_dir)
	url = 'http://api.xrel.to/api/favs/list_entries.json?id=%s&get_releases=true' % str(listid)
	resp, content = client.request(url)
	favdict[listname] = []
	for fav in json.loads(content[11:-3])['payload']:
		if ('releases' not in fav):
			continue
		if (fav['releases']):
			for dirname in fav['releases']:
				favdict[listname].append(dirname['dirname'])

for favlist in favdict:
	new_dir = os.path.join(nzb_path, favlist)
	for rel in favdict[favlist]:
		print 'Searching for: %s' % rel
		cmd = './clnns.py -d -f -o "%s" "%s"' % (new_dir, rel)
		os.system(cmd)