import pandas as pd
import matplotlib.pyplot as plt


def view_book(symbol, client):
    # call order book JSON read
    order_snap = client.get_order_book(symbol=symbol, limit=100)

    # Parse JSON structure
    bid_prices, bid_vol = [], []
    ask_prices, ask_vol = [], []
    for k in range(0, 100):
        bid_prices.append(float(order_snap['bids'][k][0]))
        bid_vol.append(float(order_snap['bids'][k][1]))
        ask_prices.append(float(order_snap['asks'][k][0]))
        ask_vol.append(float(order_snap['asks'][k][1]))

    # format ladder
    bid_vol = ([0.0 for i in range(0, 100)] + bid_vol)
    price = ask_prices[::-1] + bid_prices
    ask_vol = (ask_vol + [0.0 for i in range(0, 100)])
    # create & return pandas DF object
    frame = pd.DataFrame(data=list(zip(bid_vol, price, ask_vol)), columns=['bid_vol', 'quote', 'ask_vol'], index=range(0, 200))

    return frame, order_snap['lastUpdateId']


def plot_book(book, ticker, limit=500, save=True, path='', plot=True):

    book, timestamp = book[0], book[1]
    best_ask, best_bid = book.iloc[int(limit/2)-1], book.iloc[int(limit/2)]
    midpoint = ((best_bid['bid_vol']*best_ask['quote'] + best_ask['ask_vol']*best_bid['quote'])/(best_ask['ask_vol']+best_bid['bid_vol']))
    ref_move = [round(((quote-midpoint)/midpoint)*100, 3) for quote in book['quote']]

    if plot:
        plt.bar(book['quote'], book['ask_vol'], color='red', label='Ask')
        plt.bar(book['quote'], book['bid_vol'], color='green', label='Bid')
        plt.axvline(midpoint, color='black', linewidth=1, linestyle='--', label='Mid')
        plt.ylabel('Volume (# BTC in LOB)')
        plt.xlabel('Quote ($)')
        plt.title('Top of LOB in {}'.format(ticker))
        plt.legend()
        plt.show()
        if save:
            plt.savefig('{}book{}.jpg'.format(path, ticker), dpi=800)

    return book


def swipe_cost(book, size, pair='NA', side='BUY', ref='A'):

    asks = book['ask_vol'][0:int(len(book)/2)]
    bids = book['bid_vol'][int(len(book)/2):len(book)]
    best_ask, best_bid = book.iloc[int(len(book)/2)-1], book.iloc[int(len(book)/2)]
    midpoint = ((best_bid['bid_vol']*best_ask['quote'] + best_ask['ask_vol']*best_bid['quote'])
                /(best_ask['ask_vol']+best_bid['bid_vol']))

    fill = 0

    if side == 'BUY':
        for i in range(len(asks)-1, 0, -1):
            fill = fill + book['ask_vol'][i]
            if fill >= size:
                price = (book['quote'][i+1])
                break

    elif side == 'SELL':
        for i in range(len(asks), len(book)):
            fill = fill + book['bid_vol'][i]

            if fill >= size:
                price = (book['quote'][i-1])
                break

    if ref == 'A':
        ref_price = best_ask['quote']
    elif ref == 'B':
        ref_price = best_bid['quote']
    elif ref == 'M':
        ref_price = midpoint
    else:
        ref_price = best_ask['quote']

    change = (abs((price-ref_price)/ref_price).round(6))
    rows = ['Pair', 'Size', 'Ref. Price', 'Expected Price', 'Cost (%)']
    datums = [pair, size, ref_price, price, change*100]
    fr = pd.DataFrame()
    fr['Index'] = rows
    fr['Data'] = datums

    return fr


def monitor_book(symbol, client, limit):
    spread, mid_point, timestamp = [], [], []
    ask_mean, bid_mean = [], []
    book_balance, bba = [], []
    run, count = True, 0
    # Data fetching loop
    while run is True:
        # retrieve book
        book = view_book(symbol, client)
        frame = book[0]
        # retrieve timestamp
        timestamp.append(book[1])
        # Book analysis
        best_ask, best_bid = frame.iloc[101], frame.iloc[100]
        # Spread
        spread.append(best_bid['quote'] - best_ask['quote'])
        # Mid-point
        mid_point.append((best_bid['bid_vol']*best_ask['quote'] + best_ask['ask_vol']*best_bid['quote'])/(best_ask['ask_vol']+best_bid['bid_vol']))
        # Book Balance
        book_balance.append(sum(frame['bid_vol']*frame['quote'])/sum(frame['ask_vol']*frame['quote']))
        # Weighted Mean by Side
        bid_mean.append(sum(frame.quote * frame.bid_vol)/sum(frame.bid_vol))
        ask_mean.append(sum(frame.quote * frame.ask_vol)/sum(frame.ask_vol))
        bba.append(best_bid)

        count = count + 1

        if count > limit:
            run = False

    df = pd.DataFrame(data=list(zip(timestamp, mid_point, spread, book_balance, bid_mean, ask_mean, bba)), columns=['timestamp', 'mid_point', 'spread', 'book_balance', 'bid_mean', 'ask_mean', 'best_bid'], index=range(0,limit+1))

    return df
