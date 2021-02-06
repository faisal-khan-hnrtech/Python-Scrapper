import scrapy
from scrapy.http import FormRequest, Request
import csv
import itertools
from scrapy.utils.response import open_in_browser
from urllib.parse import urlencode
from ..items import GoogleShoppingItem
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import itertools


class ShgSpider(scrapy.Spider):
    name = 'shg'
    start_urls = ['https://shopping.google.com/']
    gtin = ''
    sku = ''
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}

    def parse(self, response):
        sku = ['LSN120HEV2 lg']
        with open('/home/nisl/Downloads/Google Shopping SKUs - Sheet1.csv', 'r') as file:
            reader = csv.reader(file)
            for line in itertools.islice(reader, 10):
        # for i in sku:
                ved = response.xpath('//*[@id="kO001e"]/c-wiz/form/@data-ved').extract_first()
                params = {
                    'psb': '1',
                    'tbm': 'shop',
                    'q': str(line[0]) + ' ' + str(line[2]),
                    # 'q': str(line[0]),
                    'hl': 'en-US',
                    'ved': str(ved)
                }
                self.sku = str(line[0]) + ' ' + str(line[2])
                # self.sku = str(i)
                url = "https://www.google.com/search?" + urlencode(params)
                print(url)
                yield scrapy.Request(url, callback=self.parse2, meta={'dont_redirect': True,
                                                                      'handle_httpstatus_list': [302],
                                                                      'sku': str(line[0]) + ' ' + str(line[2])})

    def parse2(self, response):
        url = response.xpath('/html/body/div[6]/div[2]/div/a/@href').extract_first()
        if not url:
            url = response.xpath('/html/body/div[5]/div[2]/div/a/@href').extract_first()
        print(url)
        if url:
            link = 'https://www.google.com' + str(url)
            yield response.follow(link, callback=self.final_data, meta={'link': link, 'sku': response.meta['sku']})

    def final_data(self, response):
        item = GoogleShoppingItem()

        driver = webdriver.Chrome(executable_path='/home/nisl/WORKING_DIRECTORY/New folder/chromedriver')
        driver.get(response.meta['link'])
        time.sleep(8)
        try:
            gtin = driver.find_element(By.XPATH, '//*[@id="specs"]/div[2]/table/tbody/tr[4]/td[2]').text
            title = driver.find_element(By.XPATH, '//*[@id="sg-product__pdp-container"]/div/div[3]/div[1]/span').text
            google_part_numbers = driver.find_element(By.XPATH, '//*[@id="specs"]/div[2]/table/tbody/tr[3]/td[2]').text
            google_brand_name = driver.find_element(By.XPATH, '//*[@id="specs"]/div[2]/table/tbody/tr[2]/td[2]').text
            brand = driver.find_element(By.XPATH, '//*[@id="specs"]/div[2]/table/tbody/tr[2]/td[2]').text
            page_url = driver.current_url

            item['gtin'] = gtin
            item['title'] = title
            item['google_part_numbers'] = google_part_numbers
            item['google_brand_name'] = google_brand_name
            item['brand'] = brand
            item['page_url'] = page_url
            item['sku'] = response.meta['sku']
            yield item
        except Exception as e:
            gtin = ''

        all_data = response.xpath('//*[@id="online"]/div')
        i = 1
        for data in all_data:
            i = i + 1
            sold_by = data.xpath('./div[2]/a/text()').extract_first()
            item_price = data.xpath('./div[1]/div[1]/b/text()').extract_first()
            shipping_price = data.xpath('./div[1]/div[3]/text()').extract_first()
            tax_price = data.xpath('./div[1]/div[2]/text()').extract_first()
            url = data.xpath('./div[2]/a/@href').extract_first()
            if item_price:
                if '$' in item_price:
                    item_price = item_price.replace('$', '')
            if tax_price:
                if "+$ tax" in tax_price:
                    tax_price = str(tax_price).replace('+$', '')
                    tax_price = str(tax_price).replace('tax', '')
            # next_page = data.xpath('./div[1]/div[2]/a/text()').extract_first()

            # if next_page == "Next >":
            #     next_page_url = data.xpath('./div[1]/div[2]/a/@href').extract_first()
            #     link = 'https://www.google.com' + str(next_page_url)
            #     yield response.follow(link, callback=self.final_data, meta={'link': response.meta['link'],
            #                                                                 'sku': response.meta['sku']})
            if sold_by:
                item['sold_by'] = sold_by
                item['item_price'] = item_price
                if "Free shipping" in shipping_price:
                    item['shipping_price'] = 0.0
                else:
                    item['shipping_price'] = shipping_price
                item['tax_price'] = tax_price
                item['url'] = url

                yield item

