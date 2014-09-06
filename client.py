#! /usr/bin/env python3
#encoding: utf-8

import time, re
import feedparser


rex_proxy=re.compile('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[^\d]+(\d+)')

class ProxyHunterClient:
	def parse_html(self, req):
		proxies = set()
		html = req.get_content()
		if html is not None:
			for ip,port in rex_proxy.findall(html):
				proxies.add('%s:%s' % (ip,port))
		return proxies
		
	def parse_xml(self, req):
		links = set()
		xml=req.get_content()
		if xml is not None:
			rss=feedparser.parse(xml)
			for entry in rss.entries:
				try:
					tme = time.mktime(entry.published_parsed)
					time_delay = time.time() - tme
					if time_delay < 3*24*3600: links.add(entry.link)
				except Exception as e: print(e)
		return links
	
	def verify_request(self, req):
		html =  req.get_content()
		if html is not None and html[:1024].find(req.kwd)>=0:
			return req.get_total_time()
		return -1
	
if __name__=='__main__':
	from crawler import PHRequest
	client = ProxyHunterClient()
	req = PHRequest('http://www.xici.net.co/nn/')
	#req = PHRequest('http://www.baidu.com')
	req.encode = 'utf8'
	#req.set_proxy('202.117.54.254:3128')
	req.perform()
	rst=client.parse_html(req)
	print(rst)

