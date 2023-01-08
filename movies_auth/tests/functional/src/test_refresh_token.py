import pytest

pytestmark = pytest.mark.asyncio


async def test_refresh_token(api_request):
    body = {
        "username": "refr_user",
        "password": "refr_pwd"
    }
    await api_request(method="POST", path="/user", body=body)
    response = await api_request(method="POST", path="/login", body=body)
    access_token = response.body.get("access_token")
    refresh_token = response.body.get("refresh_token")

    headers = {
        "Authorization": f'Token {access_token}'
    }
    body = {
        "refresh_token": refresh_token
    }
    response = await api_request(method="POST", path="/refresh_token", body=body, headers=headers)

    assert response.body.get("access_token") is not None
    assert response.body.get("refresh_token") is not None
    assert response.body.get("access_token") != access_token
    assert response.body.get("refresh_token") != refresh_token
