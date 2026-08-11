from flask import (
    Blueprint,
    redirect,
    request,
    session,
    current_app,
    jsonify
)

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from database import db
from models import User


# =========================================================
# AUTH BLUEPRINT
# =========================================================

auth_bp = Blueprint(
    "auth",
    __name__
)


# =========================================================
# GOOGLE PERMISSIONS
# =========================================================

SCOPES = [
    "openid",

    "https://www.googleapis.com/auth/userinfo.email",

    "https://www.googleapis.com/auth/userinfo.profile",

    "https://www.googleapis.com/auth/gmail.modify",

    "https://www.googleapis.com/auth/calendar",

    "https://www.googleapis.com/auth/drive",

    "https://www.googleapis.com/auth/spreadsheets"
]


# =========================================================
# CREATE GOOGLE OAUTH FLOW
# =========================================================

def create_google_flow(
    code_verifier=None
):

    client_config = {
        "web": {

            "client_id": (
                current_app.config[
                    "GOOGLE_CLIENT_ID"
                ]
            ),

            "client_secret": (
                current_app.config[
                    "GOOGLE_CLIENT_SECRET"
                ]
            ),

            "auth_uri": (
                "https://accounts.google.com/"
                "o/oauth2/auth"
            ),

            "token_uri": (
                "https://oauth2.googleapis.com/token"
            ),

            "redirect_uris": [
                current_app.config[
                    "GOOGLE_REDIRECT_URI"
                ]
            ]
        }
    }


    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        code_verifier=code_verifier
    )


    flow.redirect_uri = (
        current_app.config[
            "GOOGLE_REDIRECT_URI"
        ]
    )


    return flow


# =========================================================
# GOOGLE LOGIN
# =========================================================

@auth_bp.route(
    "/auth/google",
    methods=["GET"]
)
def google_login():

    client_id = current_app.config.get(
        "GOOGLE_CLIENT_ID"
    )

    client_secret = current_app.config.get(
        "GOOGLE_CLIENT_SECRET"
    )


    if not client_id or not client_secret:

        return jsonify({
            "error": (
                "Google OAuth is not configured"
            )
        }), 500


    # -----------------------------------------------------
    # CREATE FLOW
    # -----------------------------------------------------

    flow = create_google_flow()


    # -----------------------------------------------------
    # CREATE GOOGLE AUTHORIZATION URL
    # -----------------------------------------------------

    authorization_url, state = (
        flow.authorization_url(

            access_type="offline",

            include_granted_scopes="true",

            prompt="consent"
        )
    )


    # -----------------------------------------------------
    # SAVE OAUTH STATE
    # -----------------------------------------------------

    session["oauth_state"] = state


    # -----------------------------------------------------
    # SAVE PKCE CODE VERIFIER
    # -----------------------------------------------------
    #
    # The same verifier must be available during the
    # callback/token exchange.
    #

    session["oauth_code_verifier"] = (
        flow.code_verifier
    )


    return redirect(
        authorization_url
    )


# =========================================================
# GOOGLE CALLBACK
# =========================================================

