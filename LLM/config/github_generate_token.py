from github import Github, Auth, GithubIntegration
from config.config import get_settings


class GithubTokenManager:
    def __init__(self):
        self.settings = get_settings()

    def _integration(self) -> GithubIntegration:
        with open(self.settings.GITHUB_PRIVATE_KEY_PATH, "r") as key_file:
            private_key = key_file.read()
        auth = Auth.AppAuth(app_id=self.settings.GITHUB_APP_ID, private_key=private_key)
        return GithubIntegration(auth=auth)

    def get_installation_token(self) -> str:
        """Returns a short-lived installation token (valid ~1 hour) for repo access."""
        access_token = self._integration().get_access_token(self.settings.GITHUB_INSTALLATION_ID)
        return access_token.token

    def get_repo(self, owner: str, repo: str):
        token = self.get_installation_token()
        return Github(auth=Auth.Token(token)).get_user(owner).get_repo(repo)
