#!/usr/bin/env python
import cgi, cgitb
import array
import urllib2
import os
import pandas
import sys

sys.path.append(os.path.realpath('lib'))

from htmlhelpers import start_html_document, end_html_document
from sportsqueryclass import SportsQuery
from bs4 import BeautifulSoup

# -- begin code for handling as part of CGI execution
cgitb.enable()

form = cgi.FieldStorage()

# print the header and start of the body tag for the HTML that we will return to the client
start_html_document()

# initialize the object that holds all the information about the query the user submitted.
incoming_query = SportsQuery(form)


# get the hostname, patn ahd start of the query string set.  the format of the request URL is:
#
#     https://sportsdatabase.com/<league-name>/
base_url = "https://sportsdatabase.com/" + incoming_query.league + "/"
base_querystring = "?output=default&su=1&ou=1&submit=++S+D+Q+L+%21++&sdql="

    
# the format of the URL will be:
# https://sportsdatabase/mlb/<query_type>_query?output=default&su=1&ou=1&sdql=<stat1>%2C...<statn>%40<qyeryparam1>%2C...<queryparamN>
#
# where
#   - query_type = comes from the --querytype param
#   - stat1 ... statN = comes from the --stats param
#   - queryparam1 ... queryparamN = comes from the --query param
return_data = ['hits', 'home runs', 'date']

if incoming_query.data_columns != "":
    full_url = base_url + incoming_query.query_type + base_querystring + incoming_query.data_columns + "%40" + incoming_query.query_parameters
else:
    full_url = base_url + incoming_query.query_type + base_querystring + incoming_query.query_parameters

print(full_url)

# request = urllib2.Request("https://sportsdatabase.com/mlb/batter_query?output=default&su=1&ou=1&sdql=hits%2C+home+runs%2C+date%40name+%3D+Mookie+Betts+and+season%3D2019&submit=++S+D+Q+L+%21++", headers={'User-Agent' : ' Magic Browser'})
request = urllib2.Request(full_url, headers={'User-Agent' : ' Magic Browser'})
page = urllib2.urlopen(request)
soup = BeautifulSoup(page, "lxml")


# due to some odd issue with the find() function not working on my ubuntu server, i have to use find_all
# and then terate over the one instance
data_tables = soup.find_all("table", id="DT_Table", limit=1)

try:
	for data_table in data_tables:
		foo = data_table.find_all("tr");

		a = array.array('i',(i for i in range(0,len(foo))))
		new_table = pandas.DataFrame(columns=incoming_query.data_columns_list, index=a)

		row_marker = 0
		for row in data_table.find_all("tr"):
			if row_marker > 0: # skip the first row as it has non-data in it
      				column_marker = 0
        			columns = row.find_all("td")

        			for column in columns:
            				new_table.iat[row_marker,column_marker] = column.get_text().strip()
            				column_marker += 1
    			row_marker += 1

	if incoming_query.results_type == "aggregated":
		print("<br><br>---Grouped Data---<br>")
		print(new_table.groupby(incoming_query.group_column).count().sort_values(by=[incoming_query.sort_column], ascending=False).to_html())
	
	if incoming_query.results_type == "raw":
		print("<br><br>---Raw Data---<br>")
		print(new_table.sort_values(by=[incoming_query.sort_column], ascending=False).to_html())


	# print(new_table.groupby('team').sort_values('count').describe().to_html())
	# print(new_table.groupby('team').describe().to_html())


except Exception as e:
	print("exception occured: " + str(e))

end_html_document()
