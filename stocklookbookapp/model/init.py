from finvizfinance.screener.custom import Custom
from stocklookbookapp.model.stockdb import Collection, Stock, StockContainer

def load_db(db):
    print("loading db")

    #load_model(db, 'most-active', signal='Most Active')
    load_model(db, 'mega-stocks', signal='', filters={"Market Cap.": "Mega ($200bln and more)"})
    #load_model(db, 'top-dividend', filters={"Dividend Yield": "Over 10%"})
    load_model(db, 'top-gainers', signal='Top Gainers')
    load_model(db, 'top-losers', signal='Top Losers')
    #load_model(db, 'most-volatile', signal='Most Volatile')
    #load_model(db, 'top-news', signal='Major News')


    sc = StockContainer(Stock.query.all())

def load_model(db, name, signal='', filters=None):
    if filters is None:
        filters = {}

    customcols = [0, 1, 2, 3, 6, 7, 42, 43, 46, 65, 66, 67]
    fcustom = Custom()
    fcustom.set_filter(signal=signal, filters_dict=filters)
    overview = fcustom.ScreenerView(order='Performance (Month)', ascend=False, columns=customcols)

    print(signal)

    existing_collecction = Collection.query.filter_by(name=name).first()
    if existing_collecction:
        existing_collecction.stocks.clear()
    else:
        existing_collecction = Collection(name=name)

    for ticker, info in overview.set_index('Ticker').T.to_dict().items():
        existing_stock = Stock.query.filter_by(ticker=ticker).first()
        if existing_stock:
            existing_collecction.stocks.append(existing_stock)
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
            existing_collecction.stocks.append(new_stock)

    db.session.add(existing_collecction)
    db.session.commit()





