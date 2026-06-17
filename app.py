from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.image_routes import image_bp
from routes.audio_routes import audio_bp

app = Flask(__name__)

# CORS Configuration
CORS(
    app,
    resources={
        r"/*": {
            "origins": ["http://localhost:3000"]
        }
    },
    supports_credentials=True
)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(image_bp, url_prefix="/image")
app.register_blueprint(audio_bp, url_prefix="/audio")

print("✅ Auth blueprint registered")
print("✅ Image blueprint registered")

# Print all registered routes
print(app.url_map)

@app.route("/")
def home():
    return {
        "message": "HideCrypt Backend Running",
        "status": "✅ Connected to MongoDB Atlas"
    }

if __name__ == "__main__":
    app.run(
        debug=False,
        host="127.0.0.1",
        port=5000
    )