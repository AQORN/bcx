BCX
===
BCX stands for "BitCoin eXchange". This name will obviously have to change if this is ever used publicly but for now it is what it is.

Design decisions and build steps:
-----------------------------------------------------
**Make python script executable:**
Touch file, create header, set perms and add soft link

    $ cat > /etc/bcx/whatever.py
      #!/usr/bin/python3
      print "Hello World!"
    
    $ chmod u+x /etc/bcx/whatever.py
    $ sudo ln -s /etc/bcx/whatever.py /usr/bin/whatever
    
Now the script will run with a simple command:

    $ whatever

**Implementing Python 3.5 alongside Python 2**
I want the to ability to install modules for Python3 scripts since I don't want to *replace* Python 2

    $ sudo apt-get install python3-pip

Future modules can now be installed specifically for Python3 as follows:

    $ sudo pip3 install <MODULE>

I'm using REDIS for the database back-end because of its in-memory DB capabilities that scale as well as support inter-module MQ messaging if/when desired. For the enterprise in-memory DB I could've also used SAP Hana but what's the fun in that. I'm sure Cassandra and MongoDB were options as well but I heard negatives around Mongo and only good things about Redis. Since I'm learning I went with the platform over which engineers seemed to be glowing.

**INSTALL REDIS (for in-memory NoSQL DB +  Messaging):**
*Borrowed from https://redis.io/topics/quickstart*

    $ sudo apt-get install tk8.5 tcl8.5
    $ wget http://download.redis.io/redis-stable.tar.gz
    $ tar xvzf redis-stable.tar.gz
    $ cd redis-stable
    $ make
    $ make test
    $ sudo make install

If desired (aka preferably) , set Redis RAM max to protect the system (particular if  VM) from crashing by editing redis.conf

    $ redis-server #runs server in foreground

MAKE REDIS RUN IN THE BACKGROUND:

    $ sudo mkdir /etc/redis
    $ sudo mkdir /var/redis
    $ sudo cp utils/redis_init_script /etc/init.d/redis_6379
    $ sudo cp redis.conf /etc/redis/6379.conf
    $ sudo mkdir /var/redis/6379
   
   Edit file to ensure vars are set correctly:

    $ sudo nano /etc/redis/6379.conf

>  Set daemonize to yes (by default it is set to no).
>  Set the pidfile to /var/run/redis_6379.pid (change port if req’d).

This example uses the default port which is already 6379

>  Set preferred loglevel. Set the logfile to /var/log/redis_6379.log
>  Set the dir to /var/redis/6379 (IMPORTANT!)

	$ sudo update-rc.d redis_6379 defaults
	$ sudo /etc/init.d/redis_6379 start

Modules required (will update as code is developed so required modules are known/expected):

    from websocket import WebSocketApp
    from json import dumps, loads
    from pprint import pprint

Install: kairos

Install: urlparse (urllib.parse)

    $ sudo pip3 install parse

Install pymongo

    $ sudo pip3 install pymongo

Install: sqlalchemy

    $ sudo pip3 install sqlalchemy

Install: cql

    $ sudo pip3 install cql

Install: exceptions

    $ sudo pip3 install requests --upgrade

**Thoughts around using Redis to provide time-series database (storing historical sorted sets for Price/Bid/Ask)**

**Overview:**
The goal is to use individual keys like huge record sets where table.row.id equates to key.score.value. My implementation sets keys as "price_history", "ask_history” and "bid_history”. Each key represents a sorted set which achieves a series of value coupling: score (int(UNIXTIME)) and value (some value that existed at that time).

**Warning:**
Redis does not necessarily store scores in the DB in any particular order so be sure to sort the values according to the unix time so they are output in a way that can represented in visualizations.

Each key (structured as a sorted set) can hold millions of values with unique scores (for us, score = unixtime as an integer) with six months of values equating to less than 350GB of space on disk.

**Example of Time Series Read/Write:**

FIRST TIME STAMP (write)

	score => TIMESTAMP1
	price => 1
	bid => 2
	ask => 3
	ZADD(‘price_history’, score, price)
	ZADD(‘bid_history’, score, bid)
	ZADD(‘ask_history’, score, ask])

