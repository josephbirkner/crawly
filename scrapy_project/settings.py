# -*- coding: utf-8 -*-

# Scrapy settings for scrapy_project project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'scrapy_project'

SPIDER_MODULES = ['scrapy_project.spiders']
NEWSPIDER_MODULE = 'scrapy_project.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'scrapy_project (+http://www.yourdomain.com)'

ITEM_PIPELINES = {    
    'scrapy_project.pipelines.GeoLingDbPipeline': 500,    
}  

DB_SERVER = 'MySQLdb'
DB_CONNECT = {
    'db': 'hackgeoling',
    'user': 'root',
    'passwd': 'root',
    'host': 'localhost',
    'charset': 'utf8',
    'use_unicode': True,
}   
