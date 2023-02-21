from flask import Flask
from src.controller.controller import controller
from flask_debugtoolbar import DebugToolbarExtension


application = app = Flask(__name__)

controller(app)

toolbar = DebugToolbarExtension()
app.config['SECRET_KEY'] = 'SECRET_KEY_XXXXXX_XXXXX'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False  # 不拦截重定向
toolbar.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)
