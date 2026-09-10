from flask_cors import CORS

def init_cors(app):
    CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for CORS
    return app