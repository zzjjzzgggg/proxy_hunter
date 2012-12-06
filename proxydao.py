#! /usr/bin/env python
#coding=utf-8

import pymongo
import random

db=pymongo.Connection('192.168.4.238', 27037).proxy

def saveHttpProxies(proxies):
	db.http.remove()
	for i, proxy in enumerate(proxies): db.http.save({'_id':i+1, 'proxy':proxy[0], 'delay':proxy[1]})

def saveHttpsProxies(proxies):
	db.https.remove()
	for i, proxy in enumerate(proxies): db.https.save({'_id':i+1, 'proxy':proxy[0], 'delay':proxy[1]})

def count():
	print(db.proxy.count())

def getAll():
	rst=set()
	for proxy in db.http.find(): rst.add(proxy['proxy'])
	for proxy in db.https.find(): rst.add(proxy['proxy'])
	return rst

if __name__=='__main__':
	print(getHttpAll())
