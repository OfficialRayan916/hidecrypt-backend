from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.image_routes import image_bp
from routes.audio_routes import audio_bp
from routes.video_routes import video_bp
from routes.dashboard_routes import dashboard_bp
from routes.history_routes import history_bp
from routes.admin_routes import admin_bp
from routes.admin_history_routes import admin_history_bp
from routes.profile_routes import profile_bp

app = Flask(__name__)

# CORS Configuration
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "https://hidecrypt-git-main-rayan-ahmed-s-projects1.vercel.app/"
            ]
        }
    },
    supports_credentials=True,
)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(image_bp, url_prefix="/image")
app.register_blueprint(audio_bp, url_prefix="/audio")
app.register_blueprint(video_bp, url_prefix="/video")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
app.register_blueprint(history_bp, url_prefix="/history")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(admin_history_bp, url_prefix="/admin")
app.register_blueprint(profile_bp, url_prefix="/profile")

print("✅ Auth blueprint registered")
print("✅ Image blueprint registered")

# Print all registered routes
print(app.url_map)


@app.route("/")
def home():
    return {
        "message": "HideCrypt Backend Running",
        "status": "✅ Connected to MongoDB Atlas",
    }


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
