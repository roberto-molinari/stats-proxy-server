#!/usr/bin/env python
import cgi, cgitb
import array
import urllib2
import pandas
import sys

from bs4 import BeautifulSoup

# -- begin code for handling as part of CGI execution
cgitb.enable()

form = cgi.FieldStorage()

print("Contet-Type:text/html\r\n\r\n")
print("<html>")
print("<head><title>Hello world</title></head>")
print("<body>Hello world!!!</body>")


query_string = form.getvalue('querytype')
query_string = "query"
query_conditions = []
query_conditions_string = ""
query_conditions.append( form.getvalue('query1') )
query_conditions_string += form.getvalue('query1').replace(" ", "%20")
query_conditions_string += "%20and%20"

query_conditions.append( form.getvalue('query2') )
query_conditions_string += form.getvalue('query2').replace(" ", "%20")
query_conditions_string += "%20and%20"

query_conditions.append( form.getvalue('query3') )
query_conditions_string += form.getvalue('query3').replace(" ", "%20")


data_columns = []
data_columns_string = ""

data_columns.append( form.getvalue('data1') )
data_columns_string += form.getvalue('data1').replace(" ", "%20")
data_columns_string += "%2C"

data_columns.append( form.getvalue('data2') )
data_columns_string += form.getvalue('data2').replace(" ", "%20")
data_columns_string += "%2C"

data_columns.append( form.getvalue('data3') )
data_columns_string += form.getvalue('data3').replace(" ", "%20")



base_url = "https://sportsdatabase.com/mlb/"
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
    full_url = base_url + query_string + base_querystring + data_columns_string + "%40" + query_conditions_string
else:
    full_url = base_url + query_string + base_querystring + query_conditions_string + data_columns_string

print(full_url)

# request = urllib2.Request("https://sportsdatabase.com/mlb/batter_query?output=default&su=1&ou=1&sdql=hits%2C+home+runs%2C+date%40name+%3D+Mookie+Betts+and+season%3D2019&submit=++S+D+Q+L+%21++", headers={'User-Agent' : ' Magic Browser'})
request = urllib2.Request(full_url, headers={'User-Agent' : ' Magic Browser'})
#request = urllib2.Request("https://www.google.com", headers={'User-Agent' : ' Magic Browser'} )
page = urllib2.urlopen(request)
#print("<br>")
#print("---start page oontent---")
#print("<br><br>")
#print(page.read())
#print("---end page content---")
#print("<br><br>")
#print("---http status code: ")
#print(page.info())
#print("<br><br>")

soup = BeautifulSoup(page, "lxml")

#print("---start beautifulsoup---")
#print("<br><br>")
#print(soup.body)
#print("<br><br>")
#print("---end beautiful soup---")
#print("<br><br>")

# due to some odd issue with the find() function not working on my ubuntu server, i have to use find_all
# and then terate over the one instance
data_tables = soup.find_all("table", id="DT_Table", limit=1)
#print(data_tables)

try:
	for data_table in data_tables:
		print("---Found a table!---")
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

	print("<br><br>---Raw Data---<br>")
	print(new_table.to_html())

	print("<br><br>---Grouped Data---<br>")
	print(new_table.groupby('team').describe().to_html())

except Exception as e:
	print("exception occured: " + str(e))
print("</html")

