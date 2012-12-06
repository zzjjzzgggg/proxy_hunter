#! /usr/bin/env python
#encoding: utf-8

from httpclient import HttpClient
import feedparser
import time
import re
from queue import Queue
import threading
import proxydao as dao

rex_proxy=re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}[: ]\d+')
lock=threading.Lock()
class ProxyHunter:
	def __init__(self):
		self.client=HttpClient()
		self.queue=Queue(500)
		self.httpproxies=[]
		self.httpsproxies=[]
		self.proxybuf=set()
		for i in range(10): SpeedTester(self.queue, self.httpproxies, self.httpsproxies).start()
	
	def clear(self):
		while self.httpproxies: self.httpproxies.pop()
		while self.httpsproxies: self.httpsproxies.pop()
		self.proxybuf=dao.getAll()
		self.proxybuf.add('202.117.54.246:808')
		self.proxybuf.add('192.168.1.21:808')
		self.proxybuf.add('202.117.54.249:808')
		self.proxybuf.add('202.117.16.191:808')
		self.proxybuf.add('202.117.54.254:3128')
		self.proxybuf.add('202.117.54.198:8080')
		for proxy in self.proxybuf: self.queue.put(proxy)
	
	def parse_proxy(self, html):
		if html is None: return
		for rproxy in rex_proxy.findall(html): 
			proxy=rproxy.replace(' ', ':')
			if proxy in self.proxybuf: continue
			self.proxybuf.add(proxy)
			self.queue.put(proxy)
		

	def hunt_rss(self, src, encode):
		self.client.encode=encode
		xml=self.client.get(src)
		if xml is None: return
		rss=feedparser.parse(xml)
		for entry in rss.entries:
			if time.time()-time.mktime(entry.published_parsed)<5*24*3600: 
				self.parse_proxy(self.client.get(entry.link))
	
	def hunt_html(self, src, encode):
		self.client.encode=encode
		self.parse_proxy(self.client.get(src))
	
	def save(self):
		print("Saving...")
		# http
		with lock: proxies=sorted(self.httpproxies, key=lambda x: x[1])
		print("Found http proxies: %d" % len(proxies))
		if len(proxies)==0: return
		dao.saveHttpProxies(proxies)
		fw=open('http.dat', 'w')
		fw.write('#update time: %s\n' % time.ctime())
		for proxy, speed in proxies:fw.write('%s\t%.2f\n' % (proxy, speed))
		fw.close()
		# https
		with lock: proxies=sorted(self.httpsproxies, key=lambda x: x[1])
		print("Found https proxies: %d" % len(proxies))
		if len(proxies)==0: return
		dao.saveHttpsProxies(proxies)
		fw=open('https.dat', 'w')
		fw.write('#update time: %s\n' % time.ctime())
		for proxy, speed in proxies:fw.write('%s\t%.2f\n' % (proxy, speed))
		fw.close()
	
	def run(self):
		srcs=[
			('http://www.56ads.com/data/rss/2.xml', 'gb2312', self.hunt_rss), 
			('http://www.sooip.cn/e/web/?type=rss2&classid=1', 'gb2312', self.hunt_rss),
			('http://www.18daili.com/', 'utf8', self.hunt_html),
			('http://www.veryhuo.com/res/ip/', 'gb2312', self.hunt_html),
			('http://www.veryhuo.com/res/ip/page_1.php', 'gb2312', self.hunt_html),
			('http://www.veryhuo.com/res/ip/page_2.php', 'gb2312', self.hunt_html),
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
			time.sleep(2*3600)

class SpeedTester(threading.Thread):
	def __init__(self, queue, hpproxies, hsproxies):
		threading.Thread.__init__(self)
		self.daemon=True
		self.client=HttpClient()
		self.queue=queue
		self.httpproxies, self.httpsproxies=hpproxies, hsproxies

	def test_speed(self, proxy):
		httpdelay = httpsdelay = -1
		if not self.client.ping('http://www.douban.com', '豆瓣', proxy): httpdelay = -1
		if not self.client.ping('http://www.xiami.com', '虾米', proxy): httpdelay = -1
		else: httpdelay = self.client.speed
		if not self.client.ping('https://passport.baidu.com/v2/?login', '百度', proxy): httpsdelay = -1
		else: httpsdelay = self.client.speed
		return (httpdelay, httpsdelay)
	
	def run(self):
		while True:
			proxy=self.queue.get()
			hpdelay, hsdelay=self.test_speed(proxy)
			if hpdelay>0 and hpdelay<5:
				print('http', proxy, hpdelay)
				with lock: self.httpproxies.append((proxy, hpdelay))
			if hsdelay>0 and hsdelay<5:
				print('https', proxy, hsdelay)
				with lock: self.httpsproxies.append((proxy, hsdelay))
			self.queue.task_done()

if __name__=='__main__':
	hunter=ProxyHunter()
	hunter.run()
