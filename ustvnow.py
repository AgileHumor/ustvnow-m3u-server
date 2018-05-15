'''
	ustvnow

'''
import sys
import requests
import cookielib
import re
import json
import os
import sys
import random
import urllib, urllib2
from xml.dom import minidom
from time import time
from datetime import datetime, timedelta

def robust_decode(bs):
    '''Takes a byte string as param and convert it into a unicode one. First tries UTF8, and fallback to Latin1 if it fails'''
    bs.decode(errors='replace')
    cr = None
    try:
        cr = bs.decode('utf8')
    except UnicodeDecodeError:
        cr = bs.decode('latin1')
    return cr

class Ustvnow:
	__BASE_URL = 'http://m.ustvnow.com'
	def __init__(self, user, password):
		self.user = user
		self.password = password
		self.mBASE_URL = 'http://m-api.ustvnow.com'
		self.mcBASE_URL = 'http://mc.ustvnow.com'
		self.mlBASE_URL = 'https://watch.ustvnow.com'

	def get_chan_new(self, dologin=True):
		if dologin:
			self._login()

		result = ""

		self.passkey = self._get_passkey()
		content = self._get_json('gtv/1/live/listchannels', {'token': self.token})
#		content = self._get_json('gtv/1/live/playingnow', {'token': self.token})
		channels = []

		results = content['results']['streamnames'];
		result += "#EXTM3U\n"
