FROM python:3

WORKDIR /c/Users/bertm/stats-proxy-server

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m", "http.server", "--cgi", "8000" ]
