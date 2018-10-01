# -*- coding: utf-8 -*-
import scrapy
import re
from netaproj.items import NetaprojItem


class NetabotSpider(scrapy.Spider):
    name = 'netabot'
    allowed_domains = ['myneta.info']
    start_urls = ['http://myneta.info//']

    def parse(self, response):
        # Get the state urls
        state_urls = response.css('div.grid_3 .item>a')

        #create a request for each state
        for url in state_urls:
            # get url of the state
            url_state = url.css('a::attr("href")').extract_first()
            request = scrapy.Request(response.urljoin(url_state), callback=self.parse_state_item)
            # get name of the state and pass to response
            request.meta['State'] = url.css('a::text').extract_first()
            yield request

    
    def parse_state_item(self, response):
        # Get all election years of the state
        election_years = response.css("div.grid_6 div.items div.item")

        # for each year extract 'All candidates link'
        for election_year in election_years:
            #extract link for 'All Candidates'
            url = election_year.css('a:contains("All Candidates")::attr("href")').extract_first()
            request = scrapy.Request(response.urljoin(url), callback=self.parse_state_elec)
            # Get the year of election
            year_of_election = str.strip(election_year.css('div.item h3::text').extract_first())
            request.meta['Year'] = year_of_election.split(" ")[-1]
            request.meta['State'] = response.meta['State']
            yield request
    
    
    def parse_state_elec(self, response):
        # Get all the constituency divs from the table
        const_divs = response.css('table[width="100%"] td div.items')

        for row in const_divs:
            # Get the url for each constituency
            url = row.css('a::attr(href)').extract_first()

            request = scrapy.Request(response.urljoin(url), callback=self.parse_const_cand)
            request.meta['Year'] = response.meta['Year']
            request.meta['State'] = response.meta['State']
            request.meta['Constituency'] = row.css('a::text').extract_first()

            yield request

    def parse_const_cand(self, response):
        item = NetaprojItem()

        # Get the district name from the page
        district = response.css('div.title h3::text').extract_first()
        # Extract multi-word district names both lower and upper case from headings h3 text
        dis_name = re.search(r':(([A-Za-z]+ ?)+)', district)
        
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
            item['State'] = response.meta['State']
            item['Year'] = int(response.meta['Year'])
            item['Constituency'] = response.meta['Constituency']
            item['District'] = dis_name.group(1)
            yield item

        






