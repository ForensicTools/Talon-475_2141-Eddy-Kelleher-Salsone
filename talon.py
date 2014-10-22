import sys, os, re
#import HTML
import tweepy
from tweepy import OAuthHandler
from optparse import OptionParser

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

def printTweets():
	"""
	Prints info on statuses from user's timeline
	
	Arguments:
		timeline	user timeline object
	"""

	for status in timeline:
		print "----"
		print "[+] Time:      "+str(status.created_at)
		print "[+] Text:      "+status.text
		#print "[+] Location:  "+xstr(status.place.name)
		print "[+] Sent from: "+xstr(status.source)
		print "[+] URL:       http://twitter.com/"+status.user.screen_name+"/status/"+str(status.id)
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
	print "match...........Compare timeline against wordlist"	#toBeImplemented
	print "new.............Change target account"				#toBeImplemented?
	print "print...........Print user's tweets"
	print "search..........Search user's tweets interactively"	#toBeImplemented
	print "zip.............Download and zip timeline"			#toBeImplemented

def xstr(s):
	"""
	Converts null string to 'N/A'
	"""
	if s is None:
		return 'N/A'
	return str(s)
	
def main():

	parser = OptionParser(usage="usage: %prog -u <username>", version="%prog 1.0")
	parser.add_option("-u", "--username", dest="username", help="Twitter username of target account")
	parser.add_option("-c", "--count", dest="count", help="Number of tweets to retrieve (default of 20)")
	(options, args) = parser.parse_args()
	
	if not options.username:
		parser.print_help()
		exit(0)
	
	methodIndex =  {'exit':exit,
			'help':printHelp,
			'print':printTweets
		       }
	
	global api, timeline	
	api = setup()
	timeline = getTimeline(api, options.username, options.count)
	
	while True:
		command = raw_input(">>> ")
		
		if command in methodIndex.keys():		
			methodIndex[command]()
		else:
			print "Invalid command"
	
if __name__ == "__main__":
	main()
