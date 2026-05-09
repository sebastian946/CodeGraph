from github import Github, Auth
from config import _get_env_variable


class GithubTokenManager:
    def __init__(self):
        self.github_app_id = _get_env_variable(self,"GITHUB_APP_ID")

    def config_token(self):
        with open("codegraphtest.2026-05-08.private-key.pem", "r") as key_file:
            private_key = key_file.read()
        auth = Auth.AppAuth(app_id=self.github_app_id,private_key=private_key)
        g = Github(auth=auth)
        return g
    
    def get_repo(self, user:str, repo:str):
        g = self.config_token()
        repository = g.get_user(user).get_repo(repo)
        return repository