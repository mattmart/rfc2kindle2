'''
helper class to fetch constants for rfc2mobi
'''

from configparser import ConfigParser 

config = ConfigParser({'parDir': './mobiRFC', 'kindlegen':'./kindlegen'})
config.read('rfc2mobi.cfg')

def get_default_dir():
    return config.get('rfc2mobi','parDir')

def get_kindlegen():
    return config.get('rfc2mobi','kindlegen')

def get_css_src_dir():
    return config.get('rfc2mobi','cssDirSrc')

def get_css_dir():
    return config.get('rfc2mobi','cssDir')

def get_images_dir():
    return config.get('rfc2mobi','imgDir')
