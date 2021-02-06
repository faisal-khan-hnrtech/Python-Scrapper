# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GoogleShoppingItem(scrapy.Item):
    sold_by = scrapy.Field()
    item_price = scrapy.Field()
    total_price = scrapy.Field()
    tax_price = scrapy.Field()
    shipping_price = scrapy.Field()
    url = scrapy.Field()

    # google_shopping_products
    brand = scrapy.Field()
    sku = scrapy.Field()
    google_brand_name = scrapy.Field()
    title = scrapy.Field()
    gtin = scrapy.Field()
    google_part_numbers = scrapy.Field()
    page_url = scrapy.Field()

