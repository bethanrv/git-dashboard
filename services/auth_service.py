import keyring
import requests

SERVICE_NAME = "GitRepoLauncher"

class AuthService:
    @staticmethod
    def validate_and_save(token):
        """Verifies the token with GitHub and saves it securely."""
        try:
            headers = {"Authorization": f"token {token}"}
            response = requests.get("https://api.github.com/user", headers=headers, timeout=5)
            
            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get("login")
                
                # Save to System Keychain
                keyring.set_password(SERVICE_NAME, "token", token)
                keyring.set_password(SERVICE_NAME, "username", username)
                return {"success": True, "username": username}
            else:
                return {"success": False, "error": "Invalid token"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_current_user():
        """Returns the username if logged in, else None."""
        return keyring.get_password(SERVICE_NAME, "username")

    @staticmethod
    def get_token():
        """Retrieves the token for API calls."""
        return keyring.get_password(SERVICE_NAME, "token")

    @staticmethod
    def logout():
        """Removes credentials from the keychain."""
        try:
            keyring.delete_password(SERVICE_NAME, "token")
            keyring.delete_password(SERVICE_NAME, "username")
            return True
        except:
            return False
