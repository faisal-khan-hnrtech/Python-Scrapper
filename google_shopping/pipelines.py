# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# import pymssql
import mysql.connector

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class GoogleShoppingPipeline(object):

    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='admin',
            passwd='password',
            database='google_shopping',
        )
        self.curr = self.conn.cursor()

    def create_table(self):
        self.curr.execute("""DROP TABLE IF EXISTS Shopping""")
        self.curr.execute("""create table shopping(sold_by text, item_price text, tax_price text, 
        shipping_price text, gtin text, sku text)""")

    def process_item(self, item, spider):
        self.store_db(item)
        return item

    def store_db(self, item):
        if 'gtin' in item:
            try:
                self.curr.execute("""insert into google_shopping_products value (%s,%s,%s,%s,%s,%s)""", (
                    item['sold_by'],
                    item['item_price'],
                    item['tax_price'],
                    item['shipping_price'],
                    item['gtin'],
                    item['sku'],
                ))
                self.conn.commit()
            except:
                print("Error %d: %s")

        if 'item_price' in item:
            try:

                self.curr.execute("""insert into google_shopping_products value (%s,%s,%s,%s)""", (
                    item['sold_by'],
                    item['item_price'],
                    item['tax_price'],
                    item['shipping_price'],
                ))
                self.conn.commit()
            except:
                print("Error %d: %s")
