from server import app
from config import Config

if __name__ == '__main__':
    app.run(host=Config.FLASK_CONFIG.HOST, port=Config.FLASK_CONFIG.PORT, debug=Config.FLASK_CONFIG.DEBUG)
