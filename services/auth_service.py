import keyring
import httpx
import asyncio

SERVICE_NAME = "GitRepoLauncher"

class AuthService:
    @staticmethod
    async def validate_and_save_async(token):
        """Verifies the token with GitHub asynchronously and saves it securely."""
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.github.com/user", headers=headers, timeout=5)
            
            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get("login")
                
                # keyring operations remain sync as they are system calls
                keyring.set_password(SERVICE_NAME, "token", token)
                keyring.set_password(SERVICE_NAME, "username", username)
                
                return {"success": True, "username": username}
            else:
                return {"success": False, "error": "Invalid token"}
                
        except httpx.RequestError as e:
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def validate_and_save(token):
        """Sync wrapper for the async validation."""
        return asyncio.run(AuthService.validate_and_save_async(token))

    @staticmethod
    def get_current_user():
        """Returns the username if logged in, else None (Sync)."""
        return keyring.get_password(SERVICE_NAME, "username")

    @staticmethod
    def get_token():
        """Retrieves the token for API calls (Sync)."""
        return keyring.get_password(SERVICE_NAME, "token")

    @staticmethod
    def logout():
        """Removes credentials from the keychain."""
        try:
            # We check if they exist before deleting to avoid unnecessary exceptions
            if keyring.get_password(SERVICE_NAME, "token"):
                keyring.delete_password(SERVICE_NAME, "token")
            if keyring.get_password(SERVICE_NAME, "username"):
                keyring.delete_password(SERVICE_NAME, "username")
            return True
        except Exception:
            return False