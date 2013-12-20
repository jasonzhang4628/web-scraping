#!/usr/bin/env python

"""
web-scraper.py

Looks for specific items on a given webpage, writes the data to a .csv file.
Looks for webpages from a command line argument or standard input. 
Input file should only have one url per line.

Usage:

python web-scraper.py target-urls.txt records.csv

@author: Jason L. Zhang
@maintainer: Jason L. Zhang
@email: jason.zhang@berkeley.edu
@status: Prototype
"""

import csv
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
          \n 'python web-scraper.py [URL-TARGETS] [OUTPUT-DESTINATION]' \
          \n Command line arguments are required."
    sys.exit(0)

if len(sys.argv) != 3:
    usage()

fields = ["access_date", "access_time", "URL", "last_update", "institution",
          "pageviews", "address", "website", "email", "membership",
          "deliveries", "rating", "review_count", "classification",
          "item_name", "price_whole", "price_part1", "price_part2",
          "price_part3", "price_bundle", "price_other"]

template = {k : "" for k in fields}

targets = open(sys.argv[1], 'r')
destination = open(sys.argv[2], 'a')
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
    except httplib.BadStatusLine as e:
        print('Error fetching ' + url)

    return html

def parse_site(url):
    """
    Converts URL to HTML and parses for relevant results.
    """
    html = request_site(url)
    
    output = template.copy()
    output["access_date"] = time.strftime("%m/%d/%Y")
    output["access_time"] = time.strftime("%H:%M:%S")
    output["URL"] = url
    output["last_update"] = re.search('span class=\'timeago\' ' 
                                      + 'title=".*?">(.*?)<', html).group(1)
    output["institution"] = re.search('<h1 itemprop="name">(.*?)</h1>',
                                      html).group(1)
    output["pageviews"] = re.search('<em>\(([0-9,]*) hits\)</em>',
                                    html).group(1)
    address = re.search('<div class="span3">ADDRESS</div><div class="span9">'
                        + '(.*?)</div></div>', html)
    if address != None:
        output["address"] = re.sub('<.*?>', ' ', address.group(1))
    output["website"] = re.search('<div class="span3">WEBSITE</div><div class='
                                  + '"span9"><a href="(.*?)" target="_blank">'
                                  + '.*?</a></div></div>', html).group(1)
    output["email"] = re.search('<div class="span3">EMAIL</div><div class="'
                                + 'span9"><a href=".*?">(.*?)</a></div></div>',
                                html).group(1)
    output["membership"] = re.search('<div class="span3">MEMBER SINCE</div>\s+'
                                     + '<div class="span9">(.*?)</div>',
                                     html).group(1)
    if re.search('<b style="color:#000;">*Deliveries Only*</b>', html) != None:
        output["deliveries"] = "Deliveries Only"
    output["rating"] = re.search('<span class="rating">\s+(.*?)\s+</span>',
                                 html).group(1)
    output["review_count"] = re.search('<span class="rating">\s+.*?\s+</span>'
                                    + '\s+<strong>\((.*?) reviews\)</strong>',
                                    html).group(1)
    results = re.finditer('data-category-name="([^"]+)"\s+' + \
        'data\-json="([^"]+)"', html)

    for result in results:
        # Loads the JSON data stored in the document
        json_raw = result.group(2)
        json_data = json.loads(html_decode(json_raw))

        # Output the relevant results
        output["classification"] = result.group(1)
        output["item_name"] = json_data['name']
        output["price_whole"] = json_data['price_gram']
        output["price_part1"] = json_data['price_eighth']
        output["price_part2"] = json_data['price_quarter']
        output["price_part3"] = json_data['price_half_gram']
        output["price_bundle"] = json_data['price_ounce']
        output["price_other"] = json_data['price_unit']
        try:
            output_csv(output)
        except:
            print "Error on item: \n"
            for key in output:
                print output[key]

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

def __main__():
    for site in targets:
        parse_site(site.strip())

if __name__ == "__main__":
    __main__()
