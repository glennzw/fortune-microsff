#!/usr/bin/python
# Fortune style QoTD for @MicroSFF
# Tweet fetching code from: https://github.com/Jefferson-Henrique/GetOldTweets-python
import urllib,urllib2,json,re,datetime,sys,cookielib
from pyquery import PyQuery
import random
import time
from datetime import timedelta
import dateutil.parser

class Tweet:

	def __init__(self):
		pass

class TweetCriteria:

	def __init__(self):
		self.maxTweets = 0

	def setUsername(self, username):
		self.username = username
		return self

	def setSince(self, since):
		self.since = since
		return self

	def setUntil(self, until):
		self.until = until
		return self

	def setQuerySearch(self, querySearch):
		self.querySearch = querySearch
		return self

	def setMaxTweets(self, maxTweets):
		self.maxTweets = maxTweets
		return self

	def setTopTweets(self, topTweets):
		self.topTweets = topTweets
		return self

class TweetManager:

	def __init__(self):
		pass

	@staticmethod
	def getTweets(tweetCriteria, receiveBuffer = None, bufferLength = 100):
		refreshCursor = ''

		results = []
		resultsAux = []
		cookieJar = cookielib.CookieJar()

		if hasattr(tweetCriteria, 'username') and (tweetCriteria.username.startswith("\'") or tweetCriteria.username.startswith("\"")) and (tweetCriteria.username.endswith("\'") or tweetCriteria.username.endswith("\"")):
			tweetCriteria.username = tweetCriteria.username[1:-1]

		active = True

		while active:
			json = TweetManager.getJsonReponse(tweetCriteria, refreshCursor, cookieJar)
			if len(json['items_html'].strip()) == 0:
				break

			refreshCursor = json['min_position']
			tweets = PyQuery(json['items_html'])('div.js-stream-tweet')

			if len(tweets) == 0:
				break

			for tweetHTML in tweets:
				tweetPQ = PyQuery(tweetHTML)
				tweet = Tweet()

				usernameTweet = tweetPQ("span.username.js-action-profile-name b").text();
				#txt = re.sub(r"\s+", " ", tweetPQ("p.js-tweet-text").text().replace('# ', '#').replace('@ ', '@'));
				txt = tweetPQ("p.js-tweet-text").text()
				retweets = int(tweetPQ("span.ProfileTweet-action--retweet span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""));
				favorites = int(tweetPQ("span.ProfileTweet-action--favorite span.ProfileTweet-actionCount").attr("data-tweet-stat-count").replace(",", ""));
				dateSec = int(tweetPQ("small.time span.js-short-timestamp").attr("data-time"));
				id = tweetPQ.attr("data-tweet-id");
				permalink = tweetPQ.attr("data-permalink-path");

				geo = ''
				geoSpan = tweetPQ('span.Tweet-geo')
				if len(geoSpan) > 0:
					geo = geoSpan.attr('title')

				tweet.id = id
				tweet.permalink = 'https://twitter.com' + permalink
				tweet.username = usernameTweet
				tweet.text = txt
				tweet.date = datetime.datetime.fromtimestamp(dateSec)
				tweet.retweets = retweets
				tweet.favorites = favorites
				tweet.mentions = " ".join(re.compile('(@\\w*)').findall(tweet.text))
				tweet.hashtags = " ".join(re.compile('(#\\w*)').findall(tweet.text))
				tweet.geo = geo

				results.append(tweet)
				resultsAux.append(tweet)

				if receiveBuffer and len(resultsAux) >= bufferLength:
					receiveBuffer(resultsAux)
					resultsAux = []

				if tweetCriteria.maxTweets > 0 and len(results) >= tweetCriteria.maxTweets:
					active = False
					break


		if receiveBuffer and len(resultsAux) > 0:
			receiveBuffer(resultsAux)

		return results

	@staticmethod
	def getJsonReponse(tweetCriteria, refreshCursor, cookieJar):
		url = "https://twitter.com/i/search/timeline?f=tweets&q=%s&src=typd&max_position=%s"

		urlGetData = ''
		if hasattr(tweetCriteria, 'username'):
			urlGetData += ' from:' + tweetCriteria.username

		if hasattr(tweetCriteria, 'since'):
			urlGetData += ' since:' + tweetCriteria.since

		if hasattr(tweetCriteria, 'until'):
			urlGetData += ' until:' + tweetCriteria.until

		if hasattr(tweetCriteria, 'querySearch'):
			urlGetData += ' ' + tweetCriteria.querySearch

		if hasattr(tweetCriteria, 'topTweets'):
			if tweetCriteria.topTweets:
				url = "https://twitter.com/i/search/timeline?q=%s&src=typd&max_position=%s"

		url = url % (urllib.quote(urlGetData), refreshCursor)
		headers = [
			('Host', "twitter.com"),
			('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
			('Accept', "application/json, text/javascript, */*; q=0.01"),
			('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
			('X-Requested-With', "XMLHttpRequest"),
			('Referer', url),
			('Connection', "keep-alive")
		]

		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
		opener.addheaders = headers

		try:
			response = opener.open(url)
			jsonResponse = response.read()
		except:
			print "Twitter weird response. Try to see on browser: https://twitter.com/search?q=%s&src=typd" % urllib.quote(urlGetData)
			sys.exit()
			return

		dataJson = json.loads(jsonResponse)

		return dataJson


tws = []
def receiveBuffer(tweets):
			for t in tweets:
				#print t.text
				if t.text.startswith('"') and "**" not in t.text and "http" not in t.text:
					tws.append((t.text,t.date.strftime('%-d %B, %Y')))

def strTimeProp(start, end, format, prop):
    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(format, time.localtime(ptime))

def randomDate(start, end, prop):
    return strTimeProp(start, end, '%Y-%m-%d', prop)

if __name__ == "__main__":
  count = 5
  tweetCriteria = TweetCriteria()
  tweetCriteria.username = "MicroSFF"

  while count > 0:
    rdA = randomDate("2013-04-28", time.strftime("%Y-%m-%d"), random.random()) #Random date since first Tweet
    rdB = (dateutil.parser.parse(rdA) + timedelta(20)).strftime('%Y-%m-%d')
    tweetCriteria.since = rdA
    tweetCriteria.until = rdB
    tweetCriteria.maxTweets = 20

    TweetManager.getTweets(tweetCriteria, receiveBuffer)
    if len(tws) > 0:
		tt,td = tws[random.randint(0,len(tws)-1)]
		print "\n%s\n\n\t-%s, (c) O. Westin @MicroSFF\n" %(tt,td)
		#print "\t-" + td + ", (c) O. Westin @MicroSFF\n"
		count = -2
    else:
		count -=1

    if count == 0:
		print "Sorry bub, no quote this time."
