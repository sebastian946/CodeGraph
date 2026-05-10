import subprocess
from pathlib import Path
from indexer.redis_events import RedisEvents
from config.github_generate_token import GithubTokenManager


class RepoCloner:
    def __init__(self):
        self.redis = RedisEvents()
        self.github_manager = GithubTokenManager()

    def _get_token(self) -> str:
        token = self.redis.get_decrypted("github_token")
        if token:
            return token
        token = self.github_manager.get_installation_token()
        self.redis.save_encrypted("github_token", token, ex=3600)
        return token

    def clone(self, owner: str, repo: str, target_dir: str) -> Path:
        token = self._get_token()
        # URL contains secret — do not log
        clone_url = f"https://x-access-token:{token}@github.com/{owner}/{repo}.git"
        clone_path = Path(target_dir) / repo
        subprocess.run(
            ["git", "clone", clone_url, str(clone_path)],
            check=True,
            capture_output=True,
        )
        return clone_path
