import sys

def start_html_document():
	# print the header and start of the body tag for the HTML that we will return to the client
	print("Contet-Type:text/html\r\n\r\n")
	print("<html>")
	print("<head><title>Results of your SDQL Query</title></head>")
	print("<body>")


def end_html_document():
	print("</body>")
	print("</html>")

	sys.stdout.flush()
	sys.stdout.close()

	sys.stderr.flush()
	sys.stderr.close()