SECOND TIME STAMP (write)

	score => TIMESTAMP2
	price => 4
	bid => 2
	ask => 6
	ZADD(‘price_history’, score, price)
	ZADD(‘bid_history’, score, bid)
	ZADD(‘ask_history’, score, ask)

RESULTS

	Price @ TIMESTAMP1 = 1
	Price @ TIMESTAMP2 = 4
	Bid @ TIMESTAMP1 = 2
	Ask @ TIMESTAMP2 = 6

PRICE across all timestamps:

	ZRANGE(‘price_history’, 0, -1, desc=False, withscores=True)
	TIMESTAMP1 = 1
	TIMESTAMP2 = 4
					. . .

This results in the recording of price, bid and ask values for a single time stamp and enables sorting of any value based on a single score.

I converted the time stamps to a unique integer (seconds) since Redis cannot sort objects like it can sort integers.

Process to store Time Series data for Price/Bid/Ask:
	Convert (timestamp) => unixtime (equivalent in seconds)
	use KEY as a unique SET storing multiple score:value entries
	Keys = VALUE HISTORY
	Score = unixtime value (converting time to seconds)

	Writing Time Series value(s)
	Syntax:	ZADD(KEY, VALUE, SCORE)
	Example:
		r.zadd(‘PRICE_HISTORY’, score, price_value)
		r.zadd(‘BID_HISTORY’, score, bid_value)
		r.zadd(‘ASK_HISTORY’, score, ask_value)
	
Instead of saving these values as keys, I saved them as sets of multiple values within unique keys where each value is associated with a single score. Millions of values can be set in each key and only reach ~300-400MB of space (aka RAM) per key which is more than we will need to maintain.

**Warning:**
As the number of time series databases increases (i.e. 1x BTC-USD-GDAX, 1x BTC-USD-GDAX, 1x BTC-USD-BITFINEX, etc) more RAM may be be required for processing depending on how this the platform will be used.

Retrieving all values for one Time Series entry

    Syntax:
    ZRANGE(KEY, start, end, desc=False, withscores=False)
    with scores = adds score value to each result (i.e. time stamp (in seconds))
    
    Example:
    all_results = ZRANGE(score, 0, -1, desc=False, withscores=True)

	All values in key set:	all_results
	One value in key set:	all_results[0]
	

**Component structure:**

    +--------+         +---------+         +-----+
    | SERVER |<--API-->| web_app |<--API-->| PHP |
    +--------+         +---------+         +-----+
      |    |                |
     SUB   RW               R
      |    |                |
    ------------------------------
    |            REDIS           |
    ------------------------------
         |   |              |
        PUB  R              W
         |   |              |   
    +------------+     +---------+         +------+
    |  WATCHER   |     | TRACKER |<--API-->| GDAX |
    |  monitor/  |     +---------+         +------+
    |  trigger   |
    +------------+

**What each BCX app currently does:**

 1. Run components in separate sessions or execute them all as services
 3. All components uses bcx.conf to get their global settings.

*BCX-TRACKER:*
Currently, bcx-tracker gets prices and saves the following within Redis:

 - BTC price as a unique set member within the “PRICE_HISTORY’ key
 - BID price as a unique set member within the “BID_HISTORY’ key
 - ASK price as a unique set member within the “ASK_HISTORY’ key
 - Prints the history of BTC prices it has built so far to the console so you know the script is working
	
*BCX-WATCHER:*
Currently, bcx-watcher has two primary processes: `history_mgr()` process and the `watcher()` process. `history_mgr()` deletes old values from Redis so the database history size can be maintained. This is good so processes can continue running that add data to a database without running the risk of overloading it. `watcher()` doesn’t do anything (yet) but is `will` read Redis on an ongoing basis and and trigger alerts to the server process for processing (buy/sell/etc). Both functions are run in the same script but within unique isolated Python threads so they can run independently of each other.

