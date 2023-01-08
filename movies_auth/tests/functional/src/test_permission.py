import pytest

pytestmark = pytest.mark.asyncio


async def test_create_permission(api_request):
    body = {
        "username": "superuser",
        "password": "su_pwd"
    }
    response = await api_request(method="POST", path="/login", body=body)
    headers = {
        "Authorization": f'Token {response.body.get("access_token")}'
    }
    body = {
        "name": "test_permission"
    }
    response = await api_request(method="POST", path="/permission", body=body, headers=headers)
    print(response.body)
    assert response.body.get("name") == body.get("name")


async def test_change_permission(api_request):
    body = {
        "username": "superuser",
        "password": "su_pwd"
    }
    response = await api_request(method="POST", path="/login", body=body)
    headers = {
        "Authorization": f'Token {response.body.get("access_token")}'
    }
    body = {
        "name": "permission_to_change"
    }
    response = await api_request(method="POST", path="/permission", body=body, headers=headers)
    body = {
        "name": "changed_permission"
    }
    response = await api_request(method="PUT", path=f'/permission/{response.body.get("uuid")}', body=body,
                                 headers=headers)
    assert response.body.get("item").get("name") == body.get("name")
    assert response.body.get("message") == "Updated"


async def test_add_remove_permission_by_role(api_request):
    body = {
        "username": "superuser",
        "password": "su_pwd"
    }
    response = await api_request(method="POST", path="/login", body=body)
    headers = {
        "Authorization": f'Token {response.body.get("access_token")}'
    }
    body = {
        "name": "role_without_permissions"
    }
    role_response = await api_request(method="POST", path="/role", body=body, headers=headers)
    body = {
        "name": "permission_without_roles"
    }
    permission_response = await api_request(method="POST", path="/permission", body=body, headers=headers)
    body = {
        "role_id": role_response.body.get("uuid"),
        "permission_id": permission_response.body.get("uuid")
    }
    response = await api_request(method="POST", path="/role_permission_add", body=body, headers=headers)
    assert response.body.get("role_id") == body.get("role_id")
    assert response.body.get("permission_id") == body.get("permission_id")

    response = await api_request(method="POST", path="/role_permission_revoke", body=body, headers=headers)
    assert response.status == 204


async def test_check_permission(api_request):
    """
    Создаём по два объекта user, role, permission
    Связываем их через UserRole и RolePermission следующим образом:
        user1 -> role1 -> permission1
        user2 -> role2 -> permission2
    Проверяем соответствие user <-> permission
    """
    body = {
        "username": "superuser",
        "password": "su_pwd"
    }
    response = await api_request(method="POST", path="/login", body=body)
    headers = {
        "Authorization": f'Token {response.body.get("access_token")}'
    }
    body = {
        "username": "user1",
        "password": "pwd1"
    }
    user1_response = await api_request(method="POST", path="/user", body=body, headers=headers)
    body = {
        "username": "user2",
        "password": "pwd2"
    }
    user2_response = await api_request(method="POST", path="/user", body=body, headers=headers)
    body = {
        "name": "role1"
    }
    role1_response = await api_request(method="POST", path="/role", body=body, headers=headers)
    body = {
        "name": "role2"
    }
    role2_response = await api_request(method="POST", path="/role", body=body, headers=headers)
    body = {
        "name": "permission1"
    }
    permission1_response = await api_request(method="POST", path="/permission", body=body, headers=headers)
    body = {
        "name": "permission2"
    }
    permission2_response = await api_request(method="POST", path="/permission", body=body, headers=headers)

    body = {
        "user_id": user1_response.body.get("uuid"),
        "role_id": role1_response.body.get("uuid")
    }
    await api_request(method="POST", path="/user_role_add", body=body, headers=headers)
    body = {
        "user_id": user2_response.body.get("uuid"),
        "role_id": role2_response.body.get("uuid")
    }
    await api_request(method="POST", path="/user_role_add", body=body, headers=headers)
    body = {
        "role_id": role1_response.body.get("uuid"),
        "permission_id": permission1_response.body.get("uuid")
    }
    await api_request(method="POST", path="/role_permission_add", body=body, headers=headers)
    body = {
        "role_id": role2_response.body.get("uuid"),
        "permission_id": permission2_response.body.get("uuid")
    }
    await api_request(method="POST", path="/role_permission_add", body=body, headers=headers)

    body = {
        "user_id": user1_response.body.get("uuid"),
        "permission_name": "permission1"
    }
    response = await api_request(method="POST", path="/check_permission", body=body, headers=headers)
    assert response.body.get("result") is True

    body = {
        "user_id": user2_response.body.get("uuid"),
        "permission_name": "permission2"
    }
    response = await api_request(method="POST", path="/check_permission", body=body, headers=headers)
    assert response.body.get("result") is True

    body = {
        "user_id": user1_response.body.get("uuid"),
        "permission_name": "permission2"
    }
    response = await api_request(method="POST", path="/check_permission", body=body, headers=headers)
    assert response.body.get("result") is False

    body = {
        "user_id": user2_response.body.get("uuid"),
        "permission_name": "permission1"
    }
    response = await api_request(method="POST", path="/check_permission", body=body, headers=headers)
    assert response.body.get("result") is False
