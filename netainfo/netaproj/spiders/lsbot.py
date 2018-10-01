# -*- coding: utf-8 -*-
import scrapy
import re
from netaproj.items import NetaprojItem, LSItem

class LsbotSpider(scrapy.Spider):
    name = 'lsbot'
    allowed_domains = ['myneta.info']
    start_urls = ['http://myneta.info/']

    def parse(self, response):
        # get the div containing all LS eections
        ls = response.xpath('//*[@id="main"]/div/div[2]/div/div[1]/div[3]')
        # get individual election divs
        ls_items = ls.css('div.items div.item')

        for ls_item in ls_items:
            # extract text of the election
            item_text = str.strip(ls_item.css("::text").extract_first())
            year = item_text.split(' ')[-1]
            url = ls_item.css("div.sub-links a:contains('All Candidates')::attr('href')").extract_first()
            request = scrapy.Request(response.urljoin(url), callback=self.parse_state_elec)
            request.meta['Year'] = year
            yield request


    def parse_state_elec(self, response):
        # states = response.css("h5.title")
        districts = response.css('table[width="100%"] td div.items')

        for district in districts:
            dist_name = str.strip(district.css('a::text').extract_first())
            url = district.css('a::attr(href)').extract_first()
            request = scrapy.Request(response.urljoin(url), callback=self.parse_state_year)
            request.meta['Year'] = response.meta['Year']
            request.meta['District'] = dist_name
            yield request

    def parse_state_year(self, response):
        item = LSItem()
        # Get the state name from the page
        state = response.css('div.title h3::text').extract_first()

        # Extract multi-word district names both lower and upper case from headings h3 text
        m =re.search(r':((?:[A-Za-z]+ ?)+)', state)
        state_name = str.strip(m.group(1))
       
        # get rows for all the candidates in a constituency
        cand_rows = response.css('table[id="table1"] tr[onmouseover]')

        for row in cand_rows:
            item['Candidate'] = row.css('td')[0].css('::text').extract_first()
            outcome = row.css('td')[0].css('font::text').extract_first()
            if outcome:
                item['Winner'] = 'Yes'
            else:
                item['Winner'] = 'No'
            item['Party'] = row.css('td')[1].css('::text').extract_first()
            item['Criminal_Case'] = row.css('td')[2].css('::text').extract_first()
            item['Education'] = row.css('td')[3].css('::text').extract_first()
            item['Age'] = row.css('td')[4].css('::text').extract_first()
            item['Total_Assets'] = row.css('td')[5].css('::text').extract_first()
            item['Liabilities'] = row.css('td')[6].css('::text').extract_first()
            item['State'] = state_name
            item['Year'] = int(response.meta['Year'])
            item['District'] = response.meta['District']
            yield item