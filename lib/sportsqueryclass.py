import sys

# define some constants
MAX_QUERY_PARAMS=10
MAX_DATA_FIELDS=10


class SportsQuery:
    def __init__(self, form):
        self.form = form
        # get the name of the league that we're going to query (mlb, nfl, nhl, etc.)
        self.league = form.getvalue('league-select')

        self.initializeQueryType()

        self.initializeQueryParameters()

        self.initializeDataColumns()
        
        self.initializeSortColumn()

        self.initializeGroupColumn()

    def initializeQueryType(self):
        # get the type of query that we're going to do (game or player)
        query_type_value = self.form.getvalue('query-type-select')
        if query_type_value != "game":
            self.query_type = query_type_value + "_query"
        else:
            self.query_type = "query"


    def initializeQueryParameters(self):
        # iterate over the query params and get them into the correct format for passing to the server
        self.query_parameters = ""
        i = 1
        while i < MAX_QUERY_PARAMS:
            query_key_string = "query"+str(i)
            i+=1
            if self.form.getvalue( query_key_string ):
                self.query_parameters += self.form.getvalue( query_key_string ).replace(" ", "%20")
                if i < MAX_QUERY_PARAMS:
                    next_query_key_string = "query"+str(i)
                    if self.form.getvalue( next_query_key_string ):
                        self.query_parameters += "%20and%20"


    def initializeDataColumns(self):   
        # iterate over the data columns the user has requested and get them into the correct format for passing to the server
        self.data_columns_list = []
        self.data_columns = ""
        i = 1
        while i < MAX_DATA_FIELDS:
            data_key_string = "data"+str(i)
            i+=1
            if self.form.getvalue( data_key_string ):
                self.data_columns_list.append( self.form.getvalue(data_key_string) )
                self.data_columns += self.form.getvalue( data_key_string ).replace(" ", "%20")
                if i < MAX_DATA_FIELDS:
                    next_data_key_string = "data"+str(i)
                    if self.form.getvalue( next_data_key_string ):
                        self.data_columns += "%2C"

    def initializeSortColumn(self):
        self.sort_column=self.data_columns_list[ int(self.form.getvalue("sort") ) ]

    def initializeGroupColumn(self):
        self.group_column=self.data_columns_list[ int(self.form.getvalue("group") ) ]
