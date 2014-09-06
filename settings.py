#! /usr/bin/env python3
#encoding: utf-8

import time
import logging
from logging import Formatter
from logging import FileHandler, StreamHandler

##############################################################
##############################################################
## logging

formatter = Formatter("[%(asctime)s][%(levelname)s]: %(message)s", "%b %d %H:%M:%S")

stream_handler = StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = FileHandler('proxy_hunter.log','w')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

logger = logging.getLogger()
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

def LOG_DEBUG(msg):
    return logger.debug(msg)

def LOG_INFO(msg):
    return logger.info(msg)

def LOG_WARNING(msg):
    return logger.warning(msg)

def LOG_ERROR(msg):
    return logger.error(msg)

def LOG_CRITICAL(msg):
    return logger.critical(msg)

def LOG_EXCEPTION(e):
    return logger.exception(e)


TP_LNK = 0
TP_XML = 1
TP_HTTP = 2
TP_HTTPS = 3

PROXIES=[
	'202.117.54.254:3128',
	'202.117.54.249:808',
]

PROXY_SRCS=[
	('http://www.xici.net.co/nn/1', 'utf8', TP_LNK), 
	('http://www.xici.net.co/nn/2', 'utf8', TP_LNK), 
	('http://www.xici.net.co/nt/1', 'utf8', TP_LNK), 
	('http://www.xici.net.co/nt/2', 'utf8', TP_LNK), 
	('http://www.xici.net.co/wn/1', 'utf8', TP_LNK), 
	('http://www.xici.net.co/wn/2', 'utf8', TP_LNK), 
	('http://www.xici.net.co/wt/1', 'utf8', TP_LNK), 
	('http://www.xici.net.co/wt/2', 'utf8', TP_LNK), 
	('http://www.kuaidaili.com/proxylist/1/', 'utf8', TP_LNK), 
	('http://www.kuaidaili.com/proxylist/2/', 'utf8', TP_LNK), 
	('http://www.kuaidaili.com/proxylist/3/', 'utf8', TP_LNK), 
	('http://www.kuaidaili.com/proxylist/4/', 'utf8', TP_LNK), 
	('http://www.kuaidaili.com/proxylist/5/', 'utf8', TP_LNK), 
	('http://www.kuaidaili.com/proxylist/6/', 'utf8', TP_LNK), 
	('http://www.kuaidaili.com/proxylist/7/', 'utf8', TP_LNK), 
	('http://www.kuaidaili.com/proxylist/8/', 'utf8', TP_LNK), 
	('http://www.kuaidaili.com/proxylist/9/', 'utf8', TP_LNK), 
	('http://www.kuaidaili.com/proxylist/10/', 'utf8', TP_LNK), 
	('http://cn-proxy.com', 'utf8', TP_LNK), 
	('http://ip.zdaye.com/?pageid=1', 'gb2312', TP_LNK), 
	('http://ip.zdaye.com/?pageid=2', 'gb2312', TP_LNK), 
	('http://ip.zdaye.com/?pageid=3', 'gb2312', TP_LNK), 
	('http://ip.zdaye.com/?pageid=4', 'gb2312', TP_LNK), 
	('http://ip.zdaye.com/?pageid=5', 'gb2312', TP_LNK), 
	('http://ip.zdaye.com/?pageid=6', 'gb2312', TP_LNK), 
	('http://ip.zdaye.com/?pageid=7', 'gb2312', TP_LNK), 
	('http://ip.zdaye.com/?pageid=8', 'gb2312', TP_LNK), 
	('http://ip.zdaye.com/?pageid=9', 'gb2312', TP_LNK), 
	('http://ip.zdaye.com/?pageid=10', 'gb2312', TP_LNK), 
	('http://www.56ads.com/data/rss/2.xml', 'gb2312', TP_XML), 
]

TESTS = {
	TP_HTTP: (
		('http://www.baidu.com', 'utf8', '百度一下'),
		('http://dongxi.douban.com', 'utf8', '豆瓣东西'),
	),
	TP_HTTPS: ()
}

