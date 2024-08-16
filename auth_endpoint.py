from flask import Flask, request, jsonify, redirect
from instagram_processor import InstagramProcesser
import basic_display_api
from models import User
from utils import init_db, SessionLocal
import ssl
import os

app = Flask(__name__)

# Load environment variables
INSTAGRAM_CLIENT_ID = os.getenv("INSTAGRAM_CLIENT_ID")
INSTAGRAM_AUTH_CALLBACK_URI = os.getenv("INSTAGRAM_AUTH_CALLBACK_URI")


@app.route("/")
def home():
    """Redirect to Instagram's auth window."""
    instagram_auth_window = basic_display_api.auth_window(
        INSTAGRAM_CLIENT_ID, INSTAGRAM_AUTH_CALLBACK_URI
    )
    return redirect(instagram_auth_window)


@app.route("/callback")
def callback():
    authorization_code = request.args.get("code")

    if authorization_code:
        # Get user object
        user = None

        instagram_processor = InstagramProcesser(user, authorization_code)
        result = instagram_processor.run()
        return result
    else:
        return jsonify({"error": "No authorization code provided"}), 400


@app.route("/deauth", methods=["POST"])
def deauth():
    # Handle user deauthorization
    return jsonify({"message": "User deauthorization handled successfully"})


@app.route("/delete", methods=["POST"])
def delete():
    # Handle user data deletion request
    return jsonify({"message": "User data deletion request handled successfully"})


if __name__ == "__main__":
    engine = init_db()
    SessionLocal.configure(bind=engine)

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain("ssl.crt", "ssl.key")

    app.run(host="0.0.0.0", debug=True, port=5000, ssl_context=context)
