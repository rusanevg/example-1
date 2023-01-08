import pytest

pytestmark = pytest.mark.asyncio


async def test_user_login(api_request):
    body = {
        "username": "auth_user",
        "password": "auth_pwd"
    }
    await api_request(method="POST", path="/user", body=body)
    response = await api_request(method="POST", path="/login", body=body)

    assert response.body.get("access_token") is not None
    assert response.body.get("refresh_token") is not None


async def test_user_logout(api_request):
    body = {
        "username": "auth_user",
        "password": "auth_pwd"
    }
    response = await api_request(method="POST", path="/login", body=body)
    headers = {
        "Authorization": f'Token {response.body.get("access_token")}'
    }
    response = await api_request(method="GET", path="/logout", body=body, headers=headers)
    assert response.status == 204
