#!/usr/bin/python3

import sys
import argparse
from configparser import ConfigParser
import subprocess
from subprocess import Popen, PIPE
import time
from termcolor import colored


## PROCESS COMMAND LINE ARGUMENTS
arguments = sys.argv
parser = argparse.ArgumentParser()
parser.add_argument('--start-all', action='store_true', default=False,
			dest='start_all',
			help='Starts all BCX processes')
parser.add_argument('--stop-all', action='store_true', default=False,
			dest='stop_all',
			help='Stops all BCX processes')	
parser.add_argument('--start-server', action='store_true', default=False,
			dest='start_server',
			help='Starts the BCX Server process')
parser.add_argument('--stop-server', action='store_true', default=False,
			dest='stop_server',
			help='Stops the BCX Server process')
parser.add_argument('--start-tracker', action='store_true', default=False,
			dest='start_tracker',
			help='Starts the BCX Tracker process')
parser.add_argument('--stop-tracker', action='store_true', default=False,
			dest='stop_tracker',
			help='Stops the BCX Tracker process')
parser.add_argument('--start-watcher', action='store_true', default=False,
			dest='start_watcher',
			help='Starts the BCX Watcher process')
parser.add_argument('--stop-watcher', action='store_true', default=False,
			dest='stop_watcher',
			help='Stops the BCX Watcher process')
parser.add_argument('--start-web', action='store_true', default=False,
			dest='start_web',
			help='Starts the BCX Web process')
parser.add_argument('--stop-web', action='store_true', default=False,
			dest='stop_web',
			help='Stops the BCX Web process')
parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0', help='Program version')
results = parser.parse_args()

if (len(arguments) < 2):
	print ("ERROR: Recognized command(s) not provided; type 'bcx -h' for usage.\n")
	quit()

def service_mgr(SERVICE,ACTION):
	if (SERVICE == 'bcx-web') or (SERVICE == 'all'):
		p = Popen(['sudo', '/etc/init.d/bcx-web.sh', ACTION], stdin=PIPE, stdout=PIPE, stderr=PIPE)
		# Note: using sequence uses shell=0
		stdout, stderr = p.communicate()
		#print ("Stdout:", stdout)
		if (stderr != b''): print ("BCX-SERVER ERROR:", stderr)
		service_status = subprocess.check_output(['ps', '-A'])
		if (stderr == b'') and (ACTION == 'stop'): print (colored("BCX-WEB was stopped", 'red'))
		if (stderr == b'') and (ACTION == 'start'): print (colored("BCX-WEB is now running", 'green'))
	if (SERVICE == 'bcx-server') or (SERVICE == 'all'):
		p = Popen(['sudo', '/etc/init.d/bcx-server.sh', ACTION], stdin=PIPE, stdout=PIPE, stderr=PIPE)
		# Note: using sequence uses shell=0
		#stdout, stderr = p.communicate()
		#print ("Stdout:", stdout)
		if (stderr != b''): print ("BCX-SERVER ERROR:", stderr)
		if (stderr == b'') and (ACTION == 'stop'): print (colored("BCX-SERVER was stopped", 'red'))
		if (stderr == b'') and (ACTION == 'start'): print (colored("BCX-SERVER is now running", 'green'))
	if (SERVICE == 'bcx-watcher') or (SERVICE == 'all'):
		p = Popen(['sudo', '/etc/init.d/bcx-watcher.sh', ACTION], stdin=PIPE, stdout=PIPE, stderr=PIPE)
		# Note: using sequence uses shell=0
		stdout, stderr = p.communicate()
		#print ("Stdout:", stdout)
		if (stderr != b''): print ("BCX-WATCHER ERROR:", stderr)
		if (stderr == b'') and (ACTION == 'stop'): print (colored("BCX-WATCHER was stopped", 'red'))
		if (stderr == b'') and (ACTION == 'start'): print (colored("BCX-WATCHER is now running", 'green'))
	if (SERVICE == 'bcx-tracker') or (SERVICE == 'all'):
		p = Popen(['sudo', '/etc/init.d/bcx-tracker.sh', ACTION], stdin=PIPE, stdout=PIPE, stderr=PIPE)
		# Note: using sequence uses shell=0
		stdout, stderr = p.communicate()
		#print ("Stdout:", stdout)
		if (stderr != b''): print ("BCX-TRACKER ERROR:", stderr)
		service_status = subprocess.check_output(['ps', '-A'])
		if (stderr == b'') and (ACTION == 'stop'): print (colored("BCX-TRACKER was stopped", 'red'))
		if (stderr == b'') and (ACTION == 'start'): print (colored("BCX-TRACKER is now running", 'green'))

def main():
	if (results.start_tracker == True):
		service_mgr('bcx-tracker', 'start')
	if (results.stop_tracker == True):
		service_mgr('bcx-tracker', 'stop')
	if (results.start_watcher == True):
		service_mgr('bcx-watcher', 'start')
	if (results.stop_watcher == True):
		service_mgr('bcx-watcher', 'stop')
	if (results.start_server == True):
		service_mgr('bcx-server', 'start')
	if (results.stop_server == True):
		service_mgr('bcx-server', 'stop')
	if (results.start_web == True):
		service_mgr('bcx-web', 'start')
	if (results.stop_web == True):
		service_mgr('bcx-web', 'stop')
	if (results.start_all == True):
		service_mgr('all', 'start')
	if (results.stop_all == True):
		service_mgr('all', 'stop')
		
if __name__ == '__main__':
	main()