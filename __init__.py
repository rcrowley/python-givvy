import urllib
import hashlib
from xml.dom import minidom

class Givvy(object):

	ENDPOINT = 'http://www.givvy.com/api'

	def __init__(self, api_key, api_secret):
		self.api_key = api_key
		self.api_secret = api_secret
		self.api_session = False

	def authNewSession(self):
		rsp = self._send('authNewSession', perms='r')
		if 'ok' != rsp.getAttribute('stat'): return False
		self.api_session = _xml_text(rsp.getElementsByTagName(
			'api-session')[0])
		return True
	def authCheckSession(self):
		if not self.api_session: return False
		rsp = self._send('authCheckSession', api_session=self.api_session)
		if 'ok' == rsp.getAttribute('stat'): return True
		self.api_session = False
		return False
	def authEndSession(self):
		if not self.api_session: return False
		rsp = self._send('authEndSession', api_session=self.api_session)
		return 'ok' == rsp.getAttribute('stat')

	def search(self, **kw):
		if not self.api_session: return False
		rsp = self._send('search', **kw)
		if 'ok' != rsp.getAttribute('stat'): return False
		out = []
		for charity in rsp.getElementsByTagName('charity'):
			d = {}
			for n in charity.childNodes:
				if n.ELEMENT_NODE == n.nodeType: d[n.nodeName] = _xml_text(n)
			out.append(d)
		return out

	def charityGet(self, ein):
		if not self.api_session: return False
		rsp = self._send('charityGet', ein=ein)
		if 'ok' != rsp.getAttribute('stat'): return False
		out = {}
		for n in rsp.getElementsByTagName('charity')[0].childNodes:
			if n.ELEMENT_NODE == n.nodeType: out[n.nodeName] = _xml_text(n)
		return out

	def _send(self, method, **kw):
		params = {'api-key': self.api_key}
		for k in kw: params[str(k).replace('_', '-')] = str(kw[k])
		if self.api_session: params['api-session'] = self.api_session
		return minidom.parseString(urllib.urlopen('%s/%s?%s&api-sig=%s' % (
			self.ENDPOINT,
			method,
			urllib.urlencode(params),
			self._sign(params)
		)).read()).documentElement

	def _sign(self, params):
		keys = params.keys()
		keys.sort()
		s = self.api_secret
		for k in keys: s = '%s%s%s' % (s, str(k), str(params[k]))
		return hashlib.md5(s).hexdigest()

def _xml_text(node):
	s = ''
	for n in node.childNodes:
		if n.TEXT_NODE == n.nodeType: s = '%s%s' % (s, n.data)
	return s.strip()