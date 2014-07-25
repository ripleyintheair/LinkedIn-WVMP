#uses code from http://stackoverflow.com/questions/18907503/logging-in-to-linkedin-with-python-requests-sessions

import cookielib, os, urllib, urllib2, re, string, json, datetime, threading
from bs4 import BeautifulSoup

username = "LINKEDIN USERNAME"
password = "LINKEDIN PASSWORD"

cookie_filename = "parser.cookies.txt"

cj = cookielib.MozillaCookieJar(cookie_filename)
if os.access(cookie_filename, os.F_OK):
    cj.load()
opener = urllib2.build_opener(
    urllib2.HTTPRedirectHandler(),
    urllib2.HTTPHandler(debuglevel=0),
    urllib2.HTTPSHandler(debuglevel=0),
    urllib2.HTTPCookieProcessor(cj)
)
opener.addheaders = [
    ('User-agent', ('Mozilla/4.0 (compatible; MSIE 6.0; '
                   'Windows NT 5.2; .NET CLR 1.1.4322)'))
]
html = opener.open("https://www.linkedin.com/")
soup = BeautifulSoup(html)
csrf = soup.find(id="loginCsrfParam-login")['value']
login_data = urllib.urlencode({
     'session_key': username,
     'session_password': password,
     'loginCsrfParam': csrf,
 })
html = opener.open("https://www.linkedin.com/uas/login-submit", login_data)

minutestimedelay=10
secondstimedelay=minutestimedelay*60

def f():
	mobilez = opener.open("https://touch.www.linkedin.com/li/v1/people/wvmp")
	data=json.load(mobilez)
	for x in data["wvmp"]:
		for y in x["values"]:
			t=datetime.datetime.fromtimestamp(float(y["timestamp"])/1000.)
			diff=datetime.datetime.now()-t
			if diff<datetime.timedelta(minutes=minutestimedelay):
				#send a notification
				push_data = urllib.urlencode({
					'token': 'PUSHOVER TOKEN',
					'user': 'PUSHOVER USER',
					'title': y["formattedName"],
					'message': y["headline"]
				})
				html=opener.open("https://api.pushover.net/1/messages.json",push_data)
#				On Android, you can use y["picture"] for an image
	threading.Timer(secondstimedelay,f).start()

f()

#cj.save()

#other WVMP APIs:
#desktop old: https://www.linkedin.com/wvmx/profile/viewers
#desktop new: https://www.linkedin.com/wvmx/profile/viewers_v2
#	relevant fields:
#	fmt__full_name = full name; this and timeAgo are the only ones also present when visitor is anonymous
#	headline = headline
#	fmt__location = location
#	fmt__industry = industry
#	picId = end of URL for photo; should be preceded by "https://media.licdn.com/mpr/mpr/shrink_200_200"
#	distance = degrees from you (-1 when not connected)
#	fmt_num_sharedDataCount = number of shared contacts
#	sharedConnectionids = ID number of those shared contacts
#	timeAgo = an object that contains details on the amt of time since someone visited;
#		'days' is the numerical distance from today (eg 0=today)