import pytest

pytestmark = pytest.mark.asyncio


async def test_create_role(api_request):
    body = {
        "username": "superuser",
        "password": "su_pwd"
    }
    response = await api_request(method="POST", path="/login", body=body)
    headers = {
        "Authorization": f'Token {response.body.get("access_token")}'
    }
    body = {
        "name": "test_role"
    }
    response = await api_request(method="POST", path="/role", body=body, headers=headers)
    print(response.body)
    assert response.body.get("name") == body.get("name")


async def test_change_role(api_request):
    body = {
        "username": "superuser",
        "password": "su_pwd"
    }
    response = await api_request(method="POST", path="/login", body=body)
    headers = {
        "Authorization": f'Token {response.body.get("access_token")}'
    }
    body = {
        "name": "role_to_change"
    }
    response = await api_request(method="POST", path="/role", body=body, headers=headers)
    body = {
        "name": "changed_role"
    }
    response = await api_request(method="PUT", path=f'/role/{response.body.get("uuid")}', body=body, headers=headers)
    assert response.body.get("item").get("name") == body.get("name")
    assert response.body.get("message") == "Updated"


async def test_add_remove_role_by_user(api_request):
    body = {
        "username": "superuser",
        "password": "su_pwd"
    }
    response = await api_request(method="POST", path="/login", body=body)
    headers = {
        "Authorization": f'Token {response.body.get("access_token")}'
    }
    body = {
        "username": "user_without_roles",
        "password": "pwd"
    }
    user_response = await api_request(method="POST", path="/user", body=body, headers=headers)
    body = {
        "name": "role_without_users"
    }
    role_response = await api_request(method="POST", path="/role", body=body, headers=headers)
    body = {
        "user_id": user_response.body.get("uuid"),
        "role_id": role_response.body.get("uuid")
    }
    response = await api_request(method="POST", path="/user_role_add", body=body, headers=headers)
    assert response.body.get("user_id") == body.get("user_id")
    assert response.body.get("role_id") == body.get("role_id")

    response = await api_request(method="POST", path="/user_role_revoke", body=body, headers=headers)
    assert response.status == 204
