from flask import Flask
from RoutesForModel.VideoModelRoutes import VideoModel_bp
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
# Registering BluePrints
app.register_blueprint(VideoModel_bp)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)