#!/usr/bin/python
#
# Originally derived from Hazado's BFGMobileAdapter script
#
# CGMinerMobileAdapter
#
# Copyright 2014 Axadiw
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.  See COPYING for more details.

import os
import time
import datetime
import argparse
import json
import logging
import httplib
import pprint
import socket
import urllib
import urllib2

def start_mining():
	print "STARTUJE"

def stop_mining():
	print "STOPUJE"

def restart_mining():
	print "RESTARTUJE"

actions = {
	"STOP" : stop_mining,
	"START" : start_mining,
	"RESTART" : restart_mining
}

print '[ -=-=-=-=- Starting CGMinerMobileAdapter - CGMiner to MobileMiner Interface -=-=-=-=- ]'
while 1:
	logging.basicConfig(
			 format='%(asctime)s %(levelname)s %(message)s',
			 level=logging.DEBUG
	)
	
# Edit these values for individual Miner Instance
# --- Begin Miner Configuration ---
	emailAddy = 'yourEmail@email.com'
	applicationKey = 'ApplicationKey'
	machineName = 'Miner Machine Name'
# --- End Miner Configuration  ---

	apiKey = 'yIiEyL50VuMVdp'	
	reqURL = 'https://mobileminer.azurewebsites.net/api/MiningStatisticsInput?emailAddress='+emailAddy+'&applicationKey='+applicationKey+'&machineName='+machineName+'&apiKey='+apiKey

	parser = argparse.ArgumentParser()
	parser.add_argument("command", default="devs", nargs='?')
	parser.add_argument("parameter", default="", nargs='?')
	parser.add_argument("--hostname", default="localhost")
	parser.add_argument("--port", type=int, default=4028)
	args = parser.parse_args()

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(30)

	try:
		s.connect((args.hostname, args.port))
	except socket.error, e:
		logging.error(e)

	try:
		s.send("{\"command\" : \"%s\", \"parameter\" : \"%s\"}"
				% (args.command, args.parameter)
			  )
	except socket.error, e:
		logging.error(e)

	data = []
	data2 = []
	print '['+str(datetime.datetime.now()).split('.')[0]+']  Getting Data from CGMiner RPC API using port:'+str(args.port)
	try:
		data = s.recv(32768)
	except socket.error, e:
		logging.error(e)

	try:
		s.close()
	except socket.error,e:
		logging.error(e)

	if data:
		data = json.loads(data.replace('\x00', ''))

	try:
		for item in data['DEVS']:
			device = dict()
			device[u'MinerName'] = u'CGMiner'
			device[u'CoinSymbol'] = u'LTC'
			device[u'CoinName'] = u'Litecoin'
			device[u'Algorithm'] = u'Scrypt'
			if not item.get('Name'):
					device[u'Kind'] = u'GPU'
					device[u'FanSpeed'] = item[u'Fan Speed']
					device[u'FanPercent'] = item[u'Fan Percent']
					device[u'GpuClock'] = item[u'GPU Clock']
					device[u'MemoryClock'] = item[u'Memory Clock']
					device[u'GpuVoltage'] = item[u'GPU Voltage']
					device[u'GpuActivity'] = item[u'GPU Activity']
					device[u'PowerTune'] = item[u'Powertune']
					device[u'Intensity'] = item[u'Intensity']
			elif item[u'Name'] == u'OCL':
					device[u'Kind'] =  item[u'Name']
					device[u'FanSpeed'] = item[u'Fan Speed']
					device[u'FanPercent'] = item[u'Fan Percent']
					device[u'GpuClock'] = item[u'GPU Clock']
					device[u'MemoryClock'] = item[u'Memory Clock']
					device[u'GpuVoltage'] = item[u'GPU Voltage']
					device[u'GpuActivity'] = item[u'GPU Activity']
					device[u'PowerTune'] = item[u'Powertune']
					device[u'Intensity'] = item[u'Intensity']
			else:
					device[u'Kind'] = item[u'Name']
			if not item.get('Name'):
					device[u'Index'] = item[u'GPU']
			else:
					device[u'Index'] = item[u'ID']
			if item[u'Enabled'] == u'Y':
				device[u'Enabled'] = True
			else:
				device[u'Enabled'] = False
			if u'Temperature' in item:
				device[u'Temperature'] = item[u'Temperature']
			device[u'Status'] = item[u'Status']
			device[u'AverageHashrate'] = item[u'MHS av'] * 1000
			device[u'CurrentHashrate'] = item[u'MHS 5s'] * 1000
			device[u'AcceptedShares'] = item[u'Accepted']
			device[u'RejectedShares'] = item[u'Rejected']
			device[u'HardwareErrors'] = item[u'Hardware Errors']
			device[u'Utility'] = item[u'Utility']		
			data2.append(device)

		req = urllib2.Request(reqURL)
		req.add_header('Content-Type', 'application/json')
		
		#print data2
		
	except Exception:
		import traceback
		logging.warning('Generic Exception: ' + traceback.format_exc())		
	
	try: 
		response = urllib2.urlopen(req, json.dumps(data2), 30)
	except urllib2.HTTPError, e:
		logging.warning('HTTPError = ' + str(e.code))
	except urllib2.URLError, e:
		logging.warning('URLError = ' + str(e.reason))
	except httplib.HTTPException, e:
		logging.warning('HTTPException')
	except Exception:
		import traceback
		logging.warning('Generic Exception: ' + traceback.format_exc())
		
	print '['+str(datetime.datetime.now()).split('.')[0]+']  Sending to MobileMiner API from '+machineName 

	getCommandsURL = 'https://mobileminer.azurewebsites.net/api/RemoteCommands?emailAddress='+emailAddy+'&applicationKey='+applicationKey+'&machineName='+machineName+'&apiKey='+apiKey
        getCommandsReq = urllib2.Request(getCommandsURL)
        getCommandsReq.add_header('Content-Type', 'application/json')

	try:
                getCommandsResponse = urllib2.urlopen(getCommandsReq, None, 30)
		commands = json.loads(getCommandsResponse.read())
		for d in commands:
			commandText = d['CommandText']
			actions[commandText]()
		        removeCommandsURL = 'https://mobileminer.azurewebsites.net/api/RemoteCommands?emailAddress='+emailAddy+'&applicationKey='+applicationKey+'&machineName='+machineName+'&apiKey='+apiKey+'&commandId='+str(d['Id'])
		        removeCommandsReq = urllib2.Request( removeCommandsURL)
			removeCommandsReq.get_method = lambda: 'DELETE'
		        removeCommandsReq.add_header('Content-Type', 'application/json')
			urllib2.urlopen(removeCommandsReq, None, 30)
        except Exception:
		import traceback
                logging.warning('GetCommands Generic Exception: ' + traceback.format_exc())

	time.sleep(5)
