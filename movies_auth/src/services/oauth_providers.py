from services.exceptions import OauthProviderError
from app.flask_app import db, app_config
from services.oauth_base import GoogleOAuthProvider, YandexOAuthProvider

google_provider = GoogleOAuthProvider(
    db=db,
    provider_name=app_config.GOOGLE_SOCIAL_NAME,
    client_id=app_config.GOOGLE_CLIENT_ID,
    client_secret=app_config.GOOGLE_CLIENT_SECRET,
    discovery_url=app_config.GOOGLE_DISCOVERY_URL
)
google_provider.set_config_by_discovery()
yandex_provider = YandexOAuthProvider(
    db=db,
    provider_name=app_config.YANDEX_SOCIAL_NAME,
    authorization_endpoint=app_config.YANDEX_AUTHORIZATION_ENDPOINT,
    userinfo_endpoint=app_config.YANDEX_USERINFO_ENDPOINT,
    token_endpoint=app_config.YANDEX_TOKEN_ENDPOINT,
    client_id=app_config.YANDEX_CLIENT_ID,
    client_secret=app_config.YANDEX_CLIENT_SECRET
)

providers = {
    "google": google_provider,
    "yandex": yandex_provider
}


def match_oauth_provider(provider: str):
    oauth_provider = providers.get(provider)
    if not oauth_provider:
        raise OauthProviderError("Please enter correct provider Oauth")
    return oauth_provider
