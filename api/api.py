#ignore warnings
import warnings
warnings.filterwarnings("ignore")

import time
import atexit
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

# get_data
from scrapers.zupper import get_flights as zupper_get_data

#background jobs
from scrapers.decolar import main as decolar_web_scraper
from scrapers.edestinos import main as edestino_web_scraper
from scrapers.passagenspromo import main as passagenspromo_web_scraper
from scrapers.zupper import main as zupper_web_scraper

scheduler = BackgroundScheduler()
# scheduler.add_job(func=decolar_web_scraper, trigger="interval", seconds=15)
# scheduler.add_job(func=edestino_web_scraper, trigger="interval", seconds=15)
# scheduler.add_job(func=passagenspromo_web_scraper, trigger="interval", seconds=15)
scheduler.add_job(func=zupper_web_scraper, trigger="interval", seconds=1)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

app = Flask(__name__) 
@app.route('/')   
def home():
    data = zupper_get_data()
    return jsonify(data)

if __name__ =='__main__':
    app.run(debug = True)
