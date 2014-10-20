#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import requests
import time

def login(login_data):
	xrel_session = requests.Session()
	login_url = 'https://ssl.xrel.to/login.html'
	headers = {
		'Referer': 'https://ssl.xrel.to/login.html'
	}
	
	xrel_session.get(login_url)
	xrel_session.post(login_url, headers=headers, data=login_data)
	resp = xrel_session.get('http://www.xrel.to/home.html?logged_in=1', headers=headers)

	#print resp.text.encode('ascii', 'ignore')

	return xrel_session

def set_fav_state(xrel_session, set_fav_data):
	set_fav_url = 'http://www.xrel.to/favs-manager.html?anticache=%(anticache)d&action=rls_new&new=%(isnew)d&watchlist=%(wid)d&rls=%(rid)d'
	set_fav_header = {
		'Host': 'www.xrel.to',
		'Referer': 'http://www.xrel.to/home.html'
	}

	resp = xrel_session.get(set_fav_url % set_fav_data, headers=set_fav_header)

def logout(xrel_session):
	pass

if __name__ == '__main__':
	login_data = {
		'username': '',
		'password': ''
	}
	set_fav_data = {
		'anticache': long(time.time()), # unix time stamp (long)
		'isnew': 1, # mark as new, otherwise mark as read (boolean)
		'wid': 3556, # watchlist id (int)
		'rid': 859625 # release id (int)
	}
	xrel_session = login(login_data)
	set_fav_state(xrel_session, set_fav_data)
	logout(xrel_session)