#! /usr/bin/env python
#encoding: utf-8

from httpclient import HttpClient
import feedparser
import time
import re
from queue import Queue
import threading
from proxydao import ProxyDAO

rex_proxy=re.compile('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[^\d]+(\d+)')
lock=threading.Lock()
class ProxyHunter:
	def __init__(self):
		self.client=HttpClient()
		self.dao=ProxyDAO()
		self.queue=Queue(500)
		self.httpproxies=[]
		self.httpsproxies=[]
		self.proxybuf=set()
		for i in range(10): SpeedTester(self.queue, self.httpproxies, self.httpsproxies).start()
	
	def clear(self):
		while self.httpproxies: self.httpproxies.pop()
		while self.httpsproxies: self.httpsproxies.pop()
		self.proxybuf=self.dao.getAll()
		#self.proxybuf.add('202.117.54.249:808')
		#self.proxybuf.add('202.117.54.254:3128')
		for proxy in self.proxybuf: self.queue.put(proxy)
	
	def parse_proxy(self, html):
		if html is None: return
		for ip,port in rex_proxy.findall(html): 
			proxy = '%s:%s' % (ip,port)
			if proxy in self.proxybuf: continue
			self.proxybuf.add(proxy)
			self.queue.put(proxy)
		
	def hunt_rss(self, src, encode):
		self.client.encode=encode
		xml=self.client.get(src)
		if xml is None: return
		rss=feedparser.parse(xml)
		for entry in rss.entries:
			try:
				if time.time()-time.mktime(entry.published_parsed)<7*24*3600: 
					self.parse_proxy(self.client.get(entry.link))
			except Exception as e: print(e)
	
	def hunt_html(self, src, encode):
		self.client.encode=encode
		self.parse_proxy(self.client.get(src))
	
	def save(self):
		print("Saving...")
		# http
		with lock: proxies=sorted(self.httpproxies, key=lambda x: x[1])
		print("Found http proxies: %d" % len(proxies))
		if len(proxies)==0: return
		self.dao.saveHttpProxies(proxies)
		fw=open('http.dat', 'w')
		fw.write('#update time: %s\n' % time.ctime())
		for proxy, speed in proxies:fw.write('%s\t%.2f\n' % (proxy, speed))
		fw.close()
		# https
		with lock: proxies=sorted(self.httpsproxies, key=lambda x: x[1])
		print("Found https proxies: %d" % len(proxies))
		if len(proxies)==0: return
		self.dao.saveHttpsProxies(proxies)
		fw=open('https.dat', 'w')
		fw.write('#update time: %s\n' % time.ctime())
		for proxy, speed in proxies:fw.write('%s\t%.2f\n' % (proxy, speed))
		fw.close()
	
	def run(self):
		srcs=[
			('http://www.xici.net.co/nn/', 'utf-8', self.hunt_html), 
			('http://www.xici.net.co/nt/', 'utf-8', self.hunt_html), 
			('http://www.xici.net.co/wn/', 'utf-8', self.hunt_html), 
			('http://www.xici.net.co/wt/', 'utf-8', self.hunt_html), 
			('http://www.56ads.com/data/rss/2.xml', 'gb2312', self.hunt_rss), 
			('http://www.veryhuo.com/res/ip/page_1.php', 'gb2312', self.hunt_html),
			('http://www.veryhuo.com/res/ip/page_2.php', 'gb2312', self.hunt_html),
			('http://www.veryhuo.com/res/ip/page_3.php', 'gb2312', self.hunt_html),
			('http://www.veryhuo.com/res/ip/page_4.php', 'gb2312', self.hunt_html),
			('http://www.veryhuo.com/res/ip/page_5.php', 'gb2312', self.hunt_html),
		]
		while True:
			self.clear()
			for item in srcs: 
				fun=item[2]
				fun(item[0], item[1])
			self.queue.join()
			time.sleep(10)
			self.save()
			print(time.ctime(), "Done. Sleeping...")
			time.sleep(8*3600) # sleep 8 hours

class SpeedTester(threading.Thread):
	def __init__(self, queue, hpproxies, hsproxies):
		threading.Thread.__init__(self)
		self.daemon=True
		self.client=HttpClient()
		self.queue=queue
		self.httpproxies, self.httpsproxies=hpproxies, hsproxies

	def test_speed(self, proxy):
		httpdelay = httpsdelay = -1
		#if not self.client.ping('http://www.douban.com', '豆瓣', proxy): httpdelay = -1
		#if not self.client.ping('http://www.xiami.com', '虾米', proxy): httpdelay = -1
		if not self.client.ping('http://about.pinterest.com', 'Pinterest', proxy): httpdelay = -1
		else: httpdelay = self.client.speed
		if not self.client.ping('https://www.pinterest.com/login/', 'Pinterest', proxy): httpsdelay = -1
		else: httpsdelay = self.client.speed
		return (httpdelay, httpsdelay)
	
	def run(self):
		while True:
			proxy=self.queue.get()
			hpdelay, hsdelay=self.test_speed(proxy)
			if hpdelay>0 and hpdelay<10:
				print('http', proxy, hpdelay)
				with lock: self.httpproxies.append((proxy, hpdelay))
			if hsdelay>0 and hsdelay<10:
				print('https', proxy, hsdelay)
				with lock: self.httpsproxies.append((proxy, hsdelay))
			self.queue.task_done()

if __name__=='__main__':
	hunter=ProxyHunter()
	hunter.run()
