#!/usr/bin/env python
import array
import datetime
import urllib2
import pandas as pd
import sys
import time
import traceback

from bs4 import BeautifulSoup

class PitcherData:
	def __init__(self, game_log_table, pitcher_name, over_line, over_percentage):
		self.game_log_table = game_log_table
		self.pitcher_name = pitcher_name
		self.over_line = over_line
		self.over_percentage = over_percentage
	
	def print_html(self):
		total_opportunities = len( self.game_log_table )
		if total_opportunities == 0:
			print("===" + self.pitcher_name + " has never pitched with an over line of " + str( self.over_line ))
		else:
			print("===" + self.pitcher_name + " has hit the over " + str(self.over_percentage) + "% at line " + str( self.over_line ) )
		print("<br>")

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

request = urllib2.Request(full_url, headers={'User-Agent' : ' Magic Browser'})
page = urllib2.urlopen(request)
soup = BeautifulSoup(page, "lxml")


# due to some odd issue with the find() function not working on my ubuntu server, i have to use find_all
# and then terate over the one instance
data_tables = soup.find_all("table", id="DT_Table", limit=1)

pitcher_list = []

try:
	for data_table in data_tables:

		new_table = pd.read_html(data_table.prettify())[0]
		# the table has the following headers that are interesting:
		# - Starter (in the format "<Full Name> - <Throwing Arm>"
		# - Total

		# we take the starter and the total and see how that has performed over the season
		for index, row in new_table.iterrows():
			
			starter_name = row['Starter']
			starter_name = starter_name[0:-4]
			over_total = row['Total']
			if over_total != over_total:
				xxx=5
				#print("===" + starter_name + " no total set yet.  skipping.")
				#print("<br><br>")
 			else:
				starter_total_query_string = "starter=" + starter_name.replace(" ", "%20") + "+and+total=" + str(over_total)

				full_url = base_url + base_querystring + "season=2019+and+" + starter_total_query_string
				
				time.sleep(2)
				request2 = urllib2.Request(full_url, headers={'User-Agent' : 'Mozilla/5.0'})
				page2 = urllib2.urlopen(request2)
				soup2 = BeautifulSoup(page2, "lxml")
				pitcher_html_table = soup2.find_all("table", id="DT_Table", limit=1)[0]
				pitcher_table = pd.read_html(pitcher_html_table.prettify())[0]
				
				pitcher_table.drop(columns = ['Link', 'Day', 'Site', 'Team', 'SUm', 'Hits', 'Errors', 'BL', 'Innings'], inplace=True)
				pitcher_table.drop( pitcher_table.tail(1).index, inplace=True )

				total_rows = len( pitcher_table )
				if total_rows >=1:
					over_count = len( pitcher_table[ pitcher_table["O/U"].str.contains('O')] )
					over_percentage = (float( over_count ) / float( total_rows ) ) * 100.0  
				else:
					over_percentage = 0.0
			
				pitcher_data = PitcherData( pitcher_table, starter_name, over_total, over_percentage )
				pitcher_list.append( pitcher_data )

				#print("<br>")
				#print("====" + starter + " at line " + str(total) + " hit the over " + percentage_over_message )
				#print("<br>")
				#print(pitcher_table.to_html())
				#print(pitcher_table[0].to_html())
				#print("<br>")

except Exception as e:
	print("exception occured: " + str(e))
	print(traceback.format_exc() )

i=0
for pitcher_data in pitcher_list:
	pitcher_data.print_html()
	if (i % 2) != 0:
		print("<br><br>")
	i = i + 1


print("</body>")
print("</html>")

sys.stdout.flush()
sys.stdout.close()

sys.stderr.flush()
sys.stderr.close()

