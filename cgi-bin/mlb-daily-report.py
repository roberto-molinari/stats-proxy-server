#!/usr/bin/env python
import array
import datetime
import urllib2
import pandas as pd
import sys
import time

from bs4 import BeautifulSoup

# get today's date in the right format 'YYYYMMDD'
today = datetime.datetime.now()
today_date_string = today.strftime("%Y%m%d")

# print the header and start of the body tag for the HTML that we will return to the client
print("Contet-Type:text/html\r\n\r\n")
print("<html>")
print("<head><title>Results of your SDQL Query</title></head>")
print("<body>")

base_url = "https://sportsdatabase.com/mlb/query"
base_querystring = "?output=default&su=1&ou=1&submit=++S+D+Q+L+%21++&sdql="
full_url = base_url + base_querystring + "date=" + today_date_string
#print(full_url)
#print("<br>")

request = urllib2.Request(full_url, headers={'User-Agent' : ' Magic Browser'})
page = urllib2.urlopen(request)
soup = BeautifulSoup(page, "lxml")


# due to some odd issue with the find() function not working on my ubuntu server, i have to use find_all
# and then terate over the one instance
data_tables = soup.find_all("table", id="DT_Table", limit=1)

try:
	for data_table in data_tables:

		new_table = pd.read_html(data_table.prettify())[0]
		# the table has the following headers that are interesting:
		# - Starter (in the format "<Full Name> - <Throwing Arm>"
		# - Total

		# we take the starter and the total and see how that has performed over the season
		for index, row in new_table.iterrows():
			
			starter = row['Starter']
			starter = starter[0:-4]
			total = row['Total']
			if total != total:
				print("===" + starter + " no total set yet.  skipping.")
				print("<br><br>")
 			else:
				starter_total_query_string = "starter=" + starter.replace(" ", "%20") + "+and+total=" + str(total)

				full_url = base_url + base_querystring + "season=2019+and+" + starter_total_query_string
				#print(full_url)
				#print("<br>")
				time.sleep(2)
				request2 = urllib2.Request(full_url, headers={'User-Agent' : 'Mozilla/5.0'})
				page2 = urllib2.urlopen(request2)
				soup2 = BeautifulSoup(page2, "lxml")
				pitcher_html_table = soup2.find_all("table", id="DT_Table", limit=1)[0]
				pitcher_table = pd.read_html(pitcher_html_table.prettify())[0]
				print("<br>")
				print("====" + starter + " at line " + str(total))
				print("<br>")
				print(pitcher_table.to_html())
				#print(pitcher_table[0].to_html())
				print("<br>")

except Exception as e:
	print("exception occured: " + str(e))
print("</body>")
print("</html>")


