from flask import Flask

app = Flask(__name__)

from stocklookbookapp import routes
