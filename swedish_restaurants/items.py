# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SwedishRestaurantsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class RestaurantItem(scrapy.Item):
   name = scrapy.Field()
   type = scrapy.Field()
   city = scrapy.Field()
   url = scrapy.Field()
   email = scrapy.Field()
   address = scrapy.Field()
   num_employees = scrapy.Field()
   telephone = scrapy.Field()
   last_year_revenue = scrapy.Field()
   last_year_result_after_financial_assets = scrapy.Field()
   cash_flow_word = scrapy.Field()
   cash_flow_percent = scrapy.Field()
   profit_margin_word = scrapy.Field()
   profit_margin_percent = scrapy.Field()
   solidity_word = scrapy.Field()
   solidity_percent = scrapy.Field()