import os, sys

import utils
utils.import_evernote_lib()

import httplib
import time
import Cookie
import uuid

from urllib import urlencode, unquote
from urlparse import urlparse

import config

class GeekNoteAuth(object):

	consumerKey = config.consumer_key
	consumerSecret = config.consumer_secret

	url = {
		"base"  : 'sandbox.evernote.com',
		"oauth" : "/OAuth.action?oauth_token=%s",
		"access": "/OAuth.action",
		"token" : "/oauth",
		"login" : "/Login.action",
	}

	cookies = {}

	postData = {
		'login': {
			'login': 'Sign in',
			'username': '',
			'password': '',
			'targetUrl': None,
		},
		'access': {
			'authorize': 'Authorize',
			'oauth_token': None,
			'oauth_callback': None,
			'embed': 'false',
		}
	}

	username = None
	password = None
	tmpOAuthToken = None
	verifierToken = None
	OAuthToken = None
	incorrectLogin = 0

	def getTokenRequestData(self, **kwargs):
		params = {
			'oauth_consumer_key': self.consumerKey,
			'oauth_signature': self.consumerSecret+'%26',
			'oauth_signature_method': 'PLAINTEXT',
			'oauth_timestamp': str(int(time.time())),
			'oauth_nonce': uuid.uuid4().hex
		}

		if kwargs:
			params = dict(params.items() + kwargs.items())
        
		return params
    
	def loadPage(self, url, uri=None, method='GET', params=''):
		'''
		load a web page via https 
		'''
		if not url:
			print 'Request URL undefined'

		if not uri:
			urlData = urlparse(url)
			url = urlData.netloc
			uri = urlData.path + '?' + urlData.query

		# prepare params, append to uri
		if params :
			params = urlencode(params)
			if method == 'GET':
				uri += ('?' if uri.find('?') == -1 else '&') + params
				params = ''

		# insert local cookies in request
		headers = {
			'Cookie': '; '.join( [ key + '=' + self.cookies[key] for key in self.cookies.keys() ] )
		}

		if method == 'POST':
			headers["Content-type"] = "application/x-www-form-urlencoded"

		# print 'Request URL: %s:/%s > %s # %s' % (url, uri, unquote(params), headers["Cookie"])
		# print 'url: ', url
		# print 'uri: ', uri
		# print 'params: ', unquote(params)
		# print 'Cookie: ', headers["Cookie"]

		conn = httplib.HTTPSConnection(url)
		conn.request(method, uri, params, headers)
		response = conn.getresponse()
		data = response.read()
		conn.close()

		# print 'Response : %s > %s' % (response.status, response.getheaders())
		# print 'response status: ', response.status
		# print 'response headers: ', response.getheaders()

		result = Struct(status=response.status, location=response.getheader('location', None), data=data)

		# update local cookies
		sk = Cookie.SimpleCookie(response.getheader("Set-Cookie", ""))
		for key in sk:
			self.cookies[key] = sk[key].value

		return result

	def parseResponse(self, data):
		data = unquote(data)
		return dict(item.split('=', 1) for item in data.split('?')[-1].split('&'))


	def getToken(self):
		print 'Authorize...'
		self.getTmpOAuthToken()

		self.login()

		print 'Allow Access...'
		self.allowAccess()

		print 'Getting Token...'
		self.getOAuthToken()

		return self.OAuthToken


	def getTmpOAuthToken(self):
		response = self.loadPage(self.url['base'], self.url['token'], "GET", 
			self.getTokenRequestData(oauth_callback = 'https://' + self.url['base']))

		if response.status != 200:
			print "ERROR: Unexpected response status on get temporary oauth_token 200 != ", response.status
			sys.exit()

		responseData = self.parseResponse(response.data)
		if not responseData.has_key('oauth_token'):
			print "ERROR: OAuth temporary not found"
			sys.exit()

		self.tmpOAuthToken = responseData['oauth_token']

		print "Temporary OAuth token : ", self.tmpOAuthToken

	def login(self):
		response = self.loadPage(self.url['base'], self.url['login'], "GET", {'oauth_token': self.tmpOAuthToken})

		if response.status != 200:
			print "ERROR: Unexpected response status on login 200 != ", response.status
			sys.exit()

		if not self.cookies.has_key('JSESSIONID'):
			print "ERROR: Not found value JSESSIONID in the response cookies"
			sys.exit()

		# get login/password
		self.username, self.password = GetUserCredentials()

		self.postData['login']['username'] = self.username
		self.postData['login']['password'] = self.password
		self.postData['login']['targetUrl'] = self.url['oauth'] % self.tmpOAuthToken
		response = self.loadPage(self.url['base'], self.url['login'] + ";jsessionid = " + self.cookies['JSESSIONID'], "POST", 
			self.postData['login'])

		print response

		if not response.location and response.status == 200: # response.status should be 302
			if self.incorrectLogin < 3:
				print 'Sorry, incorrect login or password'
				print 'Authorize...'
				self.incorrectLogin += 1
				return self.login()
			else:
				print "ERROR: Incorrect login or password"

		if not response.location:
			print "ERROR: Target URL was not found in the response on login"
			sys.exit()

		print "Success authorize, redirect to access page"

	def allowAccess(self):
		self.postData['access']['oauth_token'] = self.tmpOAuthToken
		self.postData['access']['oauth_callback'] = 'https://' + self.url['base']
		response = self.loadPage(self.url['base'], self.url['access'], "POST", self.postData['access'])

		if response.status != 302:
			print "ERROR: Unexpected response status on allowing access 302 != ", response.status
			sys.exit()

		responseData = self.parseResponse(response.location)
		if not responseData.has_key('oauth_verifier'):
			print "ERROR: OAuth verifier not found"
			sys.exit()

		self.verifierToken = responseData['oauth_verifier']

		print "OAuth verifier token take"

	def getOAuthToken(self):
		response = self.loadPage(self.url['base'], self.url['token'], "GET",  
			self.getTokenRequestData(oauth_token=self.tmpOAuthToken, oauth_verifier=self.verifierToken))

		if response.status != 200:
			print "ERROR: Unexpected response status on getting oauth token 200 != ", response.status
			sys.exit()

		responseData = self.parseResponse(response.data)
		if not responseData.has_key('oauth_token'):
			print "ERROR: OAuth token not found"
			sys.exit()

		print "OAuth token take: ", responseData['oauth_token']
		self.OAuthToken = responseData['oauth_token']

def GetUserCredentials():
	'''
	Prompts the user for a username and password.
	'''
	try:
		login = None
		password = None
		if login is None:
			login = raw_input("Evernote Login: ")

		if password is None:
			password = raw_input("Evernote Password: ")
	except (KeyboardInterrupt, SystemExit):
		sys.exit()

	return (login, password)

class Struct:
	def __init__(self, **entries): 
		self.__dict__.update(entries)

if __name__ == '__main__':
	tmp = GeekNoteAuth()
	print tmp.getToken()