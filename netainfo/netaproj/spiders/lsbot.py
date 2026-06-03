# -*- coding: utf-8 -*-
import scrapy
import re
from netaproj.items import LSItem


class LsbotSpider(scrapy.Spider):
    name = 'lsbot'
    allowed_domains = ['myneta.info']
    start_urls = ['http://myneta.info/']

    def parse(self, response):
        """Extract Lok Sabha election years from the homepage and follow Winners links."""
        # The homepage has a "Lok Sabha" section with election cards.
        # Each card has links: All Candidates, Winners, etc.
        # Filter cards that contain "Lok Sabha" text in their heading
        ls_cards = response.css('div.w3-card.w3-border')

        for card in ls_cards:
            heading = card.css('div.w3-light-gray b::text').get()
            if not heading or 'Lok Sabha' not in heading:
                continue

            # Extract year from heading (e.g., "Lok Sabha Election 2024" -> "2024")
            year_match = re.search(r'(\d{4})', heading)
            if not year_match:
                continue
            year = year_match.group(1)

            # Find the "Winners" link
            winners_link = card.css(
                'a:contains("Winners")::attr(href)'
            ).get()
            if not winners_link:
                continue

            request = scrapy.Request(
                response.urljoin(winners_link),
                callback=self.parse_winners
            )
            request.meta['Year'] = int(year)
            yield request

    def parse_winners(self, response):
        """Parse a winners page which contains both main winners and bye-election winners."""
        year = response.meta['Year']

        # The winners page has one or two tables:
        # 1. "List of Winners in Lok Sabha YYYY" — main winners
        # 2. "List of Winners in Lok Sabha YYYY Bye-Elections" — bye-election winners
        # Both tables have the same structure.

        # Find all candidate tables on the page (skip the summary/highlights tables)
        tables = response.css('table.w3-table.w3-bordered')

        for table in tables:
            rows = table.css('tr')
            for row in rows:
                cols = row.css('td')
                if len(cols) < 8:
                    continue  # skip header rows or empty rows

                item = LSItem()

                # Candidate name (handles double <a> tags)
                candidate_cell = cols[1]
                item['Candidate'] = self._clean_text(
                    candidate_cell.css('a::text').get()
                )

                # Winner status — everyone on this page is a winner
                item['Winner'] = 'Yes'

                # Constituency name (may include "BYE ELECTION ON ..." for bye-elections)
                item['Constituency'] = self._clean_text(cols[2].css('::text').get())

                item['Party'] = self._clean_text(cols[3].css('::text').get())
                item['Criminal_Case'] = self._clean_text(cols[4].css('::text').get())
                item['Education'] = self._clean_text(cols[5].css('::text').get())
                # Note: No Age column on winners page
                item['Age'] = 'N/A'
                item['Total_Assets'] = self._clean_text(cols[6].css('::text').get()) or 'N/A'
                item['Liabilities'] = self._clean_text(cols[7].css('::text').get()) or 'N/A'

                # The winners page doesn't provide State/District — only Constituency
                # These can be derived from the election context
                item['State'] = 'See Constituency'
                item['District'] = 'See Constituency'
                item['Year'] = year

                yield item

    @staticmethod
    def _clean_text(text):
        """Strip whitespace and return None for empty strings."""
        if text:
            return text.strip()
        return None
