# -*- coding: utf-8 -*-
import scrapy
import re
from netaproj.items import NetaprojItem


class NetabotSpider(scrapy.Spider):
    name = 'netabot'
    allowed_domains = ['myneta.info']
    start_urls = ['http://myneta.info/']

    def parse(self, response):
        """Extract state links from the State Assemblies section on the homepage."""
        # Find all state assembly links: state_assembly.php?state=STATE_NAME
        state_links = response.css(
            'a[href*="state_assembly.php?state="]'
        )
        for link in state_links:
            state_name = link.css('::text').get()
            state_url = link.attrib['href']
            request = scrapy.Request(
                response.urljoin(state_url),
                callback=self.parse_state
            )
            request.meta['State'] = state_name.strip() if state_name else ''
            yield request

    def parse_state(self, response):
        """Parse a state page to get all election years and their 'All Candidates' links."""
        # Each election year is in <div class='w3-panel w3-leftbar w3-pale-yellow'><h4>STATE YEAR</h4></div>
        # followed by <ul class="w3-ul"> with links
        election_headers = response.css(
            'div.w3-panel.w3-leftbar.w3-pale-yellow h4::text'
        ).getall()

        election_uls = response.css(
            'div.w3-panel.w3-leftbar.w3-pale-yellow + ul.w3-ul'
        )

        for header, ul_elem in zip(election_headers, election_uls):
            # Extract the year from the header text (e.g., "Delhi 2025" -> "2025")
            year_match = re.search(r'(\d{4})', header)
            if not year_match:
                continue
            year = year_match.group(1)

            # Find "All Candidates" link
            all_cand_link = ul_elem.css(
                'a:contains("All Candidates")::attr(href)'
            ).get()
            if not all_cand_link:
                continue

            request = scrapy.Request(
                response.urljoin(all_cand_link),
                callback=self.parse_election
            )
            request.meta['State'] = response.meta['State']
            request.meta['Year'] = int(year)
            yield request

    def parse_election(self, response):
        """Parse the election page listing constituencies by district dropdowns."""
        # Each district has a dropdown with constituency links
        # Constituency links: href=index.php?action=show_candidates&constituency_id=XX
        # The district name is on the button text
        dropdowns = response.css('div.w3-dropdown-click')

        for dropdown in dropdowns:
            # Get district name from the button text
            button_text = dropdown.css('button::text').get()
            if not button_text:
                continue
            district_name = button_text.strip()

            # Get constituency links
            const_links = dropdown.css(
                'div.w3-dropdown-content a[href*="show_candidates"]'
            )
            for const_link in const_links:
                const_name = const_link.css('::text').get()
                const_url = const_link.attrib['href']

                request = scrapy.Request(
                    response.urljoin(const_url),
                    callback=self.parse_constituency
                )
                request.meta['State'] = response.meta['State']
                request.meta['Year'] = response.meta['Year']
                request.meta['District'] = district_name.strip()
                request.meta['Constituency'] = const_name.strip() if const_name else ''
                yield request

    def parse_constituency(self, response):
        """Parse the candidate listing table for a constituency."""
        # New table structure: <table class='w3-table w3-bordered'>
        # Header row: SNo | Candidate | Party | Criminal Cases | Education | Age | Total Assets | Liabilities
        rows = response.css('table.w3-table.w3-bordered tr')

        for row in rows:
            cols = row.css('td')
            if len(cols) < 8:
                continue  # skip header row or empty rows

            item = NetaprojItem()

            # Candidate name and winner status
            candidate_cell = cols[1]
            item['Candidate'] = self._clean_text(
                candidate_cell.css('a::text').get()
            )
            # Check if winner (green font with "Winner")
            winner_text = candidate_cell.css('font[color="green"]::text').get()
            item['Winner'] = 'Yes' if winner_text and 'Winner' in winner_text else 'No'

            item['Party'] = self._clean_text(cols[2].css('::text').get())
            item['Criminal_Case'] = self._clean_text(cols[3].css('::text').get())
            item['Education'] = self._clean_text(cols[4].css('::text').get())
            item['Age'] = self._clean_text(cols[5].css('::text').get())
            item['Total_Assets'] = self._clean_text(cols[6].css('::text').get()) or 'N/A'
            item['Liabilities'] = self._clean_text(cols[7].css('::text').get()) or 'N/A'

            item['State'] = response.meta['State']
            item['Year'] = response.meta['Year']
            item['District'] = response.meta['District']
            item['Constituency'] = response.meta['Constituency']

            yield item

    @staticmethod
    def _clean_text(text):
        """Strip whitespace and return None for empty strings."""
        if text:
            return text.strip()
        return None
