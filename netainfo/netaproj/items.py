# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class NetaprojItem(scrapy.Item):
    # define the fields for your item here like:
    # Primary fields

    Candidate = Field()
    Winner = Field()
    Party = Field()
    Criminal_Case = Field()
    Education = Field()
    Age = Field()
    Total_Assets = Field()
    Liabilities = Field()

    # Calculated fields
    # Housekeeping fields
    State = Field()
    Year = Field()
    District = Field()
    Constituency = Field()
    
class LSItem(scrapy.Item):
    # define the fields for your item here like:
    # Primary fields

    Candidate = Field()
    Winner = Field()
    Party = Field()
    Criminal_Case = Field()
    Education = Field()
    Age = Field()
    Total_Assets = Field()
    Liabilities = Field()

    # Calculated fields
    # Housekeeping fields
    State = Field()
    Year = Field()
    District = Field()