import json
import os
from oauthlib.oauth2 import WebApplicationClient
import requests
from flask import redirect, request

from api.v1.auth import success_login_callback
from app.flask_app import urls
from services.oauth_base import OAuthProvider
from services.oauth_providers import match_oauth_provider
from utils.api_utils import create_error_response

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


@urls.route("/login/<provider>", methods=["GET"])
def oauth_login(provider):
    """
        Login via OAuth
        ---
        tags:
          - oauth
        parameters:
          - in: path
            name: provider
            type: string
            required: true
        responses:
          302:
            description: Redirect to provider
    """
    oauth_provider: OAuthProvider = match_oauth_provider(provider)
    request_uri = oauth_provider.get_redirect_request_uri(request.base_url)
    return redirect(request_uri)


@urls.route("/login/<provider>/callback", methods=["GET"])
def oauth_callback(provider):
    """
        OAuth login callback
        ---
        tags:
          - oauth
        parameters:
          - in: path
            name: provider
            type: string
            required: true
        responses:
          200:
            description: Success user's login
          400:
            description: Error
    """
    oauth_provider: OAuthProvider = match_oauth_provider(provider)
    oauth_client = oauth_provider.get_client_provider()
    code = request.args.get("code")
    token_response = get_token(oauth_provider, code)
    oauth_client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = oauth_provider.userinfo_endpoint
    uri, headers, body = oauth_client.add_token(userinfo_endpoint)
    userinfo = requests.get(uri, headers=headers, data=body).json()
    social_id, email = oauth_provider.get_info(userinfo)
    if not social_id or not email:
        return create_error_response((f"User email not available or not verified by {provider}.", 400))
    user = oauth_provider.get_user(social_id=social_id, email=email)
    return success_login_callback(user.uuid)


def get_token(oauth_provider: OAuthProvider, oauth_client: WebApplicationClient, code: str):
    token_url, headers, body = oauth_client.prepare_token_request(
        oauth_provider.token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    return requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(oauth_provider.client_id, oauth_provider.client_secret),
    )
