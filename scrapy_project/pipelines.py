# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from twisted.enterprise import adbapi
from scrapy.utils.project import get_project_settings
# from MySQLdb import escape_string

settings = get_project_settings() 

insert_sql = """
    INSERT INTO `hackgeoling`.`geodata`
        (url, shost, thost, scntry, tcntry, slang, tlang, tlang_alt)
    VALUES
        ('%s', '%s', '%s',  '%s',   '%s',   '%s',  '%s',  '%s')
    """

class GeoLingDbPipeline(object):
    def __init__(self):    
        dbargs = settings.get('DB_CONNECT')    
        db_server = settings.get('DB_SERVER')    
        dbpool = adbapi.ConnectionPool(db_server, **dbargs)    
        self.dbpool = dbpool
    
    def __del__(self):
        self.dbpool.close()

    def process_item(self, item, spider):    
        sql = insert_sql % (
            item['url'],
            item['s_host'],
            item['t_host'],
            item['s_country'],
            item['t_country'],
            item['s_language'],
            item['t_language'],
            item['t_language_alt']
        )
        return self.dbpool.runQuery(sql)

