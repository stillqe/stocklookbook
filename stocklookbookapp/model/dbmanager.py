from finvizfinance.screener.custom import Custom
from stocklookbookapp.model.stockdb import Collection, Stock, History
import numpy as np
import time

def load_db(db):
    print("loading db")
    start = time.perf_counter()
    load_collection(db, 'most-active', signal='Most Active')
    # load_collection(db, 'mega-stocks', signal='', filters={"Market Cap.": "Mega ($200bln and more)"})
    # load_collection(db, 'top-dividend', filters={"Dividend Yield": "Over 10%"})
    # load_collection(db, 'top-gainers', signal='Top Gainers')
    # load_collection(db, 'top-losers', signal='Top Losers')
    # load_collection(db, 'most-volatile', signal='Most Volatile')
    # load_collection(db, 'top-news', signal='Major News')
    elapsed = time.perf_counter() - start
    print(f"loading collection completed in {elapsed:0.2f} seconds.")
    load_stock(db, 'SPY')

    start = time.perf_counter()
    stockhistory = History(Stock.query.all())
    elapsed = time.perf_counter() - start
    print(f"History downloading completed in {elapsed:0.2f} seconds.")
    # start = time.perf_counter()
    # stockhistory.calculate_stats()
    # elapsed = time.perf_counter() - start
    # print(f"Stat calculation completed in {elapsed:0.2f} seconds.")
    # start = time.perf_counter()
    # stockhistory.visualize()
    # elapsed = time.perf_counter() - start
    # print(f"Visualization completed in {elapsed:0.2f} seconds.")


def load_collection(db, name, signal='', filters=None):
    if filters is None:
        filters = {}

    customcols = [0, 1, 2, 3, 6, 7, 42, 43, 46, 65, 66, 67]
    fcustom = Custom()
    fcustom.set_filter(signal=signal, filters_dict=filters)
    overview = fcustom.ScreenerView(order='Performance (Month)', ascend=False, columns=customcols)

    collecction = Collection.query.filter_by(name=name).first()
    if collecction:
        collecction.stocks.clear()
    else:
        collecction = Collection(name=name)

    for ticker, info in overview.set_index('Ticker').T.to_dict().items():
        existing_stock = Stock.query.filter_by(ticker=ticker).first()
        if existing_stock:
            Stock.query.filter_by(ticker=ticker).update(dict(pe=info['P/E'],
                                       perf_w=info['Perf Week'],
                                       perf_m=info['Perf Month'],
                                       perf_y=info['Perf Year'],
                                       price=info['Price'],
                                       change=info['Change'],
                                       volume=info['Volume']))
            collecction.stocks.append(existing_stock)
        else:
            new_stock = Stock(ticker=ticker,
                              company=info['Company'],
                              sector=info['Sector'],
                              #cap=info['Market Cap'],
                              pe=info['P/E'],
                              perf_w=info['Perf Week'],
                              perf_m=info['Perf Month'],
                              perf_y=info['Perf Year'],
                              price=info['Price'],
                              change=info['Change'],
                              volume=info['Volume']
                              )
            collecction.stocks.append(new_stock)

    db.session.add(collecction)
    db.session.commit()

def load_stock(db, tickers):

    customcols = [0, 1, 2, 3, 6, 7, 42, 43, 46, 65, 66, 67]
    fcustom = Custom()
    fcustom.set_filter(ticker=tickers)
    overview = fcustom.ScreenerView(order='Performance (Month)', ascend=False, columns=customcols)

    for ticker, info in overview.set_index('Ticker').T.to_dict().items():
        existing_stock = Stock.query.filter_by(ticker=ticker).first()
        if existing_stock:
            Stock.query.filter_by(ticker=ticker).update(dict(pe=info['P/E'],
                                       cap=info['Market Cap'],
                                       perf_w=info['Perf Week'],
                                       perf_m=info['Perf Month'],
                                       perf_y=info['Perf Year'],
                                       price=info['Price'],
                                       change=info['Change'],
                                       volume=info['Volume']))
        else:
            new_stock = Stock(ticker=ticker,
                              company=info['Company'],
                              sector=info['Sector'],
                              cap=info['Market Cap'],
                              pe=info['P/E'],
                              perf_w=info['Perf Week'],
                              perf_m=info['Perf Month'],
                              perf_y=info['Perf Year'],
                              price=info['Price'],
                              change=info['Change'],
                              volume=info['Volume']
                              )
            db.session.add(new_stock)
    db.session.commit()

def update_stock(db):

    load_collection(db, 'most-active', signal='Most Active')
    # load_collection(db, 'mega-stocks', signal='', filters={"Market Cap.": "Mega ($200bln and more)"})
    # load_collection(db, 'top-dividend', filters={"Dividend Yield": "Over 10%"})
    # load_collection(db, 'top-gainers', signal='Top Gainers')
    # load_collection(db, 'top-losers', signal='Top Losers')
    # load_collection(db, 'most-volatile', signal='Most Volatile')
    # load_collection(db, 'top-news', signal='Major News')

def update_history(db):
    #'date', 'ticker',  'close', 'high', 'low', 'returns', 'volume
    # time.time()
    # for stock in Stock.query.all():
    #     hs = History.query.filter(History.ticker == stock.ticker, History.date == stock.date).first()
    #     hs.close = stock.price
    #     hs.returns = np.log(stock.change)


    pass
