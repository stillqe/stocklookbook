"""Data models."""
from stocklookbookapp import db
import datetime
import dateutil
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import tempfile
from io import BytesIO
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import ContentSettings

import asyncio
import pandas as pd

MY_CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=stocklookbook;AccountKey=1R3UxnJ9muVgudoZcOfQjdouwCyAozOlQXNrqQBaLj5qg70ZjBxEv975olev8bPdh8qJfwnvWW9NDiHvrJSzqw==;EndpointSuffix=core.windows.net'

# Replace with blob container. This should be already created in azure storage.
MY_IMAGE_CONTAINER = "stocks"

plt.style.use('dark_background')
plt.switch_backend('Agg')

import math
import yfinance as yf

PERIODS = ['1m', '3m', '1y', '2y']

stock_identifier = db.Table('stock_identifier',
                            db.Column('collection_id', db.Integer, db.ForeignKey('collections.id')),
                            db.Column('stock_id', db.Integer, db.ForeignKey('stocks.id'))
                            )


class Collection(db.Model):
    __tablename__ = 'collections'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    stocks = db.relationship("Stock", secondary=stock_identifier, lazy='subquery',
                             backref=db.backref('tags', lazy=True))


class Stock(db.Model):
    __tablename__ = 'stocks'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(8), index=False, unique=True, nullable=False)
    date = db.Column(db.Date, server_default=db.func.now(), index=False, unique=False,
                     nullable=False)
    updatedAt = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), index=False, unique=False,
                          nullable=False)
    company = db.Column(db.String(100), index=False, unique=False, nullable=True)
    sector = db.Column(db.String(60), index=False, unique=False, nullable=True)
    cap = db.Column(db.BigInteger, index=False, unique=False, nullable=True)
    pe = db.Column(db.Float, index=False, unique=False, nullable=True)
    perf_w = db.Column(db.Float, index=False, unique=False, nullable=True)
    perf_m = db.Column(db.Float, index=False, unique=False, nullable=True)
    perf_y = db.Column(db.Float, index=False, unique=False, nullable=True)

    price = db.Column(db.Float, index=False, unique=False, nullable=True)
    change = db.Column(db.Float, index=False, unique=False, nullable=True)
    volume = db.Column(db.Integer, index=False, unique=False, nullable=True)

    # histories = db.relationship("History")


