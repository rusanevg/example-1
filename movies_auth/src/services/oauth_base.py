from oauthlib.oauth2 import WebApplicationClient
from models.social_account import SocialAccount
from models.user import User
from services.exceptions import OauthProviderError
import requests
from utils.api_utils import generate_password_hash, generate_random_string
from utils.backoff import backoff


class OAuthProvider:
    def __init__(
        self,
        db,
        provider_name,
        authorization_endpoint=None,
        userinfo_endpoint=None,
        token_endpoint=None,
        client_id=None,
        client_secret=None,
        discovery_url=None,
        scope=None
    ) -> None:
        self.db = db
        self.provider_name = provider_name
        self.authorization_endpoint = authorization_endpoint
        self.userinfo_endpoint = userinfo_endpoint
        self.token_endpoint = token_endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self.discovery_url = discovery_url
        self.scope = scope

    def get_client_provider(self) -> WebApplicationClient:
        return WebApplicationClient(self.client_id)

    def get_user(self, social_id, email) -> User:
        social_account = SocialAccount.query.with_entities(SocialAccount)\
            .filter_by(social_name=self.provider_name, social_id=social_id).first()
        if social_account:
            # ищем пользователя по соц. аккаунту
            user = User.query.get(social_account.user_id)
        else:
            # или по электронной почте
            user = User.query.with_entities(User).filter_by(email=email).first()
        if not user:
            username = f"{self.provider_name}.{social_id}"
            pwd_hash, salt = generate_password_hash(generate_random_string(16))
            user = User(username=username, password=pwd_hash, salt=salt, email=email)
            self.db.session.add(user)
            self.db.session.commit()
        if not social_account:
            self.db.session.add(
                SocialAccount(user_id=user.uuid, social_name=self.provider_name, social_id=social_id)
            )
            self.db.session.commit()
        return user


class GoogleOAuthProvider(OAuthProvider):
    def __init__(
        self,
        db,
        provider_name,
        authorization_endpoint=None,
        userinfo_endpoint=None,
        token_endpoint=None,
        client_id=None,
        client_secret=None,
        discovery_url=None,
        scope=None
    ) -> None:
        super().__init__(
            db,
            provider_name,
            authorization_endpoint,
            userinfo_endpoint,
            token_endpoint,
            client_id,
            client_secret,
            discovery_url,
            scope
        )

    @backoff()
    def get_config_by_discovery(self):
        if not self.discovery_url:
            raise OauthProviderError("Please enter correct discovery_url")
        return requests.get(self.discovery_url).json()

    def set_config_by_discovery(self):
        config = self.get_config_by_discovery()
        self.authorization_endpoint = config.get("authorization_endpoint")
        self.userinfo_endpoint = config.get("userinfo_endpoint")
        self.token_endpoint = config.get("token_endpoint")

    def get_info(self, userinfo: dict):
        return userinfo.get("sub"), userinfo.get("email")

    def get_redirect_request_uri(self, base_url):
        oauth_client = self.get_client_provider()
        return oauth_client.prepare_request_uri(
            self.authorization_endpoint,
            redirect_uri=base_url + "/callback",
            scope=["openid", "email"],
        )


class YandexOAuthProvider(OAuthProvider):
    def __init__(
        self,
        db,
        provider_name,
        authorization_endpoint=None,
        userinfo_endpoint=None,
        token_endpoint=None,
        client_id=None,
        client_secret=None
    ) -> None:
        super().__init__(
            db,
            provider_name,
            authorization_endpoint,
            userinfo_endpoint,
            token_endpoint,
            client_id,
            client_secret,
            None,
            None
        )

    def get_info(self, userinfo: dict):
        return userinfo.get("id"), userinfo.get("default_email")

    def get_redirect_request_uri(self, base_url):
        oauth_client = self.get_client_provider()
        return oauth_client.prepare_request_uri(
            self.authorization_endpoint,
            redirect_uri=base_url + "/callback",
        )
