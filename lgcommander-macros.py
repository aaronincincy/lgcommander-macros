#!/usr/bin/env python3

import configparser
import time
import http.client
import xml.etree.ElementTree as etree
import socket
import re
import sys

config = configparser.ConfigParser()
headers = {'Content-Type': 'application/atom+xml'}

def loadConfig():
	config.read('config.ini')
	writeConfig = False
	if 'LGTV' not in config:
		config['LGTV'] = {'ipAddress': getip()}
		writeConfig = True
	if 'pairingKey' not in config['LGTV'] or not config['LGTV']['pairingKey']:	
		displayKey()
		pairingKey = input('Enter the pairing Key: ')
		config['LGTV']['pairingKey'] = pairingKey
		writeConfig = True
		
	if writeConfig:
		with open('config.ini', 'w') as configfile:
			config.write(configfile)
			
	config['LGTV']['session'] = getSessionId()

def getip():
    strngtoXmit =   'M-SEARCH * HTTP/1.1' + '\r\n' + \
                    'HOST: 239.255.255.250:1900'  + '\r\n' + \
                    'MAN: "ssdp:discover"'  + '\r\n' + \
                    'MX: 2'  + '\r\n' + \
                    'ST: urn:schemas-upnp-org:device:MediaRenderer:1'  + '\r\n' +  '\r\n'

    bytestoXmit = strngtoXmit.encode()
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    sock.settimeout(3)
    found = False
    gotstr = 'notyet'
    i = 0
    ipaddress = None
    sock.sendto( bytestoXmit,  ('239.255.255.250', 1900 ) )
    while not found and i <= 5 and gotstr == 'notyet':
        try:
            gotbytes, addressport = sock.recvfrom(512)
            gotstr = gotbytes.decode()
        except:
            i += 1
            sock.sendto( bytestoXmit, ( '239.255.255.250', 1900 ) )
        if re.search('LG', gotstr):
            ipaddress, _ = addressport
            found = True
        else:
            gotstr = 'notyet'
        i += 1
    sock.close()
    if not found : sys.exit("Lg TV not found")
    return ipaddress

def displayKey():
    conn = http.client.HTTPConnection( config['LGTV']['ipAddress'], port=8080)
    reqKey = '<?xml version="1.0" encoding="utf-8"?><auth><type>AuthKeyReq</type></auth>'
    conn.request('POST', '/hdcp/api/auth', reqKey, headers=headers)
    httpResponse = conn.getresponse()
    if httpResponse.reason != 'OK' : sys.exit('Network error')
    return httpResponse.reason
	
def getSessionId():
	conn = http.client.HTTPConnection( config['LGTV']['ipAddress'], port=8080)
	pairCmd = '<?xml version="1.0" encoding="utf-8"?><auth><type>AuthReq</type><value>' \
			+ config['LGTV']['pairingKey'] + '</value></auth>'
	conn.request('POST', '/hdcp/api/auth', pairCmd, headers=headers)
	httpResponse = conn.getresponse()
	if httpResponse.reason != 'OK' : return httpResponse.reason
	tree = etree.XML(httpResponse.read())
	return tree.find('session').text

def handleCommand(cmdcode):
    conn = http.client.HTTPConnection( config['LGTV']['ipAddress'], port=8080)
    cmdText = '<?xml version="1.0" encoding="utf-8"?><command><session>' \
                + config['LGTV']['session']  \
                + '</session><type>HandleKeyInput</type><value>' \
                + str(cmdcode) \
                + '</value></command>'
    conn.request('POST', '/hdcp/api/dtv_wifirc', cmdText, headers=headers)
    httpResponse = conn.getresponse()
	
def getCommand(cmd):
	try:
		return int(cmd)
	except ValueError:
		return {
			"status_bar": 35,
			"quick_menu": 69,
			"home_menu": 67,
			"premium_menu": 89,
			"installation_menu": 207,
			"factory_advanced_menu1": 251,
			"factory_advanced_menu2": 255,
			"power_off": 8,
			"sleep_timer": 14,
			"left": 7,
			"right": 6,
			"up": 64,
			"down": 65,
			"select": 68,
			"back": 40,
			"exit": 91,
			"red": 114,
			"green": 113,
			"yellow": 99,
			"blue": 97,
			"zero": 16,
			"one": 17,
			"two": 18,
			"three": 19,
			"four": 20,
			"five": 21,
			"six": 22,
			"seven": 23,
			"eight": 24,
			"nine": 25,
			"underscore": 76,
			"play": 176,
			"pause": 186,
			"fast_forward": 142,
			"rewind": 143,
			"stop": 177,
			"record": 189,
			"tv_radio": 15,
			"simplink": 126,
			"input": 11,
			"component_rgb_hdmi": 152,
			"component": 191,
			"rgb": 213,
			"hdmi": 198,
			"hdmi1": 206,
			"hdmi2": 204,
			"hdmi3": 233,
			"hdmi4": 218,
			"av1": 90,
			"av2": 208,
			"av3": 209,
			"usb": 124,
			"slideshow_usb1": 238,
			"slideshow_usb2": 168,
			"channel_up": 0,
			"channel_down": 1,
			"channel_back": 26,
			"favorites": 30,
			"teletext": 32,
			"t_opt": 33,
			"channel_list": 83,
			"greyed_out_add_button": 85,
			"guide": 169,
			"info": 170,
			"live_tv": 158,
			"av_mode": 48,
			"picture_mode": 77,
			"ratio": 121,
			"ratio_4_3": 118,
			"ratio_16_9": 119,
			"energy_saving": 149,
			"cinema_zoom": 175,
			"3d": 220,
			"factory_picture_check": 252,
			"volume_up": 2,
			"volume_down": 3,
			"mute": 9,
			"audio_language": 10,
			"sound_mode": 82,
			"factory_sound_check": 253,
			"subtitle_language": 57,
			"audio_description": 145,
		}.get(cmd)
	
def main(argv):
	loadConfig()
	if len(argv):
		for arg in argv:
			print(arg)
			if arg == 'pair':
				displayKey()
			else:
				cmd = getCommand(arg)
				if cmd != None:
					handleCommand(cmd)
			time.sleep(2)
		
if __name__ == "__main__":
	main(sys.argv[1:])	