class History(db.Model):
    """ Stocks class for calculating stock stats and
    visualizing a stock based on the stats.

    Attributes:
        tickers (list of str) a list of strings extracted from the tickers
        data (dataframe) representing the historical stock data
        info (nested dictionary) representing each stock's information
        stats (nested dictionary) representing each stock's stats

    """

    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(8), index=False, unique=False, nullable=False)
    date = db.Column(db.Date, index=False, unique=False, nullable=False)
    close = db.Column(db.Float, index=False, unique=False, nullable=True)
    volume = db.Column(db.Float, index=False, unique=False, nullable=True)
    returns = db.Column(db.Float, index=False, unique=False, nullable=True)
    high = db.Column(db.Float, index=False, unique=False, nullable=True)
    low = db.Column(db.Float, index=False, unique=False, nullable=True)

    high_1m = db.Column(db.Float, index=False, unique=False, nullable=True)
    low_1m = db.Column(db.Float, index=False, unique=False, nullable=True)
    perf_1m = db.Column(db.Float, index=False, unique=False, nullable=True)
    vola1_1m = db.Column(db.Float, index=False, unique=False, nullable=True)
    vola2_1m = db.Column(db.Float, index=False, unique=False, nullable=True)

    high_3m = db.Column(db.Float, index=False, unique=False, nullable=True)
    low_3m = db.Column(db.Float, index=False, unique=False, nullable=True)
    perf_3m = db.Column(db.Float, index=False, unique=False, nullable=True)
    vola1_3m = db.Column(db.Float, index=False, unique=False, nullable=True)
    vola2_3m = db.Column(db.Float, index=False, unique=False, nullable=True)

    high_1y = db.Column(db.Float, index=False, unique=False, nullable=True)
    low_1y = db.Column(db.Float, index=False, unique=False, nullable=True)
    perf_1y = db.Column(db.Float, index=False, unique=False, nullable=True)
    vola1_1y = db.Column(db.Float, index=False, unique=False, nullable=True)
    vola2_1y = db.Column(db.Float, index=False, unique=False, nullable=True)

    high_2y = db.Column(db.Float, index=False, unique=False, nullable=True)
    low_2y = db.Column(db.Float, index=False, unique=False, nullable=True)
    perf_2y = db.Column(db.Float, index=False, unique=False, nullable=True)
    vola1_2y = db.Column(db.Float, index=False, unique=False, nullable=True)
    vola2_2y = db.Column(db.Float, index=False, unique=False, nullable=True)

    def __init__(self, stocks, benchmark="SPY"):

        tickers = [stock.ticker for stock in stocks]
        self.tickers = set(tickers)

        # self.stats = {}
        # for ticker in self.tickers:
        #     self.stats[ticker] = {}
        # self.m_stats = {}
        print('history  init')

        self.load_history()

        # self.calculate_stats()
        # stocks = Stock.query.all()
        # for period in PERIODS:
        #     self.visualize(stocks, period=period)

    def load_history(self):
        existing_tickers = {ticker[0] for ticker in History.query.with_entities(History.ticker).distinct()}

        new_tickers = self.tickers.difference(existing_tickers)
        if new_tickers:
            start = self._get_startdate('2y')
            self.df_to_sql(new_tickers, start)

        recent = History.query.order_by(History.date.desc()).first()
        if recent:
            start = recent.date + datetime.timedelta(days=1)
            print(start)
        else:
            print("no stock history")  # expected to perform only on the first time run
            start = self._get_startdate('2y')

        # download additional history for already stored stocks
        if (datetime.date.today() > start):
            self.df_to_sql(existing_tickers, start)

    def df_to_sql(self, tickers, start):
        print("downloading new stock history")
        df = yf.download(tickers=list(tickers), start=start)
        if df.columns.nlevels > 1:  # multi index column
            # caculate returns that diff close price from previous date close price
            returns = np.log(df['Adj Close'] / df['Adj Close'].shift(1))
            returns.columns = pd.MultiIndex.from_product([['Returns'], returns.columns])
            concated = pd.concat([df, returns], axis=1)
            selected = concated.stack(level=[1]).reset_index()[
                ['Date', 'level_1', 'Adj Close', 'High', 'Low', 'Returns', 'Volume']]
            selected.rename(columns={'level_1': 'ticker', 'Adj Close': 'Close'}, inplace=True)
            selected.rename(str.lower, axis='columns', inplace=True)

        else:  # single index column
            df['Returns'] = np.log(df['Adj Close'] / df['Adj Close'].shift(1))
            selected = df.reset_index()[['Date', 'Adj Close', 'High', 'Low', 'Returns', 'Volume']]
            selected['ticker'] = tickers.pop()
            selected.rename(columns={'Adj Close': 'Close'}, inplace=True)
            selected.rename(str.lower, axis='columns', inplace=True)

        selected.to_sql("history", con=db.engine, index=False, if_exists="append")

    def calculate_stats(self):
        """calcuate performance of each stock on given period and store it to dataframe"""
        for ticker in self.tickers:
            low = {}
            high = {}
            vola1 = {}
            vola2 = {}
            perf = {}
            baseQuery = History.query.filter_by(ticker=ticker)
            latest = baseQuery.order_by(History.date.desc()).with_entities(History.date).first()[0]
            for period in PERIODS:
                start = self._get_startdate(period)
                halfway = self._get_meddate(period)
                startprice = baseQuery.filter(History.date > start) \
                    .order_by(History.date.asc()).with_entities(History.close).first()[0]
                endprice = baseQuery.filter(History.date == latest).with_entities(History.close).first()[0]

                low[period], high[period] = baseQuery.filter(History.date > start).with_entities(
                    db.func.min(History.low), db.func.max(History.high)).first()
                vola1[period] = baseQuery.filter(History.date > start, History.date <= halfway).with_entities(
                    db.func.stddev(History.returns)).first()[0]
                vola2[period] = baseQuery.filter(History.date > halfway).with_entities(
                    db.func.stddev(History.returns)).first()[0]
                perf[period] = endprice / startprice

            baseQuery.filter(History.date == latest).update({'low_1m': low['1m'],
                                                             'high_1m': high['1m'],
                                                             'vola1_1m': vola1['1m'],
                                                             'vola2_1m': vola2['1m'],
                                                             'perf_1m': perf['1m'],
                                                             'low_3m': low['3m'],
                                                             'high_3m': high['3m'],
                                                             'vola1_3m': vola1['3m'],
                                                             'vola2_3m': vola2['3m'],
                                                             'perf_3m': perf['3m'],
                                                             'low_1y': low['1y'],
                                                             'high_1y': high['1y'],
                                                             'vola1_1y': vola1['1y'],
                                                             'vola2_1y': vola2['1y'],
                                                             'perf_1y': perf['1y'],
                                                             'low_2y': low['2y'],
                                                             'high_2y': high['2y'],
                                                             'vola1_2y': vola1['2y'],
                                                             'vola2_2y': vola2['2y'],
                                                             'perf_2y': perf['2y']
                                                             })
        db.session.commit()

        # for period in PERIODS:
        #     start = self._get_startdate(period)
        #     m_close = self.market[start:]['Adj Close']
        #     m_returns = np.log(m_close / m_close.shift(1))
        #     self.m_stats[period] = {'performance': m_close.iloc[-1] / m_close.iloc[0], "volatility": m_returns.std()}
        #
        #     close = self.data[start:]['Adj Close']
        #     low = self.data[start:]['Low']
        #     high = self.data[start:]['High']
        #
        #     for ticker in self.tickers:
        #         # to do : exception process when ticker doesn't exist or only one ticker case
        #
        #         s_close = close[ticker].dropna()
        #         s_low = low[ticker].dropna()
        #         s_high = high[ticker].dropna()
        #         if (len(s_close) > 0):
        #             change = s_close.iloc[-1] / s_close.iloc[0]
        #             returns = np.log(s_close / s_close.shift(1))
        #             half = int(len(returns) / 2)
        #             vola1 = returns.iloc[:half].std()
        #             vola2 = returns.iloc[half:].std()
        #             self.stats[ticker][period] = {'performance': change,
        #                                           'volatility1': vola1, 'volatility2': vola2,
        #                                           "low": s_low.min(), "high": s_high.max(), "current": s_close.iloc[-1]}

    def visualize(self):

        baseQuery = History.query.filter_by(ticker='SPY')
        m_perf, m_vola1, m_vola2 = baseQuery.order_by(History.date.desc()).with_entities(
            History.perf_1y, History.vola1_1y, History.vola2_1y).first()

        m_vola = (m_vola1+m_vola2)/2

        blob_service_client = BlobServiceClient.from_connection_string(MY_CONNECTION_STRING)
        for ticker in self.tickers:

            baseQuery = History.query.filter_by(ticker=ticker)
            latest = baseQuery.order_by(History.date.desc()).with_entities(History.date).first()[0]

            price, perf, vola1, vola2, low, high = History.query.filter_by(ticker=ticker).order_by(History.date.desc())\
                .with_entities(History.close, History.perf_1y, History.vola1_1y, History.vola2_1y, History.low_1y, History.high_1y).first()

            pe, perf_y = Stock.query.filter(Stock.ticker == ticker).with_entities(Stock.pe, Stock.perf_y).first()
            if (perf < 0):
                perf = perf_y

            fig, ax = plt.subplots(figsize=(1.5,perf/m_perf+0.5))
            ax.patch.set_facecolor('black')
            if vola1 is None:
                if vola2 is None:
                    vola1 = m_vola
                    vola2 = m_vola
                else:
                    vola1 = vola2

            self.pillarplot(ax, perf / m_perf,
                            vola1 / m_vola,
                            vola2 / m_vola,
                            low, high, price,
                            self._get_color(pe)
                            )
            temp = tempfile.gettempdir()
            image_stream = BytesIO()
            file_name = ticker + "_" + "1y" + ".svg"
            fig.savefig(image_stream, bbox_inches='tight', pad_inches=0.0, format="svg")
            # reset stream's position to 0
            image_stream.seek(0)
            # upload in blob storage
            blob_client = blob_service_client.get_blob_client(container=MY_IMAGE_CONTAINER,
                                                              blob=file_name)
            image_content_setting = ContentSettings(content_type='image/svg+xml')
            blob_client.upload_blob(image_stream.read(), overwrite=True, content_settings=image_content_setting)

            plt.close()  # this gets rid of the plot so it doesn't appear in the cell

    def pillarplot(self, ax, performance, vola1, vola2, low, high, current, color, width=1, height=1):

        dw, dx1, dy1, dx2, dy2 = self._get_cpoints(vola1, vola2)

        bottom_left = np.array([0, 0])
        bottom_right = np.array([width, 0])
        top_left = bottom_left + [0, height * performance]
        top_right = bottom_right + [0, height * performance]

        c1_left = (bottom_left * 3 / 4 + top_left / 4) + [width * dx1, 0] - [0, dy1]
        c1_right = (bottom_right * 3 / 4 + top_right / 4) - [width * dx1, 0] - [0, dy1]

        waist_left = (bottom_left + top_left) / 2 + [width * dw, 0]
        waist_right = (bottom_right + top_right) / 2 - [width * dw, 0]

        c2_left = (bottom_left / 4 + top_left * 3 / 4) + [width * dx2, 0] + [0, dy2]
        c2_right = (bottom_right / 4 + top_right * 3 / 4) - [width * dx2, 0] + [0, dy2]

        Path = mpath.Path
        codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3, Path.CURVE3, Path.CURVE3, Path.LINETO, Path.CURVE3, Path.CURVE3,
                 Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]
        vertices = [bottom_left, c1_left, waist_left, c2_left, top_left, top_right, c2_right, waist_right, c1_right,
                    bottom_right, bottom_left]

        pp = mpatches.PathPatch(Path(vertices, codes), color=color, alpha=1)
        ax.add_patch(pp)
        ax.axis('off')
        ax.set_xlim([-0.25, 1.25])
        ax.set_ylim([-0.1, top_left[1]+0.4])
        # ax.set_ylim([-0.1, 3.5])
        ax.set_aspect('equal', 'box')

        if high == low:
            pos = 0
        else:
            pos = (current - low) / (high - low) * width
        ax.scatter(pos, 0, color='w', s=10, zorder=2)

        return

    @staticmethod
    def _get_cpoints(vola1, vola2):
        """calcaulate the points of quadratic bezier curve based on the volatility of stock"""

        rv1 = (vola1 - 1) / 10
        rv2 = (vola2 - 1) / 10
        LIMIT = 4.8 / 10

        dx1 = min(rv1, LIMIT)
        dx2 = min(rv2, LIMIT)

        dy = lambda x: 0 if (x < LIMIT) else min(1 / (4 / LIMIT) * (x - LIMIT), 1 / 4)
        dy1 = dy(rv1)
        dy2 = dy(rv2)

        w = (dx1 + dx2) / 2

        return w, dx1, dy1, dx2, dy2

    @staticmethod
    def _get_color(PE, pallete='spring'):
        """get a color to represent P/E ratio"""
        cm = plt.get_cmap(pallete)

        try:
            num = float(PE) / 100
            if np.isnan(num):
                color = (0.7, 0.7, 0.7)
            else:
                color = cm(num)
        except:
            color = (0.7, 0.7, 0.7)

        return color

    @staticmethod
    def _get_startdate(period):
        month_dic = {'1m': 1, '3m': 3, '6m': 6, '1y': 12, '2y': 24, '3y': 36, '5y': 60}

        delta = dateutil.relativedelta.relativedelta(months=month_dic[period])
        start = datetime.date.today() - delta
        return start

    @staticmethod
    def _get_meddate(period):
        day_dic = {'1m': 15, '3m': 46, '6m': 91, '1y': 182, '2y': 365, '3y': 548, '5y': 913}

        delta = dateutil.relativedelta.relativedelta(days=day_dic[period])
        med = datetime.date.today() - delta
        return med

