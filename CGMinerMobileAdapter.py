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

class CgminerAPI(object):
    """ Cgminer RPC API wrapper by Thomas Sileo
		http://thomassileo.com/blog/2013/09/17/playing-with-python-and-cgminer-rpc-api/
	"""
    def __init__(self, host='localhost', port=4028):
        self.data = {}
        self.host = host
        self.port = port

    def command(self, command, arg=None):
        """ Initialize a socket connection,
        send a command (a json encoded dict) and
        receive the response (and decode it).
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((self.host, self.port))
            payload = {"command": command}
            if arg is not None:
                # Parameter must be converted to basestring (no int)
                payload.update({'parameter': unicode(arg)})

            sock.send(json.dumps(payload))
            received = self._receive(sock)
        finally:
            #sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        
        return json.loads(received[:-1])

    def _receive(self, sock, size=4096):
        msg = ''
        while 1:
            chunk = sock.recv(size)
            if chunk:
                msg += chunk
            else:
                break
        return msg

    def __getattr__(self, attr):
        def out(arg=None):
            return self.command(attr, arg)
        return out

def start_mining():
	os.system("mine start")

def stop_mining():
	os.system("mine stop")

def restart_mining():
	os.system("mine restart")

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
	
	settingsPath=os.path.dirname(os.path.abspath(__file__))+"/settings.conf"
	if (not os.path.isfile(settingsPath)):
		print "File settings.conf not found"
		os._exit(-1)
	
	f = open(settingsPath)
	settingsContent = open(settingsPath).readlines()
	
	emailAddy = settingsContent[0].rstrip('\n')
	applicationKey = settingsContent[1].rstrip('\n')
	machineName = settingsContent[2].rstrip('\n')
	
	f.close()
	
	rootURL= 'https://api.mobileminerapp.com'
	apiKey = 'yhErhKxFMCmEkf'
	
	reqURL = rootURL+'/MiningStatisticsInput?emailAddress='+emailAddy+'&applicationKey='+applicationKey+'&apiKey='+apiKey
	req = urllib2.Request(reqURL)
	req.add_header('Content-Type', 'application/json')
	
	parser = argparse.ArgumentParser()
	parser.add_argument("command", default="devs", nargs='?')
	parser.add_argument("parameter", default="", nargs='?')
	parser.add_argument("--hostname", default="localhost")
	parser.add_argument("--port", type=int, default=4028)
	args = parser.parse_args()
	
	data = []
	devices = []
	pools = []
	minerName = 'CGMinerMobileAdapter'
	hashMethod = None
	
	print '['+str(datetime.datetime.now()).split('.')[0]+']  Getting Data from CGMiner RPC API using port:'+str(args.port)
	cgminer = CgminerAPI(args.hostname, args.port)

	try:
		data = cgminer.version()
		minerName = data['VERSION'][0]['Miner']		
	except KeyError:
		minerName = data['STATUS'][0]['Description']
	except Exception:
		import traceback
		logging.warning('Generic Exception: ' + traceback.format_exc())
	
	try:
		pools = cgminer.pools()
		data = cgminer.coin()
		hashMethod = data['COIN'][0]['Hash Method']
	except Exception:
		import traceback
		logging.warning('Generic Exception: ' + traceback.format_exc())

	try:
		devs = cgminer.command(args.command, args.parameter)
		#print devs
		
		for item in devs['DEVS']:
			device = dict()
			device[u'MachineName'] = machineName
			device[u'MinerName'] = minerName
			if hashMethod == u'scrypt':
				device[u'CoinSymbol'] = u'LTC'
				device[u'CoinName'] = u'Litecoin'
				device[u'Algorithm'] = u'Scrypt'
			elif hashMethod == u'sha256':
				device[u'CoinSymbol'] = u'BTC'
				device[u'CoinName'] = u'Bitcoin'
				device[u'Algorithm'] = u'SHA-256'
				
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
			try:
				# bfgminer uses 'MHS 20s'
				# multiply by 1000 to get hashes per second
				device[u'CurrentHashrate'] = item[u'MHS 20s'] * 1000
			except KeyError:
				# cgminer uses 'MHS 5s'
				# multiply by 1000 to get hashes per second
				device[u'CurrentHashrate'] = item[u'MHS 5s'] * 1000
			
			device[u'AcceptedShares'] = item[u'Accepted']
			device[u'RejectedShares'] = item[u'Rejected']
			device[u'HardwareErrors'] = item[u'Hardware Errors']
			device[u'Utility'] = item[u'Utility']
			
			poolIndex = item[u'Last Share Pool']
			device[u'PoolIndex'] = poolIndex
			device[u'PoolName'] = pools[u'POOLS'][poolIndex][u'Stratum URL']
			devices.append(device)
		
	except Exception:
		import traceback
		logging.warning('Generic Exception: ' + traceback.format_exc())
	
	try:
		#print devices
		print '['+str(datetime.datetime.now()).split('.')[0]+']  Sending devices to MobileMiner API from '+machineName
		response = urllib2.urlopen(req, json.dumps(devices), 30)
	except urllib2.HTTPError, e:
		logging.warning('HTTPError = ' + str(e.code))
	except urllib2.URLError, e:
		logging.warning('URLError = ' + str(e.reason))
	except httplib.HTTPException, e:
		logging.warning('HTTPException')
	except Exception:
		import traceback
		logging.warning('Generic Exception: ' + traceback.format_exc())
	
	reqURL = rootURL+'/PoolsInput?emailAddress='+emailAddy+'&applicationKey='+applicationKey+'&apiKey='+apiKey+'&machineName='+machineName
	req = urllib2.Request(reqURL)
	req.add_header('Content-Type', 'application/json')
	
	try:
		poolNames = []
		for pool in pools[u'POOLS']:
			poolNames.append(pool[u'URL'])
		
		#print poolNames
		print '['+str(datetime.datetime.now()).split('.')[0]+']  Sending pools to MobileMiner API from '+machineName
		response = urllib2.urlopen(req, json.dumps(poolNames), 30)
	except urllib2.HTTPError, e:
		logging.warning('HTTPError = ' + str(e.code))
	except urllib2.URLError, e:
		logging.warning('URLError = ' + str(e.reason))
	except httplib.HTTPException, e:
		logging.warning('HTTPException')
	except Exception:
		import traceback
		logging.warning('Generic Exception: ' + traceback.format_exc())
	
	getCommandsURL = rootURL+'/RemoteCommands?emailAddress='+emailAddy+'&applicationKey='+applicationKey+'&machineName='+machineName+'&apiKey='+apiKey
	getCommandsReq = urllib2.Request(getCommandsURL)
	getCommandsReq.add_header('Content-Type', 'application/json')
	
	try:
		print '['+str(datetime.datetime.now()).split('.')[0]+']  Retrieving commands from MobileMiner API for '+machineName
		getCommandsResponse = urllib2.urlopen(getCommandsReq, None, 30)
		commands = json.loads(getCommandsResponse.read())
		#print commands
		
		for d in commands:
			commandText = d['CommandText']
			#print commandText
			
			if commandText in ['START', 'STOP', 'RESTART']:
				actions[commandText]()
			elif 'SWITCH|' in commandText:
				poolName = commandText.split("|")[1]
				poolIndex = poolNames.index(poolName)
				response = cgminer.command('switchpool', poolIndex)
				print response
				
			removeCommandsURL = 'https://mobileminer.azurewebsites.net/api/RemoteCommands?emailAddress='+emailAddy+'&applicationKey='+applicationKey+'&machineName='+machineName+'&apiKey='+apiKey+'&commandId='+str(d['Id'])
			removeCommandsReq = urllib2.Request(removeCommandsURL)
			removeCommandsReq.get_method = lambda: 'DELETE'
			removeCommandsReq.add_header('Content-Type', 'application/json')
			urllib2.urlopen(removeCommandsReq, None, 30)
			
	except Exception:
		import traceback
		logging.warning('GetCommands Generic Exception: ' + traceback.format_exc())
	
	time.sleep(60)