@auth_bp.route(
    "/auth/google/callback",
    methods=["GET"]
)
def google_callback():

    saved_state = session.get(
        "oauth_state"
    )

    returned_state = request.args.get(
        "state"
    )

    saved_code_verifier = session.get(
        "oauth_code_verifier"
    )


    # -----------------------------------------------------
    # CHECK STATE
    # -----------------------------------------------------

    if not saved_state:

        return jsonify({
            "error": "OAuth session expired"
        }), 400


    if (
        not returned_state
        or returned_state != saved_state
    ):

        return jsonify({
            "error": "Invalid OAuth state"
        }), 400


    # -----------------------------------------------------
    # CHECK CODE VERIFIER
    # -----------------------------------------------------

    if not saved_code_verifier:

        return jsonify({
            "error": (
                "OAuth code verifier is missing"
            )
        }), 400


    try:

        # -------------------------------------------------
        # CREATE SAME FLOW WITH ORIGINAL VERIFIER
        # -------------------------------------------------

        flow = create_google_flow(
            code_verifier=saved_code_verifier
        )


        # -------------------------------------------------
        # EXCHANGE AUTHORIZATION CODE
        # -------------------------------------------------

        flow.fetch_token(
            authorization_response=request.url
        )


        credentials = flow.credentials


        if not credentials.id_token:

            return jsonify({
                "error": (
                    "Google ID token missing"
                )
            }), 400


        # -------------------------------------------------
        # VERIFY GOOGLE USER
        # -------------------------------------------------

        user_info = (
            id_token.verify_oauth2_token(

                credentials.id_token,

                google_requests.Request(),

                current_app.config[
                    "GOOGLE_CLIENT_ID"
                ]
            )
        )


        google_id = user_info.get(
            "sub"
        )

        email = user_info.get(
            "email"
        )

        name = user_info.get(
            "name"
        )

        picture = user_info.get(
            "picture"
        )


        if not google_id or not email:

            return jsonify({
                "error": (
                    "Google account information "
                    "is incomplete"
                )
            }), 400


        # -------------------------------------------------
        # FIND USER
        # -------------------------------------------------

        user = User.query.filter_by(
            google_id=google_id
        ).first()


        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        if not user:

            user = User(

                google_id=google_id,

                email=email,

                name=name,

                profile_picture=picture
            )

            db.session.add(user)


        # -------------------------------------------------
        # UPDATE EXISTING USER
        # -------------------------------------------------

        else:

            user.email = email

            user.name = name

            user.profile_picture = (
                picture
            )


        # -------------------------------------------------
        # SAVE GOOGLE ACCESS TOKEN
        # -------------------------------------------------

        user.google_access_token = (
            credentials.token
        )


        # -------------------------------------------------
        # SAVE REFRESH TOKEN
        # -------------------------------------------------
        #
        # Google may not return a new refresh token
        # every time.
        #

        if credentials.refresh_token:

            user.google_refresh_token = (
                credentials.refresh_token
            )


        # -------------------------------------------------
        # SAVE TOKEN EXPIRY
        # -------------------------------------------------

        if credentials.expiry:

            user.google_token_expiry = (
                credentials.expiry
                .replace(
                    tzinfo=None
                )
            )


        # -------------------------------------------------
        # SAVE DATABASE
        # -------------------------------------------------

        db.session.commit()


        # -------------------------------------------------
        # MANAGER X SESSION
        # -------------------------------------------------

        session["user_id"] = user.id


        # -------------------------------------------------
        # REMOVE TEMPORARY OAUTH DATA
        # -------------------------------------------------

        session.pop(
            "oauth_state",
            None
        )

        session.pop(
            "oauth_code_verifier",
            None
        )


        # -------------------------------------------------
        # SEND USER TO DASHBOARD
        # -------------------------------------------------

        return redirect(
            f'{current_app.config["FRONTEND_URL"]}'
            "/dashboard"
        )


    except Exception as error:

        db.session.rollback()


        # Useful for local debugging
        print(
            "Google OAuth error:",
            error
        )


        session.pop(
            "oauth_state",
            None
        )

        session.pop(
            "oauth_code_verifier",
            None
        )


        return jsonify({
            "error": (
                "Google authentication failed"
            )
        }), 500


# =========================================================
# CURRENT USER
# =========================================================

@auth_bp.route(
    "/api/me",
    methods=["GET"]
)
def current_user():

    user_id = session.get(
        "user_id"
    )


    if not user_id:

        return jsonify({
            "authenticated": False
        }), 401


    user = db.session.get(
        User,
        user_id
    )


    if not user:

        session.clear()

        return jsonify({
            "authenticated": False
        }), 401


    return jsonify({

        "authenticated": True,

        "user": {

            "id": user.id,

            "name": user.name,

            "email": user.email,

            "profile_picture": (
                user.profile_picture
            )
        }

    }), 200


# =========================================================
# LOGOUT
# =========================================================

@auth_bp.route(
    "/api/logout",
    methods=["POST"]
)
def logout():

    session.clear()


    return jsonify({
        "message": (
            "Logged out successfully"
        )
    }), 200