import http.client
import json
import time
from pymongo import MongoClient

symbols = ["btcusd","ltcusd","ltcbtc","drkusd","drkbtc"]

def fetch_order_book(pair_name):

    try:
        conn = http.client.HTTPSConnection("api.bitfinex.com")
        conn.request("GET", "/v1/book/" + pair_name)
        response = conn.getresponse()
        book = json.loads(response.readall().decode('utf-8'))
        conn.close()
        output = {'pair': pair_name,
                  'time': time.time(),
                  'book': book}
        return output
    except:
        print("ERROR - CANNOT FETCH ORDER BOOK")

#END order_book_api

client    = MongoClient()
db        = client['btcdb']
quotes    = db.allQuotes
lastQuote = db.lastQuote


while(1):
    time.sleep(5)
    for s in symbols:
        book = (fetch_order_book(s))
        quotes.insert(book)
        lastQuote.remove({"pair": s})
        lastQuote.insert(book)
#END while(1)
