import sys, os, re
#import HTML
import tweepy
from tweepy import OAuthHandler
from optparse import OptionParser
import re

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

def getTimeline(api, username, count=20):
	"""
	Retrieves timeline of specified user
	
	Arguments:
		api			Instance of Twitter API
		username	Username of target
		count		# of tweets to retrieve, default 20
	Returns:
		timeline	list of STATUS objects
	"""
	print "[+] Retrieving timeline of @%s..."%username
	try:
		timeline = api.user_timeline(screen_name=username, count=count)
		print "[+] %s tweet(s) found"%len(timeline)
		return timeline
		
	except Exception, e:
		print "[-] Error retrieving timeline:"
		print e
		exit(0)

def printTweet(tweet):
	"""
	Prints info on statuses from user's timeline
	
	Arguments:
		tweet	user status object
	"""
	try:
		print "----"
		print "[+] Time:      "+str(tweet.created_at)
		print "[+] Text:      "+tweet.text
		#print "[+] Location:  "+xstr(tweet.place.name)
		print "[+] Sent from: "+xstr(tweet.source)
		print "[+] URL:       http://twitter.com/"+tweet.user.screen_name+"/status/"+str(tweet.id)
		return
	except:
		print "[-] Error printing tweet"
		return
	
def printHelp():
	"""
	Prints help menu
	"""	
	print "Command         Description"
	print "-" * 27
	print "exit............Exit"
	print "help............Print help"
	print "html............Download timeline to html file"		#toBeImplemented
	print "live............Interactive search for specified query"
	print "match...........Compare timeline against wordlist"	#toBeImplemented
	print "new.............Change target account"				#toBeImplemented?
	print "search..........Search user's tweets interactively"	#toBeImplemented
	print "user............Prints basic user info"
	print "advanced........Prints advanced user info"			#toBeImplemented
	print "zip.............Download and zip timeline"			#toBeImplemented

def userInfo():
	"""
	Prints info on target account
	"""
	try:
		print "[+] Name: "+str(timeline[0].user.name)
		print "[+] Handle: "+str(timeline[0].user.screen_name)
		print "[+] About: "+xstr(timeline[0].user.description)
		print "[+] Location: "+xstr(timeline[0].user.location)
		print "[+] Profile Link: http://twitter.com/"+timeline[0].user.screen_name
	except:
		print "[-] Error getting account info"

def changeUser():
	"""
	Changes target account
	"""
	try:
		user = ""
		user = raw_input("Enter new username: @")
		count = raw_input("Enter count: ")
		timeline = getTimeline(api, user, count)
	except Exception, e:
		print "[-] Unable to change user account"
		print e
	
def listSearch(wordlist):
	"""
	Will check the currently gathered timeline and match it against the given wordlist
	"""
	
	for status in timeline:
		wfile = open(wordlist, 'r')

		for word in wfile:
			word = word.strip()
			if word.lower() in status.text.lower():
				print status.text.lower()
				#printTweet(status)

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
		print e
		return

def xstr(s):
	"""
	Converts null string to 'N/A'
	"""
	if s is None:
		return 'N/A'
	return str(s)

def zip():
	i = 1
	zf = zipfile.ZipFile('important.zip', mode='w')
	for tweet in timeline:
		for media in tweet.entities.get("media",[{}]):
			if media.get("type",None) == "photo":
				s = 'image'
				file = '%s%d' %(s, i)
				ext = '.jpg'
				name = file + ext 
				i += 1
				img = urllib2.urlopen(media['media_url'])
				localFile = open(name, 'wb')
				localFile.write(img.read())
				localFile.close()
				zf.write(name)
				os.remove(name)
	zf.close()

def main():

	parser = OptionParser(usage="usage: %prog -u <username>", version="%prog 1.0")
	parser.add_option("-u", "--username", dest="username", help="Twitter username of target account")
	parser.add_option("-c", "--count", dest="count", help="Number of tweets to retrieve (default of 20)")
	#parser.add_option("-w", "--wordlist", dest="wordlist", help="Wordlist used to check against")
	(options, args) = parser.parse_args()
	
	if not options.username:
		parser.print_help()
		exit(0)
	
	methodIndex =  {'exit':exit,
			'help':printHelp,
			'match':listSearch,
			'user':userInfo,
			'change':changeUser,
			'live':liveSearch,
			'zip':zip
		       }
	
	global api, timeline	
	api = setup()
	timeline = getTimeline(api, options.username, options.count)

	#if options.wordlist:
	#	getWordList(options.wordlist)
	
	while True:
		command = raw_input(">>> ")
		
		if command in methodIndex.keys():		
			methodIndex[command]()
		else:
			print "Invalid command"
	
if __name__ == "__main__":
	main()
