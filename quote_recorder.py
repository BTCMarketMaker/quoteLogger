import http.client
import json
import time
from datetime import datetime
from pymongo import MongoClient

symbols = ["btcusd","ltcusd","ltcbtc","drkusd","drkbtc"]

def fetch_order_book(pair_name):

    try:
        conn = http.client.HTTPSConnection("api.bitfinex.com")
        conn.request("GET", "/v1/book/" + pair_name)
        response = conn.getresponse()
        book = json.loads(response.readall().decode('utf-8'))
        conn.close()

        best_bid   = float(book['bids'][0]['price'])
        best_ask   = float(book['asks'][0]['price'])
        spread     = best_ask - best_bid
        mid        = 0.5 * (best_ask + best_bid)
        limit_high = mid + 10 * spread
        limit_low  = mid - 10 * spread

        down_idx = 0
        for k in book['bids']:
            if float(k['price']) < limit_low:
                break
            down_idx += 1
        #END for k

        up_idx = 0
        for k in book['asks']:
            if float(k['price']) > limit_high:
                break
            up_idx += 1

        book['bids'] = book['bids'][0:down_idx]
        book['asks'] = book['asks'][0:up_idx]

        output = {'pair':  pair_name,
                  'time':  time.time(),
                  'valid': True,
                  'book':  book}
        return output
    except:
        print("ERROR - CANNOT FETCH ORDER BOOK")
        output = {'pair':  pair_name,
                  'time':  time.time(),
                  'valid': False}
        return output

#END order_book_api


def record():

    client    = MongoClient()
    db        = client['btcdb']
    quotes    = db.allQuotes
    lastQuote = db.lastQuote

    try:
        while(1):
            time.sleep(5)
            print(datetime.now())
            for s in symbols:
                book = (fetch_order_book(s))
                quotes.insert(book)
                lastQuote.remove({"pair": s})
                lastQuote.insert(book)
        #END while(1)
    #END try
    except:
        print("ERROR - QUOTE RECORDING WHILE LOOP")
    #END except
#END record

record()