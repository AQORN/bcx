#!/usr/bin/python3

from flask import Flask, jsonify
from datetime import datetime
import time
import redis
import json
from json import dumps, loads
import re

app = Flask(__name__)

@app.route('/bcx-web/api/v1.0/gdax/btc-usd/price/now')
def btc_usd_price_now():
	REDIS_HOST = 'localhost'
	REDIS_PORT = '6379'
	REDIS_DB = '0'
	R = redis.StrictRedis(REDIS_HOST, REDIS_PORT, REDIS_DB)
	result_range = R.zrange('PRICE_HISTORY', 0, -1, desc=False, withscores=True)
	latest_result = R.zrange('PRICE_HISTORY', -1, -1, desc=False, withscores=True)
	#d = dict(result_range)
	d = dict(latest_result)
	for k, i in d.items():
		#price
		k = re.sub('[\'b]', '', str(k))
		k = float(k)
		#score
		i = int(i)
		i = re.sub('[\']', '', str(i))
		return ("[{}000,{}]".format(i,("%0.2f" % k)))

@app.route('/bcx-web/api/v1.0/gdax/btc-usd/price/series')
def btc_usd_price_series():
	REDIS_HOST = 'localhost'
	REDIS_PORT = '6379'
	REDIS_DB = '0'
	R = redis.StrictRedis(REDIS_HOST, REDIS_PORT, REDIS_DB)
	result_range = R.zrange('PRICE_HISTORY', 0, -1, desc=False, withscores=True)
	latest_result = R.zrange('PRICE_HISTORY', -1, -1, desc=False, withscores=True)
	d = dict(result_range)
	fo = "[\n"               # placeholder for 'formatted output'
	fr = True                 #placeholder for 'first run'
	for pr, dt in sorted(d.items(), key=lambda x: x[1]):
		#price
		pr = re.sub('[\'b]', '', str(pr))
		pr = float(pr)
		#score %H:%M:%S
		Y = datetime.fromtimestamp(dt).strftime('%Y')
		M = datetime.fromtimestamp(dt).strftime('%m')
		D = datetime.fromtimestamp(dt).strftime('%d')
		h = datetime.fromtimestamp(dt).strftime('%H')
		m = datetime.fromtimestamp(dt).strftime('%M')
		s = datetime.fromtimestamp(dt).strftime('%S')
		#val1 = "Date.UTC({},{},{})".format(Y,M,D)
		val1 = "Date.UTC({},{},{},{},{},{})".format(Y,M,D,h,m,s)
		val2 = "{}".format(pr)
		if (fr == True):
			fo += "[{},{}],\n".format(val1,val2)
			ft = False
		else:
			fo += "[{},{}]".format(val1,val2)
	fo += "]"
	return(fo)

@app.route('/bcx-web/api/v1.0/gdax/btc-usd/price/series')
def bid():
	REDIS_HOST = 'localhost'
	REDIS_PORT = '6379'
	REDIS_DB = '0'
	R = redis.StrictRedis(REDIS_HOST, REDIS_PORT, REDIS_DB)
	result1 = R.zrange('PRICE_HISTORY', 0, -1, desc=False, withscores=True)
	result2 = R.zrange('BID_HISTORY', 0, -1, desc=False, withscores=True)
	result3 = R.zrange('ASK_HISTORY', 0, -1, desc=False, withscores=True)
	str1 = ' '.join(str(x) for x in result1)
	str2 = ' '.join(str(y) for y in result2)
	str3 = ' '.join(str(z) for z in result3)
	result = 'PRICE: {}<br />BID: {}<br />ASK {}'.format(str1, str2, str3)
	return json.dumps(result)

def main():
    ##Main function
	app.run(debug=True)
	btc_usd_price_series()

if __name__ == '__main__':
	#if (start_tracker == True):
	main()