from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app():
    app = Flask(__name__)
    app.config.from_object('config.DevConfig')
    db.init_app(app)
    db.app = app

    with app.app_context():
        from stocklookbookapp import routes
        from stocklookbookapp.model import dbmanager
        from apscheduler.schedulers.background import BackgroundScheduler
        print("db create all")
        db.create_all()  # Create sql tables for our data models
        print("load db")
        dbmanager.load_db(db)

        # sched = BackgroundScheduler(daemon=True)
        # sched.add_job(dbmanager.update_stock, trigger='interval', args=[db], minutes=10)
        # sched.add_job(dbmanager.update_history, trigger='interval', args=[db], hours=24)
        # sched.start()

        return app