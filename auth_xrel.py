#!/usr/bin/env python2

#from github: simplegeo/python-oauth2

import urlparse
import urllib
import oauth2 as oauth
import time
import json
import os.path
import sys

#name of config file where all keys get stored
config = '~/.config/clnns/clnns.json'

config = os.path.expanduser(config)
if not os.path.isfile(config):
	if not os.path.isdir(os.path.dirname(config)):
		try:
			os.makedirs(os.path.dirname(config))
		except:
			sys.exit(1)
else:
	print 'Config file already exists.'
	sys.exit(0)

print 'Config file will be written to: %s; please make sure it is writable' % config

consumer_key = '9e98deb544e969069901b613b064c180b99'
consumer_secret = 'oA2omK4nPb70a05rf2if2FzIoQfyO7n8vpT3a3ISgskptjbUt7kmDCuY97bq'

request_token_url = 'http://api.xrel.to/api/oauth/temp_token'
authorize_url = 'http://api.xrel.to/api/oauth/authorize'
access_token_url = 'http://api.xrel.to/api/oauth/access_token'

consumer = oauth.Consumer(consumer_key, consumer_secret)
client = oauth.Client(consumer)

# Step 1: Get a request token. This is a temporary token that is used for
# having the user authorize an access token and to sign the request to obtain
# said access token.O

# hack for callback url (must be oob since this will run as a desktop application)
body = urllib.urlencode(dict(oauth_callback='oob'))
resp, content = client.request(request_token_url, "POST", body)
if resp['status'] != '200':
    raise Exception("Invalid response %s." % resp['status'])

request_token = dict(urlparse.parse_qsl(content))

#print "Request Token:"
#print "    - oauth_token        = %s" % request_token['oauth_token']
#print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']

# Step 2: Redirect to the provider. Since this is a CLI script we do not
# redirect. In a web application you would redirect the user to the URL
# below.

print "Go to the following link in your browser:"
print "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
print

# After the user has granted access to you, the consumer, the provider will
# redirect you to whatever URL you have told them to redirect to. You can
# usually define this in the oauth_callback argument as well.
accepted = 'n'
while accepted.lower() == 'n':
    accepted = raw_input('Have you authorized me? (y/n) ')
oauth_verifier = raw_input('What is the PIN? ')

# Step 3: Once the consumer has redirected the user back to the oauth_callback
# URL you can request the access token the user has approved. You use the
# request token to sign this request. After this is done you throw away the
# request token and use the access token returned. You should store this
# access token somewhere safe, like a database, for future use.
token = oauth.Token(request_token['oauth_token'],
    request_token['oauth_token_secret'])
token.set_verifier(oauth_verifier)
client = oauth.Client(consumer, token)

resp, content = client.request(access_token_url, "POST")
access_token = dict(urlparse.parse_qsl(content))

#print "Access Token:"
#print "    - oauth_token        = %s" % access_token['oauth_token']
#print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
#print
#print "You may now access protected resources using the access tokens."

xrel_dict = {
	'oauth_token': access_token['oauth_token'],
	'oauth_token_secret': access_token['oauth_token_secret'],
	'consumer_key': consumer_key,
	'consumer_secret': consumer_secret,
	}
sabnzbd_dict = {
	'url': 'https://sabnzbdhost.com',
	'api': 'sabnzbdapikey'
}
indexers_dict = {
	'indexer1': {
		'url': 'https://mynzbindex.com',
		'api': 'myapikey'
	},
	'indexer2': {
		'url': 'http://anothernzbi.com',
		'api': 'anotherapikey'
	}
}
torrent_dict = {
	'prefer': True,
	'dir': '/magnet/file/download/path'
}
skip_list = [
	'dont_check',
	'these_lists'
]
full_config = {
	'xrel': xrel_dict,
	'hosts': indexers_dict,
	'sabnzbd': sabnzbd_dict,
	'torrent': torrent_dict,
	'skip': skip_list
}

try:
	with open(config, 'w') as f:
		f.write(json.dumps(full_config, indent=2, sort_keys=True))
	print "Access token are saved in %s" % config
except:
	print 'Error, could not open %s for writing' % config
	sys.exit(1)