class StockContainer():
    def __init__(self, stocks):
        tickers = [stock.ticker for stock in stocks]

        self.stats = {}
        self.m_stats = {}

        for stock in stocks:
            self.stats[stock.ticker] = {}
            self.stats[stock.ticker]['P/E'] = stock.pe


        self.tickers = set(tickers)
        self.tickers.add('SPY')


        self.load_history()




    def load_history(self):
        start = self._get_startdate('2y')
        # download additional history for already stored stocks
        self.data = yf.download(tickers=list(self.tickers), start=start)

    def calculate_stats(self):

        for period in PERIODS:
            start = self._get_startdate(period)

            close = self.data[start:]['Adj Close']
            low = self.data[start:]['Low']
            high = self.data[start:]['High']

            m_close = close['SPY'].dropna()
            m_returns = np.log(m_close / m_close.shift(1))
            self.m_stats[period] = {'performance': m_close.iloc[-1] / m_close.iloc[0], "volatility": m_returns.std()}

            for ticker in self.tickers:
                # to do : exception process when ticker doesn't exist or only one ticker case

                s_close = close[ticker].dropna()
                s_low = low[ticker].dropna()
                s_high = high[ticker].dropna()
                if (len(s_close) > 0):
                    change = s_close.iloc[-1] / s_close.iloc[0]
                    returns = np.log(s_close / s_close.shift(1))
                    half = int(len(returns) / 2)
                    vola1 = returns.iloc[:half].std()
                    vola2 = returns.iloc[half:].std()
                    self.stats[ticker][period] = {'performance': change,
                                                  'volatility1': vola1, 'volatility2': vola2,
                                                  "low": s_low.min(), "high": s_high.max(), "current": s_close.iloc[-1]}

    async def read_stats(self):
        for ticker, stat in self.stats.items():
            yield ticker, stat

    async def visualize(self):

        blob_service_client = BlobServiceClient.from_connection_string(MY_CONNECTION_STRING)

        async with blob_service_client:
            for period in PERIODS:
                tasks = []
                m_perf = self.m_stats[period]["performance"]
                m_vola = self.m_stats[period]["volatility"]
                async for ticker, stat in self.read_stats():
                    height = stat[period]["performance"]/m_perf + 0.5
                    if stat[period]["performance"] < 0:
                        print(ticker, stat[period]["performance"])
                        continue
                    fig, ax = plt.subplots(figsize=(1.5, height))
                    ax.patch.set_facecolor('black')
                    self.pillarplot(ax, stat[period]["performance"] / m_perf,
                                    stat[period]["volatility1"] / m_vola,
                                    stat[period]["volatility2"] / m_vola,
                                    stat[period]["low"], stat[period]["high"], stat[period]["current"],
                                    self._get_color(self.stats[ticker]["P/E"])
                                    )

                    image_stream = BytesIO()
                    file_name = ticker + "_" + period + ".svg"
                    fig.savefig(image_stream, bbox_inches='tight', pad_inches=0.0, format="svg")
                    # reset stream's position to 0
                    image_stream.seek(0)
                    # upload in blob storage
                    blob_client = blob_service_client.get_blob_client(container=MY_IMAGE_CONTAINER,
                                                                      blob=file_name)
                    image_content_setting = ContentSettings(content_type='image/svg+xml')
                    tasks.append(asyncio.create_task(
                        blob_client.upload_blob(image_stream.read(), overwrite=True, content_settings=image_content_setting)))
                    plt.close()  # this gets rid of the plot so it doesn't appear in the cell
                    await asyncio.gather(*tasks)


    def pillarplot(self, ax, performance, vola1, vola2, low, high, current, color, width=1, height=1):

        dw, dx1, dy1, dx2, dy2 = self._get_cpoints(vola1, vola2)

        bottom_left = np.array([0, 0])
        bottom_right = np.array([width, 0])
        top_left = bottom_left + [0, height * performance]
        top_right = bottom_right + [0, height * performance]

        c1_left = (bottom_left * 3 / 4 + top_left / 4) + [width * dx1, 0] - [0, dy1]
        c1_right = (bottom_right * 3 / 4 + top_right / 4) - [width * dx1, 0] - [0, dy1]

        waist_left = (bottom_left + top_left) / 2 + [width * dw, 0]
        waist_right = (bottom_right + top_right) / 2 - [width * dw, 0]

        c2_left = (bottom_left / 4 + top_left * 3 / 4) + [width * dx2, 0] + [0, dy2]
        c2_right = (bottom_right / 4 + top_right * 3 / 4) - [width * dx2, 0] + [0, dy2]

        Path = mpath.Path
        codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3, Path.CURVE3, Path.CURVE3, Path.LINETO, Path.CURVE3, Path.CURVE3,
                 Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]
        vertices = [bottom_left, c1_left, waist_left, c2_left, top_left, top_right, c2_right, waist_right, c1_right,
                    bottom_right, bottom_left]

        pp = mpatches.PathPatch(Path(vertices, codes), color=color, alpha=1)
        ax.add_patch(pp)
        ax.axis('off')
        ax.set_xlim([-0.25, 1.25])
        ax.set_ylim([-0.1, top_left[1]+0.4])
        # ax.set_ylim([-0.1, 3.5])
        ax.set_aspect('equal', 'box')

        if high == low:
            pos = 0
        else:
            pos = (current - low) / (high - low) * width
        ax.scatter(pos, 0, color='w', s=10, zorder=2)

        return

    @staticmethod
    def _get_cpoints(vola1, vola2):
        """calcaulate the points of quadratic bezier curve based on the volatility of stock"""

        rv1 = (vola1 - 1) / 10
        rv2 = (vola2 - 1) / 10
        LIMIT = 4.8 / 10

        dx1 = min(rv1, LIMIT)
        dx2 = min(rv2, LIMIT)

        dy = lambda x: 0 if (x < LIMIT) else min(1 / (4 / LIMIT) * (x - LIMIT), 1 / 4)
        dy1 = dy(rv1)
        dy2 = dy(rv2)

        w = (dx1 + dx2) / 2

        return w, dx1, dy1, dx2, dy2

    @staticmethod
    def _get_color(PE, pallete='spring'):
        """get a color to represent P/E ratio"""
        cm = plt.get_cmap(pallete)

        try:
            num = float(PE) / 100
            if np.isnan(num):
                color = (0.7, 0.7, 0.7)
            else:
                color = cm(num)
        except:
            color = (0.7, 0.7, 0.7)

        return color

    @staticmethod
    def _get_startdate(period):
        month_dic = {'1m': 1, '3m': 3, '6m': 6, '1y': 12, '2y': 24, '3y': 36, '5y': 60}

        delta = dateutil.relativedelta.relativedelta(months=month_dic[period])
        start = datetime.date.today() - delta
        return start

    @staticmethod
    def _get_meddate(period):
        day_dic = {'1m': 15, '3m': 46, '6m': 91, '1y': 182, '2y': 365, '3y': 548, '5y': 913}

        delta = dateutil.relativedelta.relativedelta(days=day_dic[period])
        med = datetime.date.today() - delta
        return med