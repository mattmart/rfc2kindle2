#!/usr/bin/env python -B

'''
helper class to fetch constants for rfc2mobi
'''

import ConfigParser

config = ConfigParser.SafeConfigParser({'parDir': './mobiRFC', 'kindlegen':'./kindlegen'})
config.read('rfc2mobi.cfg')

def get_defaultdirectory():
    return config.get('rfc2mobi','parDir')

def get_kindlegen():
    return config.get('rfc2mobi','kindlegen')

