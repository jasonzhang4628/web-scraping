#!/usr/bin/env python

"""
web-scraper.py

Looks for specific items on a given webpage, writes the data to a .csv file.
Looks for webpages from a command line argument or standard input. 
Input file should only have one url per line.

Optional third commandline argument to create an output log.

Usage:

python web-scraper.py target-urls.txt records.csv [output-log]

@author: Jason L. Zhang
@maintainer: Jason L. Zhang
@email: jason.zhang@berkeley.edu
@status: Prototype
"""

import csv
import random
import time
import httplib
import json
import re
import sys
import ssl
from urlparse import urlparse

def usage():
    """
    Prints a message regarding usage this program's usage and exits.
    """
    print "Incorrect argument format. Script should be called as follows: \
          \n 'python web-scraper.py URL-TARGETS OUTPUT-DESTINATION [LOG.csv]' \
          \n Bracketed arguments are optional. Log file will duplicate most \
          recent changes only, optimally named DATE.csv for personal records."
    sys.exit(0)

if len(sys.argv) != 3 and len(sys.argv) != 4:
    usage()

if len(sys.argv) == 4:
    log = csv.writer(open(sys.argv[3], 'wb'))

fields = ["access_date", "access_time", "URL", "last_update", "institution",
          "pageviews", "address", "website", "email", "membership",
          "deliveries", "rating", "review_count", "classification",
          "item_name"]

template = {k : "" for k in fields}

targets = open(sys.argv[1], 'rb')
destination = open(sys.argv[2], 'ab')
writer = csv.writer(destination)

def html_decode(i):
    """
    Decodes the HTML into original text.

    >>> html_decode("She &amp; Him")
    She & Him
    """
    return i.replace('&quot;', '"').replace('&gt;', '>'). \
        replace('&lt;', '<').replace('&amp;', '&').replace('&#x27', "'")

def request_site(url):
    """
    Returns html of a site from URL.
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
    except:
        print('Error fetching ' + url)

    return html

def parse_site(url):
    """
    Converts URL to HTML and parses for relevant results.
    """

    yielded_output = False
    html = request_site(url)
    
    output = template.copy()
    output["access_date"] = time.strftime("%m/%d/%Y")
    output["access_time"] = time.strftime("%H:%M:%S")
    output["URL"] = url
    
    last_update = re.search('span class=\'timeago\' ' 
                                      + 'title=".*?">(.*?)<', html)
    if last_update != None:
        output["last_update"] = last_update.group(1)

    output["institution"] = re.search('<h1 itemprop="name">(.*?)</h1>',
                                      html).group(1)
    
    pageviews = re.search('<em>\(([0-9,]*) hits\)</em>', html)
    if pageviews != None:
        output["pageviews"] = pageviews.group(1)

    address = re.search('<div class="span3">ADDRESS</div><div class="span9">'
                        + '(.*?)</div></div>', html)
    if address != None:
        output["address"] = re.sub('<.*?>', ' ', address.group(1))
   
    website = re.search('<div class="span3">WEBSITE</div><div class='
                                  + '"span9"><a href="(.*?)" target="_blank">'
                                  + '.*?</a></div></div>', html)
    if website != None:
        output["website"] = website.group(1)
   
    email = re.search('<div class="span3">EMAIL</div><div class="'
                                + 'span9"><a href=".*?">(.*?)</a></div></div>',
                                html)
    if email != None:
        output["email"] = email.group(1)
    
    membership = re.search('<div class="span3">MEMBER SINCE</div>\s+'
                                     + '<div class="span9">(.*?)</div>',
                                     html)
    if membership != None:
        output["membership"] = membership.group(1)

    if re.search('Deliveries Only', html) != None:
        output["deliveries"] = "Deliveries Only"
    
    rating = re.search('<span class="rating">\s+(.*?)\s+</span>', html)
    if rating != None:
        output["rating"] = rating.group(1)

    review_count = re.search('<span class="rating">\s+.*?\s+</span>'
                                    + '\s+<strong>\((.*?) reviews\)</strong>',
                                    html)
    if review_count != None:
        output["review_count"] = review_count.group(1)

    results = re.finditer('data-category-name="([^"]+)"\s+' + \
        'data\-json="([^"]+)"', html)

    for result in results:
        # Loads the JSON data stored in the document
        json_raw = result.group(2)
        json_data = json.loads(html_decode(json_raw))
        item_fields = ["classification", "item_name"]
        for item in item_fields:
            output[item] = ''
        # Output the relevant results
        output["classification"] = result.group(1)
        output["item_name"] = json_data['name']
        try:
            output_csv(output)
            yielded_output = True
        except:
            print "Error on item: \n"
            for key in output:
                print output[key]
            print "\nskipping item..."
    if not yielded_output:
        output_csv(output)

def output_csv(output_data):
    """
    Writes the given output to the csv file set on the command line.
    """
    output = []
    for item in fields:
        if output_data[item] == '0.0' or output_data[item] == 0:
            output.append('')
        else:
            output.append(output_data[item])
    writer.writerow(output)
    if len(sys.argv) == 4:
        log.writerow(output)

def __main__():
    try:
        for site in targets:
            try:
                site = site.strip()
                time.sleep(random.random())
                parse_site(site)
            except:
                print "Error in " + site
    except:
        print "Input error."
if __name__ == "__main__":
    __main__()
