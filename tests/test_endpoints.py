import pytest

from env_setup import client, db_setup, anyio_backend

class TestEndpoints:
    @pytest.mark.anyio
    async def test_create_user(self, client, db_setup):
        user = {
            "username": "test",
            "password": "password",
            "email": "email"
        }
        response = await client.post("/users", json=user)
        response_data = response.json()
        assert response.status_code == 201
        assert response_data["username"] == "test"
        assert response_data["email"] == "email"
    
    @pytest.mark.anyio
    async def test_create_user_already_exist(self, client, db_setup):
        user = {
            "username": "test",
            "password": "password",
            "email": "email"
        }
        await client.post("/users", json=user)
        response = await client.post("/users", json=user)
        assert response.status_code == 409
    
    @pytest.mark.anyio
    async def test_token(self, client, db_setup):
        user = {
            "username": "test",
            "password": "password",
            "email": "email"
        }
        await client.post("/users", json=user)
        
        auth_info = {
            "username": "test",
            "password": "password"
        }
        response = await client.post("/token", data=auth_info)
        response_data = response.json()
        assert response.status_code == 200
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert response_data["token_type"] == "bearer"
    
    @pytest.mark.anyio
    async def test_token_unauthorized(self, client, db_setup):
        user = {
            "username": "test",
            "password": "password",
            "email": "email"
        }
        await client.post("/users", json=user)
        
        auth_info = {
            "username": "test",
            "password": "wrong_password"
        }
        response = await client.post("/token", data=auth_info)
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_get_user_info(self, client, db_setup):
        user = {
            "username": "test",
            "password": "password",
            "email": "email"
        }
        await client.post("/users", json=user)
        response = await client.post("/token", data=user)
        token = response.json()["access_token"]
        
        headers = {'Authorization': f'Bearer {token}'}
        response = await client.get("/users/me", headers=headers)
        response_data = response.json()
        assert response.status_code == 200
        assert response_data["username"] == "test"
        assert response_data["email"] == "email"
    
    @pytest.mark.anyio
    async def test_get_user_info_unauthorized(self, client, db_setup):
        user = {
            "username": "test",
            "password": "password",
            "email": "email"
        }
        await client.post("/users", json=user)
        response = await client.get("/users/me")
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_update_user_info(self, client, db_setup):
        user = {
            "username": "test",
            "password": "password",
            "email": "email"
        }
        await client.post("/users", json=user)
        response = await client.post("/token", data=user)
        token = response.json()["access_token"]
        
        headers = {'Authorization': f'Bearer {token}'}
        update_info = {
            "username": "test2",
            "email": "email2"
        }
        response = await client.put("/users", json=update_info, headers=headers)
        response_data = response.json()
        assert response.status_code == 200
        assert response_data["username"] == "test2"
        assert response_data["email"] == "email2"
        
    @pytest.mark.anyio
    async def test_update_user_password(self, client, db_setup):
        user = {
            "username": "test",
            "password": "password",
            "email": "email"
        }
        await client.post("/users", json=user)
        response = await client.post("/token", data=user)
        token = response.json()["access_token"]
        
        headers = {'Authorization': f'Bearer {token}'}
        update_info = {
            "password": "password2"
        }
        await client.put("/users", json=update_info, headers=headers)
        
        response = await client.post("/token", data=user)
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_update_user_duplicate_username(self, client, db_setup):
        other_user = {
            "username": "test2",
            "password": "password2"
        }
        await client.post("/users", json=other_user)
        user = {
            "username": "test",
            "password": "password",
            "email": "email"
        }
        await client.post("/users", json=user)
        response = await client.post("/token", data=user)
        token = response.json()["access_token"]
        
        headers = {'Authorization': f'Bearer {token}'}
        update_info = {
            "username": "test2"
        }
        response = await client.put("/users", json=update_info, headers=headers)
        assert response.status_code == 409
    
    @pytest.mark.anyio
    async def test_update_user_info_unauthorized(self, client, db_setup):
        user = {
            "username": "test",
            "password": "password",
            "email": "email"
        }
        await client.post("/users", json=user)
        
        update_info = {
            "username": "test2",
            "email": "email2"
        }
        response = await client.put("/users", json=update_info)
        assert response.status_code == 401
    
    @pytest.mark.anyio
    async def test_delete_user(self, client, db_setup):
        user = {
            "username": "test",
            "password": "password",
            "email": "email"
        }
        await client.post("/users", json=user)
        response = await client.post("/token", data=user)
        token = response.json()["access_token"]
        
        headers = {'Authorization': f'Bearer {token}'}
        response = await client.delete("/users", headers=headers)
        assert response.status_code == 204
        
        response = await client.get("/users/me", headers=headers)
        assert response.status_code == 401
        response = await client.post("/token", data=user)
        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_delete_user_unauthorized(self, client, db_setup):
        user = {
            "username": "test",
            "password": "password",
            "email": "email"
        }
        await client.post("/users", json=user)
        response = await client.delete("/users")
        assert response.status_code == 401