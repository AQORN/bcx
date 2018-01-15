#!/usr/bin/python3

import redis
from datetime import datetime
from time import sleep
from websocket import WebSocketApp
from json import dumps, loads
from configparser import ConfigParser
import calendar

CONFIG_FILE = '/etc/bcx/bcx.conf'
	
## LOAD GLOBALS FROM CONFIGURATION FILE
parser = ConfigParser()
parser.read(CONFIG_FILE)
REDIS_HOST = parser.get('redis', 'host')
REDIS_PORT = parser.get('redis', 'port')
REDIS_DB = parser.get('redis', 'history_db')

R = redis.StrictRedis(REDIS_HOST, REDIS_PORT, REDIS_DB)

def on_message(_, message):
	p = None
	a = None 
	b = None
	d = dict(loads(message))
	conn = redis.StrictRedis(host="localhost", port=6379, db=0)
	
	for k, i in d.items():
		if k == "price":
			p = float(i)
		if k == "best_ask":
			a = float(i)
		if k == "best_bid":
			b = float(i)
	
	write2db(p, b, a)
	show_db()

def get_score():
	## Generates a score value from current timestamp
	t = datetime.now()
	return calendar.timegm(t.utctimetuple())

def score2stamp(score_in):
	## Converts score value into a timestamp
	return datetime.fromtimestamp(score_in).strftime('%Y-%m-%d %H:%M:%S')

def write2db(price, bid, ask):
	sc = str(get_score())
	if (price != None):
		R.zadd('PRICE_HISTORY', sc, price)
	if (bid != None):
		R.zadd('BID_HISTORY', sc, bid)
	if (ask != None):
		R.zadd('ASK_HISTORY', sc, ask)

def show_db():
	result1 = R.zrange('PRICE_HISTORY', 0, -1, desc=False, withscores=True)
	result2 = R.zrange('BID_HISTORY', 0, -1, desc=False, withscores=True)
	result3 = R.zrange('ASK_HISTORY', 0, -1, desc=False, withscores=True)
	
def on_error(ws, error):
	print(error)


def on_open(socket):
	##Callback executed at socket opening.
	##Keyword argument:
	##socket -- The websocket itself

	params = {
		"type": "subscribe",
		"channels": [{"name": "ticker", "product_ids": ["BTC-USD"]}]
	}
	socket.send(dumps(params))


def on_close(socket):
    print("\n## Socket Closed ##")


def main():
    ##Main function

	while (True):
		try:

			URL = 'wss://ws-feed.gdax.com'
			ws = WebSocketApp(URL, on_open=on_open,
				on_close=on_close,
				on_error=on_error,
				on_message=on_message)
			ws.run_forever()
		except WebSocketConnectionClosedException as e:
			print ( "WebSocketConnectionClosedException:Failed to recreate connection to host, please ensure network connection to host: {}".format(URL))
			print(e)
			print (os.sys.exc_info()[0:2])
		except WebSocketTimeoutException as e:
			print ( "WebSocketTimeoutException: Failed to recreate connection to hos, please ensure network connection to host: {}".format(URL))
			print(e)
			print (os.sys.exc_info()[0:2])
		except Exception as e:
			print ( "Exception: Failed to (re-)create connection to host, please ensure network connection to host: {}".format(URL))
			print(e)
			print (os.sys.exc_info()[0:2])


if __name__ == '__main__':
	main()