import pytest

pytestmark = pytest.mark.asyncio


async def test_auth_history(api_request):
    body = {
        "username": "auth_hist_user",
        "password": "auth_hist_pwd"
    }
    await api_request(method="POST", path="/user", body=body)
    for i in range(5):
        response = await api_request(method="POST", path="/login", body=body)

    headers = {
        "Authorization": f'Token {response.body.get("access_token")}'
    }
    response = await api_request(method="GET", path="/auth_history?page=1&page_size=10", headers=headers)

    assert len(response.body.get("results")) == 5
