from github import Github, Auth
from config.config import get_settings


class GithubTokenManager:
    def __init__(self):
        self.settings = get_settings()

    def config_token(self) -> Github:
        with open(self.settings.GITHUB_PRIVATE_KEY_PATH, "r") as key_file:
            private_key = key_file.read()
        auth = Auth.AppAuth(app_id=self.settings.GITHUB_APP_ID, private_key=private_key)
        return Github(auth=auth)

    def get_repo(self, user: str, repo: str, github_token: Github):
        return github_token.get_user(user).get_repo(repo)