import sys, os, re
import HTML
import tweepy
from tweepy import OAuthHandler
from optparse import OptionParser
from datetime import datetime
import codecs
import zipfile
import urllib2
import collections
import shutil
import time

def setup():
	"""
	Authenticates with Twitter with OAuth credentials and creates an instance of a Twitter API
	"""
	CONSUMER_KEY = '4S4kMhPkZ0NfRJ00sspA1sJfA'
	CONSUMER_SECRET = 'mqi3E7ELWlPCW6GzDRE8J75bJJdoFyNns1aCYK6K3bNILzLEid'
	ACCESS_KEY = '2808956111-uumNUJgW4or9oqXOZzEAwQOgEYbShImKXjZaVkv'
	ACCESS_SECRET = 'AzHHqljl4IvN20XydnIZnGpUNprjFVYIffXG3kUOfdOaR'

	print "[+] Authenticating..."
	try:
		auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
		api = tweepy.API(auth)
		
		print "[+] Successfully authenticated!"
		return tweepy.API(auth)
		
	except Exception, e:
		print "[-] Error authenticating to Twitter:"
		print e
		exit(0)

def printHelp():
	"""
	Prints help menu
	"""	
	print "-" * 24
	print "%-12s %s" % ("Command", "Description")
	print "-" * 24
	print "%-12s %s" % ("archive", "Downloads HTML archive of loaded timeline")
	print "%-12s %s" % ("clear","Clears the terminal")
	print "%-12s %s" % ("date", "Find tweets in certain date ranges")
	print "%-12s %s" % ("exit", "Exits the program")
	print "%-12s %s" % ("followers", "Downloads follower info into HTML archive")
	print "%-12s %s" % ("help", "Prints this help list")
	print "%-12s %s" % ("images", "Download all pictures from user's timeline")
	print "%-12s %s" % ("live", "Interactive live search for specific queries")
	print "%-12s %s" % ("match", "Compare timeline against a given wordlist")
	print "%-12s %s" % ("mentions", "Find most frequently contacted users")
	print "%-12s %s" % ("new", "Change target account")			
	print "%-12s %s" % ("user", "Prints basic user info")
		
def getTimeline(api, username, count=20, verbose=True):
	"""
	Retrieves timeline of specified user
	
	Arguments:
		api			Instance of Twitter API
		username	Username of target
		count		# of tweets to retrieve, default 20
	Returns:
		timeline	list of STATUS objects
	"""
	if verbose:print "[+] Retrieving timeline of @%s..."%username
	try:
		timeline = api.user_timeline(screen_name=username, count=count)
		if verbose:	print "[+] %s tweet(s) found"%len(timeline)
		return timeline
		
	except Exception, e:
		print "[-] Error retrieving timeline of "+username
		print e
		
def printTimeline():
	"""
	Prints all statuses from loaded timeline
	"""
	try:
		for status in timeline:
			printTweet(status)
		return
		
	except Exception, e:
		print "[-] Error printing timeline"
		errorLog(e, "printTimeline")
		return

def printTweet(tweet):
	"""
	Prints info on statuses from user's timeline
	
	Arguments:
		tweet	user status object
	"""
	try:
		print "----"
		print "%-14s %s" % ("[+] Time:", tweet.created_at)
		print "%-14s %s" % ("[+] Text:", tweet.text)
		print "%-14s %s" % ("[+] Location:", geoInfo(tweet))
		print "%-14s %s" % ("[+] Platform:", tweet.source)
		print "%-14s %s" % ("[+] Retweets:", str(tweet.retweet_count))
		print "%-14s %s" % ("[+] Favorites:", str(tweet.favorite_count))
		print "%-14s %s" % ("[+] Link:", "http://twitter.com/"+tweet.user.screen_name+"/status/"+str(tweet.id))
		return
		
	except Exception, e:
		print "[-] Error printing tweet"
		errorLog(e, "printTweet")
		return		

def userInfo():
	"""
	Prints info on target account
	"""
	try:
		print "%-18s %s" % ("[+] Name:",user.name)
		print "%-18s %s" % (("[+] Handle:", user.screen_name.encode('utf-8')))
		print "%-18s %s" % ("[+] Created at: ", user.created_at)
		print "%-18s %s" % ("[+] About: ", xstr(user.description))
		print "%-18s %s" % ("[+] Location: ", xstr(user.location))
		print "%-18s %s" % ("[+] Website: ", xstr(user.url))
		print "%-18s %s" % ("[+] Tweets: ", str(user.statuses_count))
		print "%-18s %s" % ("[+] Followers: ", str(user.followers_count))
		print "%-18s %s" % ("[+] Following: ", str(user.friends_count))
		
		print "%-18s %s" % ("[+] Profile Link:", "http://twitter.com/"+user.screen_name)
	
	except Exception, e:
		print "[-] Error getting account info"
		errorLog(e, "userInfo")
		return

