import array
import urllib2
import pandas
import sys

from bs4 import BeautifulSoup

base_url = "https://sportsdatabase.com/mlb/"
base_querystring = "?output=default&su=1&ou=1&submit=++S+D+Q+L+%21++&sdql="

# usage: stats-proxy-server.py --querytype <batter|pitcher|game> --query 'key1=value1' 'key2=value2' --stats stat1 stat2 ... statn 
if(len(sys.argv) < 5 or sys.argv[1] != "--querytype" or not(sys.argv[2] == "batter" or sys.argv[2] == "pitcher" or sys.argv[2] == "game")):
    print "usage: stats-proxy-server.py --querytype <batter|pitcher|game> --queryparams 'key1=value1' 'key2=value2' --stats stat1 stat2 ... statn"
    quit()

# the URL on sports data uses 'query' (for game queries), 'batter_query' (for hitter queries) or 'pitcher_query' (for pitcher queries) as the last 
# element in the path before the query string.  Form that last element here, depending on what kind of query the user wants to do.
query_type = sys.argv[2]
if query_type != "game":
    query_string = query_type + "_query"
else:
    query_string = "query"

query_conditions = []
query_conditions_string = ""
i = 4
while i < len(sys.argv) and sys.argv[i] != "--stats":
    query_conditions.append( sys.argv[i])
    query_conditions_string += sys.argv[i].replace(" ", "%20")
    i += 1
    if i < len(sys.argv) and sys.argv[i] != "--stats":
        query_conditions_string += "%20and%20"


data_columns = []
data_columns_string = ""
if sys.argv[i] == "--stats":
    i += 1
    while i < len(sys.argv):
        data_columns.append(sys.argv[i])
        data_columns_string += sys.argv[i].replace(" ", "%20")
        i += 1
        if i < len(sys.argv):
            data_columns_string += "%2C"

    
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

print full_url

# request = urllib2.Request("https://sportsdatabase.com/mlb/batter_query?output=default&su=1&ou=1&sdql=hits%2C+home+runs%2C+date%40name+%3D+Mookie+Betts+and+season%3D2019&submit=++S+D+Q+L+%21++", headers={'User-Agent' : ' Magic Browser'})
request = urllib2.Request(full_url, headers={'User-Agent' : ' Magic Browser'})
page = urllib2.urlopen(request)
soup = BeautifulSoup(page, "lxml")

data_table = soup.find('table', {'id':'DT_Table'})


foo = data_table.find_all('tr');

a = array.array('i',(i for i in range(0,len(foo))))
new_table = pandas.DataFrame(columns=data_columns, index=a)

row_marker = 0
for row in data_table.find_all('tr'):
    if row_marker > 0: # skip the first row as it has non-data in it
        column_marker = 0
        columns = row.find_all('td')

        for column in columns:
            new_table.iat[row_marker,column_marker] = column.get_text().strip()
            column_marker += 1
    row_marker += 1

print "\n\n---Grouped Data---"
print new_table.groupby('team').sort_values(by=['count']).describe()

print "\n\n---Raw Data---"
print new_table