from flask import render_template, request
from src.service.service import Service

from datetime import datetime


def controller(app):
    service = Service()

    @app.route('/')
    def index():
        today = datetime.now().strftime("%Y-%m-%d")
        order, orderCount = [],0

        return render_template('index.html', order=[], orderCount=orderCount,)

