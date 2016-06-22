from rauth.service import OAuth1Service
import requests
from BeautifulSoup import BeautifulSoup
import json

import urllib

class ABCMagentoRESTClient(object):
	MAGENTO_HOST = 'http://dev.abcwarehouse.com'
	MAGENTO_API_BASE = '%s/api/rest/' % MAGENTO_HOST
	MAGENTO_LOGIN_URL = '%s/index.php/admin/oauth_authorize/index/' % MAGENTO_HOST
	CONSUMER_KEY = '1fa23d38e3152f8ae4bb62dac0697185'
	CONSUMER_SECRET = '2bb909b904b0fadb4b318d14195e2ae0'

	def __init__(self):
		self.username = "restuser"
		self.password = "ksiksiksi123"
		self.headers = {'Accept': 'application/xml','Content-Type':'application/xml',}

		magento = OAuth1Service(
		    name               = 'abcmagento',
		    consumer_key       = ABCMagentoRESTClient.CONSUMER_KEY,
		    consumer_secret    = ABCMagentoRESTClient.CONSUMER_SECRET,
		    request_token_url  = '%s/oauth/initiate' % ABCMagentoRESTClient.MAGENTO_HOST,
		    access_token_url   = '%s/oauth/token' % ABCMagentoRESTClient.MAGENTO_HOST,
		    # Customer authorization
		    #authorize_url     = '%s/oauth/authorize' % MAGENTO_HOST,
		    # Admin authorize url depending on admin url
		    authorize_url      = '%s/admin/oauth_authorize' % ABCMagentoRESTClient.MAGENTO_HOST,
		    base_url           = ABCMagentoRESTClient.MAGENTO_API_BASE
		)

		request_token, request_token_secret = magento.get_request_token(method='POST', params={'oauth_callback': 'oob'})
		print request_token
		# authorize us
		authorize_url = magento.get_authorize_url(request_token)
		print authorize_url
		#code = raw_input('Paste Code from browser: ')

		r = requests.post( authorize_url )
		#print r.content

		# see if we have errors
		self.exceptionRequest(r)

		html = r.content
		parsed_html = BeautifulSoup(html)
		adminhtml = ''
		if(parsed_html.body.find('input', attrs={'name':'form_key'}) != None):
		    form_key = parsed_html.body.find('input', attrs={'name':'form_key'})['value']
		    d = {"login[username]":self.username,"login[password]":self.password,"form_key":form_key,"form_key":form_key, "oauth_token":request_token}
		    r = requests.post( ABCMagentoRESTClient.MAGENTO_LOGIN_URL, data=d )
			#self.exceptionRequest(r)
		    #print r.content
		    #print r.headers['Set-Cookie'].split(';')[0].split("=")[1]
		    adminhtml = r.headers['Set-Cookie'].split(';')[0]
		    html = r.content
		    parsed_html = BeautifulSoup(html)

		verify_code = ''

		if(parsed_html.body.find('button', attrs={'title':'Authorize'}) != None):
		    MAGENTO_OAUTH_CONFIRM_URL = '%s/index.php/admin/oauth_authorize/confirm/?oauth_token=%s' % ( ABCMagentoRESTClient.MAGENTO_HOST, request_token )    #r = requests.get( authorize_url)
		    h = {
		            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
		            "Accept-Language": "en-US,en;q=0.8",
		            "Accept-Encoding": "gzip, deflate, sdch",
		            "Upgrade-Insecure-Requests": "1",
		            "User-Agent":"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
		            "Cookie": adminhtml,
		        }
		    r = requests.get(MAGENTO_OAUTH_CONFIRM_URL, headers=h)
		    #print r.content
		    self.exceptionRequest(r)
		    html = r.content
		    parsed_html = BeautifulSoup(html)
		    verify_code = parsed_html.body.find('p', attrs={'style':'font-size: 14px;'}).text.split(':')[1].strip(' ')

		if(verify_code == ''):
		    print "failed to get verify code"
		    exit()
		print verify_code

		self.session = magento.get_auth_session(request_token, request_token_secret, method='POST', data={'oauth_verifier':verify_code})
		print self.session

	def exceptionRequest(self, r):
		if r.status_code != 200:
		    print 'Request Error!'
		    print r.text
		    quit()

	def retrieveCategories(self):
		r = self.session.get(
		    'abcwarehouse/categories',
		    #'products/1/categories',
		    #'customers',
		    #'stockitems',
		    #'products?filter[1][attribute]=entity_id&filter[1][gt]=4'
		    headers=self.headers,
		    #header_auth=True,
		)
		self.exceptionRequest(r)
		print r.content
		return r.content

	def deleteCategoryById(self, categoryId):
		r = self.session.delete(
			'abcwarehouse/categories/%s' % categoryId,
			headers=self.headers,
			header_auth=True,)
		self.exceptionRequest(r)
		print r.content
		return r.content

	def createCategory(self,d):
		r = self.session.post(
		    'abcwarehouse/categories',
		    header_auth=True,
		    headers=self.headers,
		    data = d
		)
		self.exceptionRequest(r)
		print r.content
		return r.content

	def createProduct(self, p):
		#create product entity
		r = self.session.post(
		    'products',
		    header_auth=True,
		    headers=self.headers,
		    data = p
		)
		self.exceptionRequest(r)
		return r

	def bindProduct2Category(self, r, c):
		#bind category
		for categoryXML in c:
			url = "products/%s/categories" % r.headers['Location'].split('/')[4]
			r = self.session.post(
			    url,
			    header_auth=True,
			    headers=self.headers,
			    data = categoryXML
			)
			self.exceptionRequest(r)
		return True

	def bindImage2Product(self, r, p):
		#create product entity
		r = self.session.post(
		    'products/%s/images'% r.headers['Location'].split('/')[4],
		    header_auth=True,
		    headers=self.headers,
		    data = p
		)
		self.exceptionRequest(r)
		return r

	def updateImageInfo(self, r, p):
		#create product entity
		r = self.session.put(
		    'products/%s/images/%s'% (r.headers['Location'].split('/')[4], r.headers['Location'].split('/')[6]),
		    header_auth=True,
		    headers=self.headers,
		    data = p
		)
		self.exceptionRequest(r)
		return r