def changeUser():
	"""
	Changes target account
	"""
	try:
		global timeline
		username = ""
		username = raw_input("Enter new username: @")
		count = raw_input("Enter count: ")
		timeline = getTimeline(api, username, count)
		user = api.get_user(options.username)
	
	except Exception, e:
		print "[-] Unable to change user account, target is still"+user.name
		errorLog(e, "changeUser")
		timeline = getTimeline(api, username, count, verbose=False)
		return
		
def dateSearch():
	try:
		start_entry = raw_input('Enter start date (YYYY-MM-DD): ')
		end_entry = raw_input('Enter end data (YYYY-MM-DD): ')

		syear, smonth, sday = start_entry.split('-')
		eyear, emonth, eday = end_entry.split('-')
		start_date = syear + smonth + sday
		end_date = eyear + emonth + eday

		for status in timeline:
			date = str(status.created_at)
			current_date, time = date.split(' ');
			year, month, day = current_date.split('-', 3)
			check_date = year + month + day

			if check_date > start_date and check_date < end_date:
				printTweet(status)
				return
				
	except Exception, e:
		print "[-] Error performing chronological search"
		errorLog(e, "dateSearch")
		return
	
def listSearch():
	"""
	Will check the currently gathered timeline and match it against the given wordlist
	"""
	try:
		wordlist = raw_input('Enter filename: ')
		print "[+] Searching timeline for contents of %s..." %wordlist
		
		results = HTML.Table(header_row=['Matched Word', 'Time', 'Text', 'Location', 'Platform', 'Web Link'])
		
		for tweet in timeline:
			wfile = open(wordlist, 'r')

			for word in wfile:
				word = word.strip()
				if word.lower() in tweet.text.lower():
					webUrl = HTML.link('View on web', "http://twitter.com/"+tweet.user.screen_name+"/status/"+str(tweet.id))
					match = [word.lower(), tweet.created_at, tweet.text.encode('utf-8'), geoInfo(tweet), tweet.source, webUrl]
					results.rows.append(match)
		wfile.close()
		
		name = str(user.screen_name)+"_search_"+wordlist+"_"+datetime.now().strftime('%Y-%m-%d_%H%M%S')+".html"
		localFile = open(name, 'w')
		localFile.writelines(str(results))
		localFile.close()
		
		print "[+] Results written to "+name
					
	except Exception, e:
		print "[-] Error searching timeline"
		errorLog(e, "listSearch")
		return
	
def liveSearch():
	"""
	Will check the currently gathered timeline and match it against a specified text query
	"""
	try:
		query = ""
		while True:
			query = raw_input("Enter search query ('q 'to quit): ")
			if query == "q":
				return
			for status in timeline:
				if query.lower() in status.text.lower():
					printTweet(status)
		return
		
	except Exception, e:
		print "[-] Error with search query"
		errorLog(e, "liveSearch")
		return

def getImages():
	"""
	Downloads all images from loaded timeline into folder in current directory
	"""
	print "[+] Downloading images from @%s's timeline..." % user.screen_name
	try:
		i = 0
		directory = user.screen_name+"_images_"+datetime.now().strftime('%Y-%m-%d_%H%M%S')
		os.makedirs(directory)
		for tweet in timeline:
			for media in tweet.entities.get("media",[{}]):
				if media.get("type",None) == "photo":
					file = "photo_%d"%i#tweet.created_at.replace(":","")
					ext = '.jpg'
					name = file + ext
					i += 1
					img = urllib2.urlopen(media['media_url'])
					localFile = open(name, 'wb')
					localFile.write(img.read())
					localFile.close()
					shutil.move(name,directory)
		print "[+] Downloaded %d image(s)"%i
		return
		
	except Exception, e:
		print "[-] Error downloading pictures"
		errorLog(e, "getImages")
		return
		
def getFollowers():
	"""
	Retrieves list of followers and writes to HTML file
	"""
	print "[+] Attempting to create list of followers..."
	print "[*] Warning: May take up to 15 minutes per 180 followers"
	
	try:
		ids = []
		for page in tweepy.Cursor(api.followers_ids, screen_name=user.screen_name).pages():
			ids.extend(page)
			time.sleep(60)
		
		table = HTML.Table(header_row=["Name", 'Handle', 'Web Link'])
		file = user.screen_name+"_followers_"+datetime.now().strftime('%Y-%m-%d_%H%M')+".html"
		
		i = 0	
		for user_id in ids:
			if i % 180 == 0:
				time.sleep(900)
			i += 1
			follower = api.get_user(user_id)
			webUrl = HTML.link('View Profile', "http://twitter.com/"+follower.screen_name)
			
			newRow = [follower.name.encode('utf-8'), "@"+follower.screen_name, webUrl]
			table.rows.append(newRow)
			
		print "[+] Found %d follower(s)" % len(ids)
		
		name = user.screen_name+"_followers_"+datetime.now().strftime('%Y-%m-%d_%H%M%S')+".html"
		localFile = open(name, 'w')
		localFile.writelines(str(table))
		localFile.close()

		print "[+] Results written to "+file
		return
		
	except Exception, e:
		print "[-] Error retrieving followers"
		errorLog(e, "getFollowers")
		return

