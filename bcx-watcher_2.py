#!/usr/bin/python3

import sys				# list args
import argparse			# parse args
import time				# allows sleep loops
import redis			# allows StrictRedis
import io				# allows file access
import datetime
from time import sleep
from datetime import datetime
from time import mktime
from configparser import ConfigParser
from threading import Thread

CONFIG_FILE = '/etc/bcx/bcx.conf'

## PROCESS COMMAND LINE ARGUMENTS
arguments = sys.argv
parser = argparse.ArgumentParser()
parser.add_argument('--start', action='store_true', default=False,
			dest='start_watcher',
			help='Starts the BCX Watcher process')
parser.add_argument('--stop', action='store_true', default=False,
			dest='stop_watcher',
			help='Stops the BCX Watcher process')
parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0', help='Program version')
results = parser.parse_args()
start_watcher = results.start_watcher
if (len(arguments) < 2):
	print ("ERROR: Recognized command(s) not provided; type 'bcx-watcher -h' for usage.\n")
	quit()


## LOAD GLOBALS FROM CONFIGURATION FILE
parser = ConfigParser()
parser.read(CONFIG_FILE)
REDIS_HOST = parser.get('redis', 'host')
REDIS_PORT = parser.get('redis', 'port')
REDIS_DB = parser.get('redis', 'history_db')
MAX_AGE_OF_DB = int(parser.get('watcher', 'max_age_of_database'))
R = redis.StrictRedis(REDIS_HOST, REDIS_PORT, REDIS_DB)


def get_score():
	## Generates a score value from current timestamp
	t = datetime.now()
	return int(mktime(t.timetuple()))

def score2stamp(score_in):
	## Converts score value into a timestamp
	return datetime.fromtimestamp(score_in).strftime('%Y-%m-%d %H:%M:%S')

def watcher():
	#arg = 5
	#for i in range(arg):
		#t = datetime.datetime.now()
		#print (t, 'Main Watcher thread')
		#sleep(1)
		print()

def history_mgr(secs):
	while (True):
		## Keep databases younger than last NN seconds ('sec')
		curr_score = get_score()
		max_age = curr_score - secs
		## Remove set members older than XXX seconds
		R.zremrangebyscore('PRICE_HISTORY', '-inf', max_age)
		R.zremrangebyscore('BID_HISTORY', '-inf', max_age)
		R.zremrangebyscore('ASK_HISTORY', '-inf', max_age)
		sleep(10)

def main():
    ##Main function
	quit()

if __name__ == '__main__':
	if (start_watcher == True):
		thread_watch = Thread(target = watcher)
		thread_history_mgr = Thread(target = history_mgr, args = (MAX_AGE_OF_DB, ))
		#thread_watch.start()
		thread_history_mgr.start()
		#main()
