import httplib
from pyamf.remoting.client import RemotingService
from urlparse import urlparse

# URL hosting the Flash player
FLASH_PLAYER_URL = 'http://www.rdio.com/api/swf'

# API endpoint for AMF
AMF_ENDPOINT = 'http://www.rdio.com/api/1/amf/'


def resolve_url(url):
    '''Recursively resolve the given URL, following 3xx redirects. Returns
       the final URL that did not result in a redirect.'''

    url = FLASH_PLAYER_URL
    while True:
        pr = urlparse(url)

        hc = httplib.HTTPConnection(pr.hostname)
        hc.request('GET', pr.path)
        hr = hc.getresponse()
        
        if hr.status / 100 == 3:
            url = hr.getheader('location')
        else:
            return url


def get_rtmpdump_info(domain, token, track, flash_url=None):
    '''Return a tuple of (app ID, RTMP url); raises an Exception on failure.'''

    if not flash_url:
        flash_url = resolve_url(FLASH_PLAYER_URL)

    svc = RemotingService(AMF_ENDPOINT, referer=flash_url, amf_version=3)
    svc.addHeader('Auth', chr(5))
    rdio_svc = svc.getService('rdio')

    pi = rdio_svc.getPlaybackInfo({
        'domain': domain,
        'playbackToken': token,
        'manualPlay': False,
        'playerName': 'api_544189',
        'type': 'flash',
        'key': track})
    if not pi:
        raise Exception, 'Failed to get playback info'

    return (
        'ondemand?' + pi['auth'],
        'rtmpe://cp102543.edgefcs.net:1935/ondemand/mp3:' + \
            pi['surl'].replace('30s-96', 'full-192'))
