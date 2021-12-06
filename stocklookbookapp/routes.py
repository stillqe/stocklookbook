from flask import current_app as app
from flask import render_template, request, session

from apscheduler.schedulers.background import BackgroundScheduler

from stocklookbookapp.model.stockdb import Stock, Collection


@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
def index():
    choice = 'mega-stocks'
    stocks = Collection.query.filter_by(name=choice).first().stocks
    print("the total number of stocks: {}".format(len(stocks)))
    return render_template('display.html', collection=choice, stocks=stocks, period='1y')


@app.route('/<choice>')
def trendingstocks(choice):
    if choice == 'all':
        stocks = Stock.query.all()
        print(len(stocks))
    else:
        stocks = Collection.query.filter_by(name=choice).first().stocks
    if stocks is None:
        return print("No stock found")
    return render_template('display.html', collection=choice, stocks=stocks)


@app.route('/collection', methods=['GET', 'POST'])
def collections():
    choice = request.form['choice']
    period = request.form['period']

    stocks = Collection.query.filter_by(name=choice).first().stocks

    if stocks is None:
        return print("No stock found")

    return render_template('display.html', collection=choice, period=period, stocks=stocks)
