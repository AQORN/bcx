#!/usr/bin/python3

PATH_TO_CONFIG = '/etc/bcx/bcx.conf'

import sys				# list args
import argparse			# parse args
import requests 		# req'd for API usage
import gdax				# talk to GDAX API
import time				# allows sleep loops
import datetime
import io				# allows file access
from configparser import ConfigParser


## PROCESS COMMAND LINE ARGUMENTS
arguments = sys.argv
parser = argparse.ArgumentParser()
parser.add_argument('--start', action='store_true', default=False,
			dest='start_tracker',
			help='Starts the BCX Tracker process')
parser.add_argument('--stop', action='store_true', default=False,
			dest='stop_server',
			help='Stops the BCX Tracker process')
parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0', help='Program version')
results = parser.parse_args()
start_server = results.start_tracker
if (len(arguments) < 2):
	print ("ERROR: Recognized command(s) not provided; type 'bcx-tracker -h' for usage.\n")
	quit()

## LOAD GLOBALS FROM CONFIGURATION FILE
parser = ConfigParser()
parser.read(PATH_TO_CONFIG)
BUY_TARGET =  parser.get('server', 'buy_target')
SELL_TARGET =  parser.get('server', 'sell_target')
CASH =  parser.get('server', 'cash')

## Define internal globals (temporary)
ACTION = "" 			# Placeholder (used to populate Hold/Buy/Sell)
prev_bal = float(0)		# Account balance before tranaction starts
new_bal = float(0)		# Account balance after tranaction completes 
prev_price = float(0)	# Price at last transaction (used to calc price diff)
pivot_price = float(0)	# Set whenever a buy or sell is executed to determine price differential
price = 0				# Current price
diff = 0				# Difference between the last price and current price
firstrun = True			# To help script know this is the first run (before it learns context)
check_interval = 0.5	# Number of seconds until next price check


def main():
    ##Main function
	quit()


if __name__ == '__main__':
	if (start_server == True):
		main()