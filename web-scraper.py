#!/usr/bin/env python

"""
web-scraper.py

Looks for specific items on a given webpage, writes the data to a .csv file.
Looks for webpages from a file named 'TARGETS.txt' in same directory.

@author: Jason L. Zhang
@maintainer: Jason L. Zhang
@email: jason.zhang@berkeley.edu
@status: Prototype
"""

import csv
import datetime
import fileinput
import httplib
import json
import re
import ssl
from urlparse import urlparse

# 'https://weedmaps.com/dispensaries/california/oakland/blum?c=main'

def html_decode(i):
    """
    Decodes the HTML into original text.

    >>> html_decode("She &amp; Him")
    She & Him
    """
    return i.replace('&quot;', '"').replace('&gt;', '>'). \
        replace('&lt;', '<').replace('&amp;', '&')

def request_site(url):
    """
    Returns html of a site from url.
    """
    url_info = urlparse(url)

    scheme = url_info.scheme
    hostname = url_info.netloc
    query_path = url[url.find(hostname) + len(hostname):]
    is_ssl = scheme == "https"
    remote_port = 443 if is_ssl else 80

    # Check if a port number is specified
    if hostname.find(":") != -1:
        try:
            remote_port = int(hostname[hostname.find(":") + 1 : ].strip())
            hostname = hostname[ : hostname.find(":")]
        except ValueError as e:
            pass

    if is_ssl:
        try:
            site = httplib.HTTPSConnection(hostname, remote_port)
        except ssl.SSLError as e:
            site = httplib.HTTPConnection(hostname, remote_port)
    else:
        site = httplib.HTTPConnection(hostname, remote_port)
    site.request('GET', query_path)

    try:
        html = site.getresponse().read()
    except httplib.BadStatusLine as e:
        print "{}".format(e)

    return html

def parse_site(url):
    html = request_site(url)

    timeago = re.search('class="timeago"\s+title="([^"]+)"', html)
    if timeago:
        print timeago.group(1)


    

#   results = re.finditer('data\-json="([^"]+)"', html)
#   print results
#   for result in results:
#       json_raw = result.group(1)
#       json_data = json.loads(html_decode(json_raw))
#       for item in json_data:
#           print("The value of {} is {}".format(item, json_data[item]))

def __main__():
    for site in fileinput.input():
        print site
        parse_site(site.strip())

if __name__ == "__main__":
    __main__()

#   def csv_setup():
#       """Sets up a csv file to store the data. Name of the file is the current
#       date, expressed as previously specified format in 'DATE_FORMAT'. Prints a
#       warning message regarding usage.
#       """
#       today = datetime.date.today()
#       today_string = today.strftime(DATE_FORMAT)
#       file_name = today_string + '.csv'
#       output = open(file_name, 'wb')
#       writer = csv.writer(output)
#       writer.writerow(categories)
#       return writer, file_name




