#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import os.path
import oauth2 as oauth
import json
from font_colors import font_colors
import getrel
import setfav
import time
from torrentApi import torrent_api as api

#name of config file where all keys get stored
config = '~/.config/getrel/getrel.json'
nzb_path = '~/.get_fav/nzbs'

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

config = os.path.expanduser(config)
try:
	with open(config, 'r') as f:
		config_dict = json.loads(f.read())
except IOError:
	print 'please run auth_xrel first'
	exit(-42)
config_args = getrel.init_argparse(config)
parsed_config = getrel.init_configparser(config)

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
	if listname in config_dict['skip']:
		continue
	listid = favlist['id']
	new_dir = os.path.join(nzb_path, listname)
	if not os.path.exists(new_dir):
		os.makedirs(new_dir)
	url = 'http://api.xrel.to/api/favs/list_entries.json?id=%d&get_releases=true' % listid
	resp, content = client.request(url)
	favdict[listid] = {'name': listname, 'rels': []}
	for fav in json.loads(content[11:-3])['payload']:
		if ('releases' not in fav):
			continue
		if (fav['releases']):
			for dirname in fav['releases']:
				relid = int(dirname['link_href'].split('/')[4])
				favdict[listid]['rels'].append({'name': dirname['dirname'], 'id': relid})

try:
	xrel_session = setfav.login({'username': config_xrel['username'], 'password': config_xrel['password']})
except:
	pass

prefer_torrent = config_dict['torrent']['prefer']
torrent_download_path = config_dict['torrent']['dir']
if prefer_torrent:
	torrentApi = api.TorrentApi(base_path=torrent_download_path)

for favlist in favdict:
	listname = favdict[favlist]['name']
	print '%s%s%s:' % (font_colors.f_magenta, listname, font_colors.f_reset)
	new_dir = os.path.join(nzb_path, listname)
	config_args['category'] = listname.lower()
	for reldict in favdict[favlist]['rels']:
		rel = reldict['name']
		print '%s%s%s searching...' % (font_colors.f_yellow, rel, font_colors.f_reset)
		config_args['query'] = rel
		checked_args = getrel.check_args(config_args.copy(), parsed_config)

		set_fav_data = {
			'anticache': long(time.time()), # unix time stamp (long)
			'isnew': 0, # mark as new, otherwise mark as read (boolean)
			'wid': favlist, # watchlist id (int)
			'rid': reldict['id'] # release id (int)
		}

		found_release = False
		if prefer_torrent:
			found_release = torrentApi.search(rel)
		if not found_release:
			found_release = getrel.main(checked_args)
		if found_release:
			if xrel_session:
				setfav.set_fav_state(xrel_session, set_fav_data)