Redis is being used here because it will be much easier to read data/identify trends when keeping track of prices over time. Since I needed to store these values, a NoSQL database (key:value) storage platform seemed perfectly logical.

Using Flask to provide API interface so apps don't need to talk directly to Redis:

Integrate flask+redis:

    $ pip3 install flash-redis

Running a python3 app in the Flask dev webserver is okay for now, I'll need another method later:

	$ export FLASK_APP="/etc/bcx/bcx-web.py" flask run --host=0.0.0.0

Current API implementations:
http://localhost/bcx-tracker/api/v1.0/
http://localhost/bcx-watcher/v1.0/
http://localhost/bcx-server/api/v1.0/
http://localhost/bcx-web/api/v1.0/

Setting up a Python script to run as a service at boot (in Linux):
`$ sudo vi ‘whatever.sh’` (shell script that defines the new Linux process)

    #!/bin/sh
    
    ### BEGIN INIT INFO
    # Provides:          NAME_OF_SERVICE
    # Required-Start:    $remote_fs $syslog
    # Required-Stop:     $remote_fs $syslog
    # Default-Start:     2 3 4 5
    # Default-Stop:      0 1 6
    # Short-Description: Put a short description of the service here
    # Description:       Put a long description of the service here
    ### END INIT INFO

	# Change the next 3 lines to suit where you install your script and what you want to call it
	DIR=/DIR/WHERE/PYTHYON/SCRIPT/IS/LOCATED
	DAEMON=$DIR/name_of_python_script.py
	DAEMON_NAME=NAME_OF_SERVICE

	# Add any command line options for your daemon here
	DAEMON_OPTS=""

	# This next line determines what user the script runs as.
	# Root generally not recommended but necessary if you are using the Raspberry Pi GPIO from Python.
	DAEMON_USER=root

	# The process ID of the script when it runs is stored here:
	PIDFILE=/var/run/$DAEMON_NAME.pid

	. /lib/lsb/init-functions

	do_start () {
	    log_daemon_msg "Starting system $DAEMON_NAME daemon"
	    start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --chuid $DAEMON_USER --startas $DAEMON -- $DAEMON_OPTS
	    log_end_msg $?
	}
	do_stop () {
	    log_daemon_msg "Stopping system $DAEMON_NAME daemon"
	    start-stop-daemon --stop --pidfile $PIDFILE --retry 10
	    log_end_msg $?
	}

	case "$1" in

	    start|stop)
	        do_${1}
	        ;;

	    restart|reload|force-reload)
	        do_stop
	        do_start
	        ;;

	    status)
	        status_of_proc "$DAEMON_NAME" "$DAEMON" && exit 0 || exit $?
	        ;;

	    *)
	        echo "Usage: /etc/init.d/$DAEMON_NAME {start|stop|restart|status}"
	        exit 1
	        ;;

	esac
	exit 0

Save the file.

From command line:

    $ sudo chmod 755 whatever.sh
    $ sudo cp whatever.sh /etc/init.d
    $ sudo chmod 755 /etc/init.d/whatever.sh
    $ sudo chown root:root /etc/init.d/whatever.sh
    $ sudo apt-get install dos2unix #removes any windows characters if present
    $ sudo dos2unix /etc/init.d/whatever.sh
    $ sudo update-rc.d whatever.sh defaults

**WWW Implementation and Rational:**
Components currently being used and how:

    USER => PHP/APACHE (API client) => BCX-WEB/Python (API server)

*What:*
Eliminated  Python+Flask+<rendering_engine>+Jinja2+Apache +etc...

*Reason:*
Too many “frameworks” (aka potential break points) to manage making this not ideal as a platform to troubleshoot while coding front-end. Platform requirement/configuration feels unnecessarily complicated versus other WWW options. If I'm wrong please explain but for now I'm conflating to systems I know. If it's good enough for the Yahoo! and Facebook frameworks, it's good enough for me.

*Framework Selected:*

 - PHP/Apache as front-end
     Highcharts for visualization (supports multiple time series
   comparisons, free non-commercial)
    Reason: Easy to test and code, single mechanism to write code and
   display in browser

