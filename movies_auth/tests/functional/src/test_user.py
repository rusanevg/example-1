import pytest

pytestmark = pytest.mark.asyncio


async def test_create_user_with_empty_username(api_request):
    body = {
        "username": "",
        "password": "test_pwd"
    }
    response = await api_request(method="POST", path="/user", body=body)
    assert response.body.get("error") == "Username is empty"


async def test_create_user_with_empty_password(api_request):
    body = {
        "username": "test_user",
        "password": ""
    }
    response = await api_request(method="POST", path="/user", body=body)
    assert response.body.get("error") == "Password is empty"


async def test_create_user(api_request):
    body = {
        "username": "test_user",
        "password": "test_pwd"
    }
    response = await api_request(method="POST", path="/user", body=body)
    assert response.body.get("username") == body.get("username")
    assert response.body.get("password") is not None
    assert response.body.get("uuid") is not None
    assert response.body.get("salt") is not None


async def test_create_user_with_existing_username(api_request):
    body = {
        "username": "test_user",
        "password": "test_pwd"
    }
    response = await api_request(method="POST", path="/user", body=body)
    assert response.body.get("error") == "Key (username)=(test_user) already exists."


@pytest.mark.skip
async def test_change_user(api_request):
    body = {
        "username": "test_user",
        "password": "test_pwd"
    }
    response = await api_request(method="POST", path="/login", body=body)
    access_token = response.body.get("access_token")
    headers = {
        "Authorization": f"Token {access_token}"
    }
    body = {
        "username": "test_user2",
        "password": "test_pwd2"
    }
    response = await api_request(method="PUT", path="/user", body=body, headers=headers)
    assert response.body.get("item").get("username") == body.get("username")
    assert response.body.get("message") == "Updated"
