"""Data models."""
from stocklookbookapp import db
import datetime
import dateutil
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.path as mpath
import matplotlib.patches as mpatches

plt.style.use('dark_background')
plt.switch_backend('Agg')

import math
import yfinance as yf


class PriceHistory(db.Model):
    """Data model for price history."""

    __tablename__ = 'price_history'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(8), index=False, unique=False, nullable=False)
    date = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    price = db.Column(db.Float, index=False, unique=False, nullable=True)
    returns = db.Column(db.Float, index=False, unique=False, nullable=True)
    #stock_id = db.Column(db.Integer. db.ForeignKey('stocks.id'))


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
    # date = db.Column(db.DateTime, index=False, unique=False, nullable=False)
    company = db.Column(db.String, index=False, unique=False, nullable=True)
    sector = db.Column(db.String(20), index=False, unique=False, nullable=True)
    cap = db.Column(db.Integer, index=False, unique=False, nullable=True)
    pe = db.Column(db.Float, index=False, unique=False, nullable=True)
    perf_w = db.Column(db.Float, index=False, unique=False, nullable=True)
    perf_m = db.Column(db.Float, index=False, unique=False, nullable=True)
    perf_y = db.Column(db.Float, index=False, unique=False, nullable=True)

    price = db.Column(db.Float, index=False, unique=False, nullable=True)
    change = db.Column(db.Float, index=False, unique=False, nullable=True)
    volume = db.Column(db.Integer, index=False, unique=False, nullable=True)

    #histories = db.relationship("PriceHistory")



class StockContainer:
    """ Stocks class for calculating stock stats and
    visualizing a stock based on the stats.

    Attributes:
        tickers (list of str) a list of strings extracted from the tickers
        data (dataframe) representing the historical stock data
        info (nested dictionary) representing each stock's information
        stats (nested dictionary) representing each stock's stats

    """

    def __init__(self, stocks, benchmark="SPY"):

        self.tickers = [stock.ticker for stock in stocks]

        self.stats = {}
        for ticker in self.tickers:
            self.stats[ticker] = {}
        self.m_stats = {}

        self.load_stocks(self.tickers, benchmark, '3y')
        self.calculate_stats()
        stocks = Stock.query.all()
        self.visualize(stocks, period='1m')
        self.visualize(stocks, period='3m')
        self.visualize(stocks, period='1y')
        self.visualize(stocks, period='2y')
        #self.visualize(Stock.query.all(), '3y')


    def __repr__(self):
        """function to represent the instance of the stocks"""
        return str([stock + ": " + str(info['1y']['performance']) for stock, info in self.stats.items()])

    def calculate_stats(self):
        """calcuate performance of each stock on given period and store it to dataframe"""
        for period in ['1m', '3m', '1y','2y','3y']:
            start = self._get_startdate(period)
            m_close = self.market[start:]['Adj Close']
            m_returns = np.log(m_close / m_close.shift(1))
            self.m_stats[period] = {'performance': m_close.iloc[-1] / m_close.iloc[0], "volatility": m_returns.std()}

            close = self.data[start:]['Adj Close']
            low = self.data[start:]['Low']
            high = self.data[start:]['High']

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

    def load_stocks(self, tickers, benchmark, period='1y'):

        print('downloading benchmark')
        self.market = yf.download(tickers=benchmark, period=period)
        print('downloading stock data')
        self.data = yf.download(tickers=tickers, period=period)

    def visualize(self, stocks, pallete='spring', period='1y'):

        m_perf = self.m_stats[period]["performance"]
        m_vola = self.m_stats[period]["volatility"]

        for stock in stocks:
            fig, ax = plt.subplots(figsize=(1, 2))
            ax.patch.set_facecolor('black')
            stat = self.stats[stock.ticker]

            self.pillarplot(ax, stat[period]["performance"] / m_perf,
                            stat[period]["volatility1"] / m_vola,
                            stat[period]["volatility2"] / m_vola,
                            stat[period]["low"], stat[period]["high"], stat[period]["current"],
                            self._get_color(stock.pe, pallete)
                            )

            fig.savefig("stocklookbookapp/static/stocks/" + stock.ticker + "_" + period + ".svg", bbox_inches='tight',
                        pad_inches=0.0, format="svg")
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
        pos = (current - low) / (high - low) * width
        ax.scatter(pos, 0, color='w', s=10, zorder=2)

        ax.axis('off')
        ax.set_xlim([-0.25, 1.25])
        ax.set_ylim([-0.1, 3.5])
        ax.set_aspect('equal', 'box')

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
    def _get_color(PE, pallete):
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

