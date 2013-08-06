import urlparse
import webbrowser
import oauth2 as oauth

import config
import utils
utils.import_evernote_lib()

from evernote.api.client import EvernoteClient

class EvernoteAuth(object):
	def __init__(self):
		super(EvernoteAuth, self).__init__()
		self.consumer = oauth.Consumer(config.consumer_key, config.consumer_secret)
		self.client = oauth.Client(self.consumer)
		
	def get_evernote_client(token=None):
		if token:
			return EvernoteClient(token=token, sandbox = config.sandbox)
		else:
			return EvernoteClient(
				consumer_key = config.consumer_key,
				consumer_secret = config.consumer_secret,
				sandbox = config.sandbox
			)

	def auth(self):
		resp, content = self.client().request(config.request_token_url, "GET")

		print resp,content

		if resp['status'] != '200':
			raise Exception("Invalid response %s." % resp['status'])

		request_token = dict(urlparse.parse_qsl(content))

		print 'Request token'
		print "    - oauth_token        = %s" % request_token['oauth_token']
		print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
		print 

		user_authorize_url = '%s?oauth_token=%s' % (config.authorize_url, request_token['oauth_token'])
		webbrowser.open(user_authorize_url)
		print 'Authorized page has been open in your default browser...'

		oauth_verifier = raw_input('What is the PIN? ')

		token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
		token.set_verifier(oauth_verifier)

		client = oauth.Client(self.consumer, token)
		resp, content = client.request(config.access_token_url, "POST")
		access_token = dict(urlparse.parse_qsl(content))

		print access_token

		print "Access Token:"
		print "    - oauth_token        = %s" % access_token['oauth_token']
		print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
		print

if __name__ == '__main__':
	ea = EvernoteAuth()
	ea.auth()


