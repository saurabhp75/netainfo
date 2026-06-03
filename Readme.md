Scrapy spider which collects Assembly and Lok Sabha Elections data from http://www.myneta.info.

 ### Data fields scraped

 Candidate, Winner, Party, Criminal_Case, Education, Age (N/A — not on winners page), Total_Assets,
 Liabilities, State, Year, District, Constituency (includes bye-election annotation like NANDED : BYE
 ELECTION ON 20-11-2024)

 ### Run commands

 ```bash
   # Create a virtual environment and install Scrapy
   python3 -m venv venv
   source venv/bin/activate
   pip install scrapy   cd netainfo
   source ../venv/bin/activate

   # Lok Sabha winners (all years, including bye-elections)
   scrapy crawl lsbot -o ls_winners.csv

   # Assembly elections (all states, all years)
   scrapy crawl netabot -o assembly.csv
 ```
