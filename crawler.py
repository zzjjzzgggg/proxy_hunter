#! /usr/bin/env python3
#encoding: utf-8

from iotools import *
from mytools import *
from basecrawler import *
from proxydao import ProxyDAO
from settings import *
from client import ProxyHunterClient

class PHRequest(CommonRequest):
	def __init__(self, url, timeout=8):
		super(PHRequest, self).__init__(url, timeout)


class ProxyHunter(BaseCrawler):
	def __init__(self, proxy=None, max_concurrent=30):
		super(ProxyHunter, self).__init__(max_concurrent)
		self.client = ProxyHunterClient()
		self.dao = ProxyDAO()
		self.proxy_tme = {TP_HTTP:[], TP_HTTPS:[]}
		self.proxy_buf = set()

	def dispatch(self):
		LOG_INFO("Testing specified proxies ...")
		for proxy in PROXIES: # first test specified proxies
			self.issue_new_request_with_proxy(proxy) 
		LOG_INFO("Testing database proxies ...")
		for proxy in self.dao.getAllProxies(): # second test existing proxies
			self.issue_new_request_with_proxy(proxy) 
		LOG_INFO("Testing wild proxies ...")
		for url, encode, tp in PROXY_SRCS: # last test new proxies
			self.issue_request(url, encode, tp)
	
	def save(self):
		LOG_INFO('Http: %d, Https: %d' % (len(self.proxy_tme[TP_HTTP]), len(self.proxy_tme[TP_HTTPS])))
		for tp,name,saver in ((TP_HTTP,'http.dat',self.dao.saveHttpProxies), (TP_HTTPS,'https.dat',self.dao.saveHttpsProxies)):
			proxies = self.proxy_tme[tp]
			if len(proxies)>0:
				proxies.sort(key=lambda x: x[1])
				saveList(proxies, name)
				saver(proxies)
		LOG_INFO("Summary:")
		self.dao.info()

	def handle_ok(self, req):
		if req.type == TP_XML:
			for url in self.client.parse_xml(req):
				self.issue_request(url, req.encode, TP_LNK)
		elif req.type == TP_LNK:
			for proxy in self.client.parse_html(req):
				self.issue_new_request_with_proxy(proxy)
		elif req.type == TP_HTTP or req.type == TP_HTTPS:
			tme = self.client.verify_request(req)
			if tme < 0: return
			req.tme_sum += tme
			if req.test_cnt < len(TESTS[req.type]): # not the last test
				self.issue_next_request(req, TESTS[req.type][req.test_cnt])
			else: # test finshed
				tme = req.tme_sum/abs(req.test_cnt)
				self.proxy_tme[req.type].append((req.proxy, tme))

	def issue_request(self, url, encode, req_type):
		req = PHRequest(url)
		req.type = req_type
		req.encode = encode
		self.send(req)
	
	def issue_new_request_with_proxy(self, proxy):
		if proxy in self.proxy_buf: return
		self.proxy_buf.add(proxy)
		for tp in (TP_HTTP, TP_HTTPS):
			if len(TESTS[tp]) == 0: continue
			url, encode, kwd = TESTS[tp][0]
			req = PHRequest(url)
			req.encode, req.kwd, req.proxy = encode, kwd, proxy
			req.type = tp
			req.tme_sum = 0
			req.test_cnt = 1 # the first test
			req.set_proxy(proxy)
			self.send(req)
	
	def issue_next_request(self, req, next_test):
		req.prior = True
		req.retry = 3
		req.set_url(next_test[0])
		req.encode = next_test[1]
		req.kwd = next_test[2]
		req.test_cnt += 1
		self.send(req)


if __name__=='__main__':
	try:
		timer=Timer()
		while True:
			LOG_INFO("Processing ...")
			timer.tick()
			hunter = ProxyHunter()
			hunter.run()
			LOG_INFO("Saving ...")
			hunter.save()
			LOG_INFO("Cost time "+timer.tmstr())
			LOG_INFO("Sleeping 4 hrs ...")
			time.sleep(4*3600)
	except Exception as e:
		LOG_EXCEPTION(e)

