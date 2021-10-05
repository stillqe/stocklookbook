from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from finvizfinance.screener.custom import Custom

import pandas as pd

db = SQLAlchemy()


def init_app():
    app = Flask(__name__)
    app.config.from_object('config.DevConfig')
    db.init_app(app)

    with app.app_context():
        from stocklookbookapp import routes

        print("db create all")
        db.create_all()  # Create sql tables for our data models
        print("load db")
        load_db()
        return app


# to do: load data from yfinance and return dataframe
def load_db():
    print("loading db")

    load_model(signal='Most Active')
    # stocks = set()
    # stocks.update(load_table('most_active', signal='Most Active'))
    # stocks.update(load_table('mega_stocks', filters={"Market Cap.": "Mega ($200bln and more)"}))
    # stocks.update(load_table('top_dividend', filters={"Dividend Yield": "High (>5%)"}))
    # stocks.update(load_table('top_gainers', signal='Top Gainers'))
    # stocks.update(load_table('top_losers', signal='Top Losers'))
    # stocks.update(load_table('most_volatile', signal='Most Volatile'))
    # stocks.update(load_table('top_news', signal='Major News'))

    # load_stocks(stocks)


def load_model(signal='', filters=None):
    if filters is None:
        filters = {}
    from stocklookbookapp.model.stockdb import Tag, Stock

    customcols = [0, 1, 2, 3, 6, 7, 42, 43, 46, 65, 66, 67]
    fcustom = Custom()
    fcustom.set_filter(signal=signal, filters_dict=filters)
    overview = fcustom.ScreenerView(order='Performance (Month)', ascend=False, columns=customcols)

    try:
        tags = Tag.query.filter_by(name=signal).first()
        #to do : delete existing stocks
        #tags.stocks.remove_all()
    except:
        tags = Tag(name=signal)

    for ticker, info in overview.set_index('Ticker').T.to_dict().items():
        stock = Stock(ticker=ticker,
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
        tags.stocks.append(stock)
    db.session.add(tags)
    db.session.commit()


def load_table(table_name, signal='', filters=None):
    if filters is None:
        filters = {}
    customcols = [0, 1, 2, 3, 6, 7, 42, 43, 46, 65, 66, 67]
    col_dict = {"Ticker": "ticker", "Company": "company", "Sector": "sector",
                "Market Cap": "cap", "P/E": "pe", "Perf Week": "perf_w", "Perf Month": "perf_m",
                "Perf Year": "perf_y", "Price": "price", "Change": "change", "Volume": "volume"}

    fcustom = Custom()
    fcustom.set_filter(signal=signal, filters_dict=filters)
    overview = fcustom.ScreenerView(order='Performance (Month)', ascend=False, columns=customcols).rename(
        columns=col_dict)
    overview['type'] = table_name

    overview.to_sql(table_name, con=db.engine, index=True, index_label='id', if_exists="replace")

    return set(overview.ticker)
