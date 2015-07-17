from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy_project.items import CrawlyItem
from scrapy.selector import Selector
from langdetect import detect, detect_langs
from urlparse import urlparse

import xml.etree.ElementTree
import re
import string
import HTMLParser
import subprocess

HTML_SCRIPT_RE = re.compile(r"<script[a-zA-Z0-9\W_]+<\/script>")
HTML_STYLE_RE = re.compile(r"<style[a-zA-Z0-9\W_]+<\/style>")
HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile("["+string.whitespace+"]+")
STRING_IP = re.compile(r"([0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4})")

HTML_PARSER = HTMLParser.HTMLParser()

def strip_tags(html):
    html_without_tags = HTML_SCRIPT_RE.sub("",html)
    html_without_tags = HTML_STYLE_RE.sub("",html_without_tags)
    #    try:
    #        html_without_tags = ''.join(xml.etree.ElementTree.fromstring(html_without_tags).itertext())
    #    except Exception:
    #        print "################### ERROR IN TAG REPLACE ###################"
    html_without_tags = HTML_TAG_RE.sub("", html_without_tags)
    html_without_tags = HTML_PARSER.unescape(html_without_tags)
    html_without_tags = WHITESPACE_RE.sub(" ", html_without_tags)
    return html_without_tags

def get_html_response_language(response):
    try:
        raw_body = strip_tags(response.body_as_unicode())
        langs = detect_langs(raw_body)
        return (langs[0].lang, langs[-len(langs)+1].lang)
        # return detect(raw_body)
    except Exception,e:
        print str(e)
        return "unknown"

def get_host_from_url(url):
    the_uri = urlparse(url)
    return '{uri.hostname}'.format(uri=the_uri)

def load_ip_ranges(file):
    result = []
    for iprange in open(file).read().split('\n'):
        iprange = iprange.strip().split('\t')
        if len(iprange) >= 4:
            result.append((long(iprange[0]), long(iprange[1]), iprange[2], iprange[3]))
    return result

ipranges = load_ip_ranges("iplocations.csv")
hostlanguages = {}

def get_country_for_host(host):
    # Find ip for host with ping
    p = subprocess.Popen(['ping','-c','1','-a',host],stdout=subprocess.PIPE)
    result = p.communicate()[0]
    stringip = ""
    try:
        stringip = STRING_IP.findall(result)[0]
    except Exception:
        print "Could not ping host",host,"Ping result:",result
        return "unknown"

    numericip = 0L
    shl = 24L
    # Convert string ip to numeric ip
    for ipbyte in stringip.split("."):
        numericip += long(ipbyte) << shl
        shl -= 8L
    country = 'unknown'
    # Lookup numeric ip in ip ranges
    for iprange in ipranges:
        if numericip >= iprange[0] and numericip <= iprange[1]:
            country = iprange[3]
            break
    return country

class MySpider(CrawlSpider):

    name = "crawly"
    start_urls = [
        "http://cn.chinadaily.com.cn",
        "http://russian.rt.com",
    ]
    rules = (
        Rule(
            SgmlLinkExtractor(), # allow=("index\d00\.html", ),restrict_xpaths=('//p[@class="nextpage"]',)
            callback="parse_items", follow= True
        ),)

    def parse_items(crawler, response):
        """
        The lines below is a spider contract. For more info see:
        http://doc.scrapy.org/en/latest/topics/contracts.html
        @url http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/
        @scrapes name
        """
        # Create a new link item
        item = CrawlyItem()

        # Set the basic target parameters
        item["url"] = response.url
        item["t_host"] = get_host_from_url(response.url)
        item["t_country"] = get_country_for_host(item['t_host'])

        lang = get_html_response_language(response)
        item["t_language"] = lang[0]
        item["t_language_alt"] = lang[1]
        hostlanguages[response.url] = item['t_language']
        
        # Try to determine where the link is coming from...
        item["s_host"] = get_host_from_url(response.request.headers.get('Referer', None))
        item["s_country"] = get_country_for_host(item['s_host'])
        item["s_language"] = hostlanguages.get(response.request.headers.get('Referer', None))

        if(item['s_host'] == None or item['s_language'] == None):
            print "Insufficient data:",item['s_host'],item['s_language']
            return []
        else:
            return [item]



