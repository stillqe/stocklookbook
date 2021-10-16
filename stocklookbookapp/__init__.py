from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app():
    app = Flask(__name__)
    app.config.from_object('config.ProdConfig')
    db.init_app(app)
    db.app = app

    with app.app_context():
        from stocklookbookapp import routes
        from stocklookbookapp.model import init
        from apscheduler.schedulers.background import BackgroundScheduler
        print("db create all")
        db.create_all()  # Create sql tables for our data models
        print("load db")
        init.load_db(db)

        # sched = BackgroundScheduler(daemon=True)
        # sched.add_job(init.load_db, trigger='interval', args=[db], minutes=60)
        # sched.start()

        return app




