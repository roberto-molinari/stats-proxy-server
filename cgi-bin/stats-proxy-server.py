#!/usr/bin/env python
import cgi, cgitb
import array
import urllib2
import os
import pandas
import sys

sys.path.append(os.path.realpath('lib'))

from htmlhelpers import start_html_document, end_html_document

from bs4 import BeautifulSoup

# define some constants
MAX_QUERY_PARAMS=10
MAX_DATA_FIELDS=10

# -- begin code for handling as part of CGI execution
cgitb.enable()

form = cgi.FieldStorage()

# print the header and start of the body tag for the HTML that we will return to the client
start_html_document()

# get the name of the league that we're going to query (mlb, nfl, nhl, etc.)
league_string = form.getvalue('league-select')

# get the type of query that we're going to do (game or player)
query_type = form.getvalue('query-type-select')
if query_type != "game":
   query_type_string = query_type + "_query"
else:
   query_type_string = "query"

# iterate over the query params and get them into the correct format for passing to the server
query_conditions = []
query_conditions_string = ""
i = 1
while i < MAX_QUERY_PARAMS:
	query_key_string = "query"+str(i)
	i+=1
	if form.getvalue( query_key_string ):
		query_conditions.append( form.getvalue( query_key_string ) )
		query_conditions_string += form.getvalue( query_key_string ).replace(" ", "%20")
		if i < MAX_QUERY_PARAMS:
			next_query_key_string = "query"+str(i)
			if form.getvalue( next_query_key_string ): 
				query_conditions_string += "%20and%20"
	

# iterate over the data columns the user has requested and get them into the correct format for passing to the server
data_columns = []
data_columns_string = ""
i = 1
while i < MAX_DATA_FIELDS:
	data_key_string = "data"+str(i)
	i+=1
	if form.getvalue( data_key_string ):
		data_columns.append( form.getvalue( data_key_string ) )
		data_columns_string += form.getvalue( data_key_string ).replace(" ", "%20")
		if i < MAX_DATA_FIELDS:
			next_data_key_string = "data"+str(i)
			if form.getvalue( next_data_key_string ):
				data_columns_string += "%2C"
	

# get the hostname, patn ahd start of the query string set.  the format of the request URL is:
#
#     https://sportsdatabase.com/<league-name>/
base_url = "https://sportsdatabase.com/" + league_string + "/"
base_querystring = "?output=default&su=1&ou=1&submit=++S+D+Q+L+%21++&sdql="

# -- begin code for executing from command line
# usage: stats-proxy-server.py --querytype <batter|pitcher|game> --query 'key1=value1' 'key2=value2' --stats stat1 stat2 ... statn 
##if(len(sys.argv) < 5 or sys.argv[1] != "--querytype" or not(sys.argv[2] == "batter" or sys.argv[2] == "pitcher" or sys.argv[2] == "game")):
##    print "usage: stats-proxy-server.py --querytype <batter|pitcher|game> --queryparams 'key1=value1' 'key2=value2' --stats stat1 stat2 ... statn"
##    quit()

# the URL on sports data uses 'query' (for game queries), 'batter_query' (for hitter queries) or 'pitcher_query' (for pitcher queries) as the last 
# element in the path before the query string.  Form that last element here, depending on what kind of query the user wants to do.
##query_type = sys.argv[2]
##if query_type != "game":
##   query_string = query_type + "_query"
##else:
##    query_string = "query"

##query_conditions = []
##query_conditions_string = ""
##i = 4
##while i < len(sys.argv) and sys.argv[i] != "--stats":
##    query_conditions.append( sys.argv[i])
##    query_conditions_string += sys.argv[i].replace(" ", "%20")
##    i += 1
##    if i < len(sys.argv) and sys.argv[i] != "--stats":
##        query_conditions_string += "%20and%20"


##data_columns = []
##data_columns_string = ""
##if sys.argv[i] == "--stats":
##    i += 1
##    while i < len(sys.argv):
##        data_columns.append(sys.argv[i])
##        data_columns_string += sys.argv[i].replace(" ", "%20")
##        i += 1
##        if i < len(sys.argv):
##            data_columns_string += "%2C"

    
# the format of the URL will be:
# https://sportsdatabase/mlb/<query_type>_query?output=default&su=1&ou=1&sdql=<stat1>%2C...<statn>%40<qyeryparam1>%2C...<queryparamN>
#
# where
#   - query_type = comes from the --querytype param
#   - stat1 ... statN = comes from the --stats param
#   - queryparam1 ... queryparamN = comes from the --query param
return_data = ['hits', 'home runs', 'date']

if data_columns_string != "":
    full_url = base_url + query_type_string + base_querystring + data_columns_string + "%40" + query_conditions_string
else:
    full_url = base_url + query_type_string + base_querystring + query_conditions_string + data_columns_string

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
		new_table = pandas.DataFrame(columns=data_columns, index=a)

		row_marker = 0
		for row in data_table.find_all("tr"):
			if row_marker > 0: # skip the first row as it has non-data in it
      				column_marker = 0
        			columns = row.find_all("td")

        			for column in columns:
            				new_table.iat[row_marker,column_marker] = column.get_text().strip()
            				column_marker += 1
    			row_marker += 1

	print("<br><br>---Grouped Data---<br>")
	print(new_table.groupby('team').count().sort_values(by=['goals'], ascending=False).to_html())

	print("<br><br>---Raw Data---<br>")
	print(new_table.to_html())


	# print(new_table.groupby('team').sort_values('count').describe().to_html())
	# print(new_table.groupby('team').describe().to_html())


except Exception as e:
	print("exception occured: " + str(e))

end_html_document()