#		print json.dumps(content);

		for i in results:
			scode = i['scode']
			name = i['sname']
	
			if name == "ABC":
				tvgname = "WHTM"
			elif name == "BBCA":
				tvgname = "BBC America"
			elif name == "CBS":
				tvgname = "WHP"
			elif name == "CW":
				tvgname = "WXBU"
			elif name == "Discovery Channel":
				tvgname = "The Discovery Channel"
			elif name == "FOX":
				tvgname = "WPMT"
			elif name == "My9":
				tvgname = "WHVLLP (WHVL-LP)"
			elif name == "NBC":
				tvgname = "WGAL"
			elif name == "PBS":
				tvgname = "WPSU"
			elif name == "SundanceTV":
				tvgname = "SundanceTV HD"
			elif name == "USA":
				tvgname = "USA Network HD"
			elif name == "National Geographic Channel":
				tvgname = "National Geographic HD"
			else:
				tvgname = name
				
			icon = self.__BASE_URL + '/' + i['img']
			url = "http://m.ustvnow.com/stream/1/live/view?scode="+scode+"&token="+self.token+"&br_n=Firefox&pr=ec&tr=expired&pl=vjs&pd=1&br_n=Firefox&br_v=54&br_d=desktop"
			json = self._get_json('stream/1/live/view', {'token': self.token, 'key': self.passkey, 'scode': i['scode']})
			stream = json['stream']
			URL = stream.replace('smil:', 'mp4:').replace('USTVNOW1', 'USTVNOW').replace('USTVNOW', 'USTVNOW' + str(2))
			result += '#EXTINF:0, tvg-name="' + tvgname + '" tvg-logo="' + icon + '" group-title="High", ' + name + '\n';
			result += URL+"\n"
		return(result.strip("\n"))


	def get_channels(self, dologin=True):
		if dologin:
			self._login()

		content = self._get_json('gtv/1/live/listchannels', {'token': self.token})
		channels = []
		
		#print json.dumps(content);
   	
		results = content['results']['streamnames'];
    	
		for i in results:
			channels.append({
				'name': i['sname'], 
				'sname' : i['callsign'],
				'icon': self.__BASE_URL + '/' + i['img']
				})
    	
		return channels 
       
        
	def get_guide(self):
		self._login()
		content = self._get_json('gtv/1/live/channelguide', {'token': self.token})
		results = content['results'];

		now = time();

		doc = minidom.Document();
		base = doc.createElement('tv');
		base.setAttribute("cache-version", str(now));
		base.setAttribute("cache-time", str(now));
		base.setAttribute("generator-info-name", "IPTV Plugin");
		base.setAttribute("generator-info-url", "http://www.xmltv.org/");
		doc.appendChild(base)
		
		channels = self.get_channels(dologin=False);

		for channel in channels:
	
			name = channel['name'];
			id = channel['sname'];
		
			c_entry = doc.createElement('channel');
			c_entry.setAttribute("id", id);
			base.appendChild(c_entry)
		
		
			dn_entry = doc.createElement('display-name');
			dn_entry_content = doc.createTextNode(name);
			dn_entry.appendChild(dn_entry_content);
			c_entry.appendChild(dn_entry);
			
			dn_entry = doc.createElement('display-name');
			dn_entry_content = doc.createTextNode(id);
			dn_entry.appendChild(dn_entry_content);
			c_entry.appendChild(dn_entry);
			
			icon_entry = doc.createElement('icon');
			icon_entry.setAttribute("src", channel['icon']);
			c_entry.appendChild(icon_entry);
			
			
		for programme in results:
	
			start_time 	= datetime.fromtimestamp(float(programme['ut_start']));
			stop_time	= start_time + timedelta(seconds=int(programme['guideremainingtime']));
					
		
			pg_entry = doc.createElement('programme');
			pg_entry.setAttribute("start", start_time.strftime('%Y%m%d%H%M%S -0700'));
			pg_entry.setAttribute("stop", stop_time.strftime('%Y%m%d%H%M%S -0700'));
			pg_entry.setAttribute("channel", programme['callsign']);
			base.appendChild(pg_entry);
		
			t_entry = doc.createElement('title');
			t_entry.setAttribute("lang", "en");
			t_entry_content = doc.createTextNode(programme['title']);
			t_entry.appendChild(t_entry_content);
			pg_entry.appendChild(t_entry);
			
			st_entry = doc.createElement('sub-title');
			st_entry.setAttribute("lang", "en");
			st_entry_content = doc.createTextNode(programme['episode_title']);
			st_entry.appendChild(st_entry_content);
			pg_entry.appendChild(st_entry);
		
			d_entry = doc.createElement('desc');
			d_entry.setAttribute("lang", "en");
			d_entry_content = doc.createTextNode(programme['synopsis']);
			d_entry.appendChild(d_entry_content);
			pg_entry.appendChild(d_entry);
		
			dt_entry = doc.createElement('date');
			dt_entry_content = doc.createTextNode(start_time.strftime('%Y%m%d'));
			dt_entry.appendChild(dt_entry_content);
			pg_entry.appendChild(dt_entry);
		
			c_entry = doc.createElement('category');
			c_entry_content = doc.createTextNode(programme['xcdrappname']);
			c_entry.appendChild(c_entry_content);
			pg_entry.appendChild(c_entry);
			
			
			en_entry = doc.createElement('episode-num');
			en_entry.setAttribute('system', 'dd_progid');
			en_entry_content = doc.createTextNode(programme['content_id']);
			en_entry.appendChild(en_entry_content);
			pg_entry.appendChild(en_entry);
		
	
			i_entry = doc.createElement('icon');
			i_entry.setAttribute("src", self.__BASE_URL + '/' + programme['img']);
			pg_entry.appendChild(i_entry);
		
		return doc  

	def _build_url(self, path, queries={}):
		if queries:
			query = urllib.urlencode(queries)
			return '%s/%s?%s' % (self.mBASE_URL, path, query)
		else:
			return '%s/%s' % (self.mBASE_URL, path)

	def _build_json(self, path, queries={}):
		if queries:
			query = urllib.urlencode(queries)
			return '%s/%s?%s' % (self.mBASE_URL, path, query)
		else:
			return '%s/%s' % (self.mBASE_URL, path)

	def _fetch(self, url, form_data=False):
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		if form_data:
			req = urllib2.Request(url, form_data)
		else:
			req = url
		try:
			response = opener.open(req)
			return response
		except urllib2.URLError, e:
			return False
		
	def _get_json(self, path, queries={}):
		content = False
		url = self._build_json(path, queries)
		response = self._fetch(url)
		if response:
			content = json.loads(response.read())
		else:
			content = False
		return content
		
	def _get_html(self, path, queries={}):
		html = False
		url = self._build_url(path, queries)

		response = self._fetch(url)
		if response:
			html = response.read()
		else:
			html = False
		return html
		
	#TODO this func
	def get_link(self, sname, quality=1, stream_type='rtmp'):
		self._login()
		
		self.__BASE_URL = 'http://lv2.ustvnow.com';
		html = self._get_html('iphone_ajax', {'tab': 'iphone_playingnow', 
											  'token': self.token})
		channel = re.search('class="panel".+?images\/' + sname + '.+?class="nowplaying_itemdesc".+?<.+?href="rtmp(.+?)">View<\/a>', html, re.DOTALL);
		
		if channel == None:
			return None;
		
		url = channel.group(1);
		url = '%s%s%d' % (stream_type, url[:-1], quality)
		
		return url    

	def _get_passkey(self):
		passkey = self._get_json('gtv/1/live/viewdvrlist', {'token': self.token})['globalparams']['passkey']
		return passkey


	def _login(self):
		with requests.Session() as s:
				   
			url=self.mlBASE_URL + "/account/signin"
			r = s.get(url)
			html = r.text
			html = ' '.join(html.split())
			ultimate_regexp = "(?i)<\/?\w+((\s+\w+(\s*=\s*(?:\".*?\"|'.*?'|[^'\">\s]+))?)+\s*|\s*)\/?>"
			for match in re.finditer(ultimate_regexp, html):
				i = repr(match.group())
				if '<input type="hidden" name="csrf_ustvnow" value="' in i:
					csrf = i.replace('<input type="hidden" name="csrf_ustvnow" value="','').replace('">','')
					csrf = str(csrf).replace("u'","").replace("'","")
			
			url = self.mlBASE_URL + "/account/login"
			payload = {'csrf_ustvnow': csrf, 'signin_email': self.user, 'signin_password':self.password, 'signin_remember':'1'}
			r = s.post(url, data=payload)
			html = r.text
			html = ' '.join(html.split())
			html = html[html.find('var token = "')+len('var token = "'):]
			html = html[:html.find(';')-1]
			token = str(html)
			self.token = token
