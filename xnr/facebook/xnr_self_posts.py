#!/usr/bin/env python
#encoding: utf-8

from selenium import webdriver
import requests
import time
from pyvirtualdisplay import Display
from launcher import Launcher
from elasticsearch import Elasticsearch
import re
import random
from datetime import datetime, timedelta
import sys
sys.path.append('../')
from timed_python_files import new_facebook_xnr_flow_text_mappings as mapping

display = Display(visible=0, size=(1024,768))
display.start()

endDate = '2017-10-25'
dateList = []
for i in range(0,11):
	date = datetime.strptime(endDate,"%Y-%m-%d") - timedelta(days=i)
	dateList.append(datetime.strftime(date,"%Y-%m-%d"))

# 获取已创建xnr的数据
es = Elasticsearch([{'host':'219.224.134.213','port':9205}])
xnrData = []
query_body = {
		"query":
		{
			"match": {
				"create_status": 2
			}
		}
}
res = es.search(index='fb_xnr', doc_type='user', body=query_body, request_timeout=100)
hits = res['hits']['hits']
for each in hits:
	if each['_source']['create_status'] == 2:
		xnrData.append(each['_source'])

for xnr in xnrData:
	account = xnr['fb_mail_account']
	password = xnr['password']

	# 登录
	driver = webdriver.Firefox()
	driver.get('https://www.facebook.com/')
	driver.find_element_by_xpath('//input[@id="email"]').send_keys(account)
	driver.find_element_by_xpath('//input[@id="pass"]').send_keys(password)
	driver.find_element_by_xpath('//input[@data-testid="royal_login_button"]').click()
	time.sleep(2)
	# 退出通知弹窗进入页面
	try:
		driver.find_element_by_xpath('//div[@class="_n8 _3qx uiLayer _3qw"]').click()
	except:
		pass
	time.sleep(1)
	# 点掉进入主页之后的提醒
	try:
		driver.find_element_by_xpath('//a[@action="cancel"]').click()
	except Exception as e:
		pass
	time.sleep(1)
	driver.find_element_by_xpath('//a[@title="个人主页"]').click()
	time.sleep(1)
	#加载更多
	length=100
	for i in range(0,20):
		js="var q=document.documentElement.scrollTop="+str(length) 
		driver.execute_script(js) 
		time.sleep(1)
		length += 400

	# 获取数据
	postsNum = 0
	for div in driver.find_elements_by_xpath('//div[@id="recent_capsule_container"]/ol/div'):
		for post in div.find_elements_by_xpath('./div'):
			postsNum += 1

	for div in driver.find_elements_by_xpath('//div[@id="recent_capsule_container"]/ol/div'):
		for post in div.find_elements_by_xpath('./div'):
			xnr_user_no = xnr['xnr_user_no']
			uid = xnr['uid']
			try:
				text = post.find_element_by_xpath('./div/div[2]/div/div[2]/div[2]/p').text
			except:
				text = None
			try:
				picture_url = post.find_element_by_xpath('./div/div[2]/div/div[2]/div[3]//img').get_attribute('src')
			except:
				picture_url = None
			vedio_url = None
			user_friendsnum = driver.find_element_by_xpath('//a[@data-tab-key="friends"]/span[1]').text
			user_followersum = None
			weibos_sum = postsNum
			try:
				fid = re.findall(re.compile('fbid=(\d+)'),post.find_element_by_xpath('./div/div[2]/div/div[2]/div[1]/div[1]/div/div[2]/div/div/div[2]/div/span[3]/span/a').get_attribute('href'))[0]
			except:
				fid = re.findall(re.compile('posts/(\d+)'),post.find_element_by_xpath('./div/div[2]/div/div[2]/div[1]/div[1]/div/div[2]/div/div/div[2]/div/span[3]/span/a').get_attribute('href'))[0]
			ip = None
			#timestamp = post.find_element_by_xpath('./div/div[2]/div/div[2]/div[1]/div[1]/div/div[2]/div/div/div[2]/div/span[3]/span/a/abbr').get_attribute('data-utime')
			timestamp = int(time.mktime(time.strptime(dateList[random.randint(1,10)],"%Y-%m-%d")))
			for each in driver.find_elements_by_xpath('//div[@class="_50f3"]'):
				if u'所在地' in each.text:
					geo = each.find_element_by_xpath('./a').text

			try:
				directed_uid = re.findall(re.compile('id=(\d+)'),post.find_element_by_xpath('./div/div[2]/div/div[2]/div[3]/div[2]/div/div/div/span/span/a').get_attribute('data-hovercard'))[0]
			except:
				directed_uid = None
			try:
				directed_uname = post.find_element_by_xpath('./div/div[2]/div/div[2]/div[3]/div[2]/div/div/div/span/span/a').text
			except:
				directed_uname = None
			if directed_uid:
				message_type = 2
			else:
				message_type = 1
			root_uid = directed_uid
			try:
				root_mid = re.findall(re.compile(r'fbid=(\d+)'),post.find_element_by_xpath('./div/div[2]/div/div[2]/div[3]/div[2]/div/div/div/div/span/span/a'))[0]
				if not root_mid:
					root_mid = re.findall(re.compile(r'posts/(\d+)'),post.find_element_by_xpath('./div/div[2]/div/div[2]/div[3]/div[2]/div/div/div/div/span/span/a'))[0]
				if not root_mid:
					root_mid = re.findall(re.compile(r'photos/(\d+)'),post.find_element_by_xpath('./div/div[2]/div/div[2]/div[3]/div[2]/div/div/div/div/span/span/a'))[0]
			except:
				root_mid = None
			try:
				origin_text = post.find_element_by_xpath('./div/div[2]/div/div[2]/div[3]/div[2]/div/div/div/div[2]').text
			except:
				origin_text = None

			dict = {"xnr_user_no":xnr_user_no, "uid":uid, "text":text,\
					 "picture_url":picture_url, "vedio_url":vedio_url,\
					  "user_friendsnum":user_friendsnum, "user_followersum":user_followersum,\
					   "weibos_sum":weibos_sum, "fid":fid, "ip":ip, "timestamp":timestamp,\
					    "geo":geo, "message_type":message_type, "directed_uid":directed_uid,\
					      "directed_uname":directed_uname, "root_uid":root_uid, "root_mid":root_mid,\
					       "origin_text":origin_text}
			print(dict)

			index_name = mapping.new_xnr_flow_text_index_name_pre + time.strftime("%Y-%m-%d",time.localtime(dict['timestamp']))
			mapping.new_facebook_xnr_flow_text_mappings(index_name)
			time.sleep(2)
			es.index(index=index_name, doc_type=mapping.new_xnr_flow_text_index_type, id=dict['fid'], body=dict)

	# 退出
	driver.close()



















