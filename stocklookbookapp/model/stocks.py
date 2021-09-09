import datetime
import dateutil
import yfinance as yf

def get_startdate(period):
    month_dic = {'1m':1, '3m':3, '6m':6, '1y':12, '2y':24, '3y':36, '5y':60}
    delta = dateutil.relativedelta.relativedelta(months=month_dic[period])
    start = datetime.date.today() - delta
    return start

import io
import base64

class FlowLayout(object):
    ''' A class / object to display plots in a horizontal / flow layout below a cell '''
    def __init__(self):
        # string buffer for the HTML: initially some CSS; images to be appended
        self.sHtml =  """
        <style>
        .floating-box {
        display: inline-block;
        text-align: center;
        margin: 4px;
        border: 1px solid #888888;
        }
        </style>
        """

    def add_plot(self, oAxes, ticker):
        ''' Saves a PNG representation of a Matplotlib Axes object '''
        Bio=io.BytesIO() # bytes buffer for the plot
        fig = oAxes.get_figure()
        fig.canvas.print_png(Bio) # make a png of the plot in the buffer

        # encode the bytes as string using base 64
        sB64Img = base64.b64encode(Bio.getvalue()).decode()
        self.sHtml+= (
            '<div class="floating-box">'+
            '<img src="data:image/png;base64,{}\n">'.format(sB64Img)+
            ticker+
            '</div>')

    def PassHtmlToCell(self):
        ''' Final step - display the accumulated HTML '''
        display(HTML(self.sHtml))


class Stocks:
    """ Stocks class for calculating stock stats and
    visualizing a stock based on the stats.

    Attributes:
        tickers (list of str) a list of strings extracted from the tickers
        data (dataframe) representing the historical stock data
        info (nested dictionary) representing each stock's information
        stats (nested dictionary) representing each stock's stats

    """

    def __init__(self, tickers, benchmark):
        self.tickers=tickers.split(" ")
        self.stats={}
        for ticker in self.tickers:
            self.stats[ticker]={}
        self.m_stats = {}
        periods = ['1m', '3m', '1y','2y','5y']

        self.load_stocks(tickers, benchmark, periods[-1])
        self.calculate_stats(periods)
     #   self.load_info()




    def __repr__(self):
        """function to represent the instance of the stocks"""
        return str([stock +": " + str(info['1y']['performance']) for stock, info in self.stats.items()])

    def calculate_stats(self, periods):
        """calcuate performance of each stock on given period and store it to dataframe"""
        for period in periods:
            start = get_startdate(period)
            m_close = self.market[start:]['Adj Close']
            m_returns = np.log(m_close/m_close.shift(1))
            self.m_stats[period] = {'performance': m_close.iloc[-1]/m_close.iloc[0], "volatility":m_returns.std()}

            close = self.data[start:]['Adj Close']
            low = self.data[start:]['Low']
            high = self.data[start:]['High']

            for ticker in self.tickers:
                #to do : exception process when ticker doesn't exist or only one ticker case

                s_close = close[ticker].dropna()
                s_low = low[ticker].dropna()
                s_high = high[ticker].dropna()
                if (len(s_close)>0):
                    change = s_close.iloc[-1]/s_close.iloc[0]
                    returns = np.log(s_close/s_close.shift(1))
                    half = int(len(returns)/2)
                    vola1 = returns.iloc[:half].std()
                    vola2 = returns.iloc[half:].std()
                    self.stats[ticker][period] = {'performance':change,
                                          'volatility1':vola1, 'volatility2':vola2,
                                         "low":s_low.min(),"high":s_high.max(), "current":s_close.iloc[-1]}




    def load_stocks(self, tickers, benchmark, period='5y'):

        self.market = yf.download(tickers=benchmark, period=period)
        self.data = yf.download(tickers=tickers, period=period)

    def visualize(self, period='1y'):
        oPlot = FlowLayout() # create an empty FlowLayout
        m_perf = self.m_stats[period]["performance"]
        m_vola = self.m_stats[period]["volatility"]
        for ticker, stats in self.stats.items():


            #height =  math.ceil(stats["performance"]/self.m_stats[period]["performance"])
            fig, ax = plt.subplots(figsize=(1,3))
            self.pillarplot(ax, stats[period]["performance"]/m_perf,
                            stats[period]["volatility1"]/m_vola,
                            stats[period]["volatility2"]/m_vola,
                            stats[period]["low"], stats[period]["high"], stats[period]["current"])
            #ax.set_title(ticker)
            #ticks = np.arange(1, height+1)
            #xs = np.full(height, fill_value = 0.5)
            #plt.scatter(xs, ticks, c='r', s=1.8)
            fig.savefig("stocklookbookapp/static/stocks/"+ticker+"_"+period+".svg", format="svg")
            oPlot.add_plot(ax, ticker) # pass it to the FlowLayout to save as an image
            plt.close() # this gets rid of the plot so it doesn't appear in the cell


        oPlot.PassHtmlToCell()


    def pillarplot(self, ax, performance, vola1, vola2, low, high, current, width=1, height=1):

        dw, dx1, dy1, dx2, dy2 = self.get_cpoints(vola1, vola2)

        bottom_left = np.array([0,0])
        bottom_right = np.array([width,0])
        top_left = bottom_left + [0, height*performance]
        top_right = bottom_right + [0, height*performance]


        c1_left = (bottom_left*3/4 + top_left/4) + [width*dx1,0] -[0, dy1]
        c1_right = (bottom_right*3/4 + top_right/4) - [width*dx1,0] -[0, dy1]

        waist_left = (bottom_left + top_left)/2 + [width*dw,0]
        waist_right = (bottom_right + top_right)/2 - [width*dw,0]


        c2_left = (bottom_left/4 + top_left*3/4) + [width*dx2, 0] + [0,dy2]
        c2_right = (bottom_right/4 + top_right*3/4) - [width*dx2, 0] + [0,dy2]



        Path = mpath.Path

        codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3, Path.CURVE3,Path.CURVE3, Path.LINETO, Path.CURVE3,Path.CURVE3,Path.CURVE3,Path.CURVE3, Path.CLOSEPOLY]
        vertices = [bottom_left, c1_left, waist_left, c2_left, top_left, top_right, c2_right, waist_right, c1_right, bottom_right, bottom_left]

        pp = mpatches.PathPatch(Path(vertices, codes), facecolor='g', edgecolor='g', alpha=0.5)

        ax.add_patch(pp)
        pos = (current-low)/(high-low)*width
        ax.scatter(pos,0, facecolors='w', edgecolors='g', s=10)

        ax.axis('off')
        ax.set_xlim([-0.25,1.25])
        ax.set_ylim([-0.1,4.4])
        ax.set_aspect('equal', 'box')

        return

    @staticmethod
    def get_cpoints(vola1, vola2):
        """calcaulate the points of quadratic bezier curve based on the volatility of stock"""

        rv1 = (vola1-1)/10
        rv2 = (vola2-1)/10
        LIMIT = 4.8/10


        dx1 = min(rv1, LIMIT)
        dx2 = min(rv2, LIMIT)

        dy = lambda x: 0 if (x < LIMIT) else min(1/(4/LIMIT)*(x-LIMIT), 1/4)
        dy1 = dy(rv1)
        dy2 = dy(rv2)

        w = (dx1+dx2)/2

        return w, dx1, dy1, dx2, dy2





    #def add_stocks(tickers):