def archive():
	"""
	Downloads HTML archive of currently loaded timeline
	"""
	print "[+] Creating HTML archive of timeline..."
	
	try:
		table = HTML.Table(header_row=['Time', 'Text', 'Location', 'Platform', 'Web Link'])
		
		for tweet in timeline:
			geo =geoInfo(tweet)
			if geo != "N/A":
				geo = HTML.link(geo, geoInfo(tweet, URL=True))
			webUrl = HTML.link('View on web', "http://twitter.com/"+tweet.user.screen_name+"/status/"+str(tweet.id))
			
			newRow = [tweet.created_at, tweet.text.encode('utf-8'), geo, tweet.source,webUrl]
			table.rows.append(newRow)
		
		name = user.screen_name+"_archive_"+datetime.now().strftime('%Y-%m-%d_%H%M%S')+".html"
		localFile = open(name, 'w')
		localFile.writelines(str(table))
		localFile.close()
		
		print "[+] Results written to "+name
		return
		
	except Exception, e:
		print "[-] Error creating HTML archive from timeline"
		errorLog(e, "archive")
		return							
		
def mentions():
	"""
	Prints most common words used in tweets
	"""
	mentions = []
	print "[+] Gathering info on mentions..."
	
	try:
		for tweet in timeline:
			split = tweet.text.lower().split()
			for word in split:
				if word[0]=="@":
					mentions.append(word)
		counter = collections.Counter(mentions)
		mentions = counter.most_common()
		
		print "\nUser                   Qty"
		print "=========================="
		try:
			for i in range(0,10):
				print '%-20s %05s' % (str(mentions[i][0]), str(mentions[i][1]))
		except:
			print "[+] End of mentions"
		return
	
	except Exception, e:
		print "[-] Error getting mentions"
		errorLog(e, "mentions")
		return
		
def geoInfo(tweet, URL=False):
	"""
	Returns short description geo info from tweet
	
	Arguments:
		tweet		Tweet object
		URL			bool, whether or not user wants GMaps URL returned
	"""
	try:
		if tweet.place:
			if URL:
				append = tweet.place.full_name.replace (" ", "+")
				url = "http://www.google.com/maps/place/"+append
				return url
			else:
				return tweet.place.full_name
		else:
			return "N/A"
	
	except Exception, e:
		print "[-] Error getting geolocation info"
		errorLog(e, "printTimeline")
		return
	
def xstr(s):
	"""
	Converts potentially nullable strings that are indeed null to "N/A". Also parses emojis.
	"""
	if s is None:
		return 'N/A'
	"""	
	emoji_pattern = r'/[U0001F601-U0001F64F]/u'
	re.sub(emoji_pattern, '#', s)
	"""
	try:
		# UCS-4
		highpoints = re.compile(u'[U00010000-U0010ffff]')
	except re.error:
		# UCS-2
		highpoints = re.compile(u'[uD800-uDBFF][uDC00-uDFFF]')
	return s.encode('utf-8')	
	
def clear():
	"""
	Clears terminal
	"""
	os.system('cls' if os.name == 'nt' else 'clear')
	
def errorLog(error, module):
	"""
	Writes errors to HTML log file
	
	Arguments:
		error		Error recieved from module
		module		Function where error was encountered
	"""
	try:
		log = HTML.Table(header_row=['Function', 'Time', 'Info'])
		
		entry = [module, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(error)]
		log.rows.append(entry)
		
		logFile = open("talon_error_log.html", 'a')
		logFile.writelines("<br>")
		logFile.writelines(str(log))
		logFile.close()
		
	except Exception, e:
		print "ERROR\n"+str(e)
		return
		
def main():

	parser = OptionParser(usage="usage: %prog -u <username>", version="%prog 1.0")
	parser.add_option("-u", "--username", dest="username", help="Twitter username of target account")
	parser.add_option("-c", "--count", dest="count", help="Number of tweets to retrieve (default of 20)")
	(options, args) = parser.parse_args()
	
	if not options.username:
		parser.print_help()
		exit(0)
	
	methodIndex =  {'archive':archive,
					'clear':clear,
					'date':dateSearch,
					'exit':exit,
					'followers':getFollowers,
					'help':printHelp,
					'images':getImages,
					'list':listSearch,
					'live':liveSearch,
					'mentions':mentions,
					'new':changeUser,
					'print':printTimeline,
					'user':userInfo
					}
	
	global api, timeline, user	
	api = setup()
	user = api.get_user(options.username)
	timeline = getTimeline(api, options.username, options.count)
	
	while True:
		command = raw_input(">>> ")
		
		if command in methodIndex.keys():		
			methodIndex[command]()
		else:
			print "Invalid command"
	
if __name__ == "__main__":
	main()

	
