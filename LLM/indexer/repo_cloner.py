import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from git import Repo, GitCommandError
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

    @contextmanager
    def clone_repo(self, owner: str, repo: str):
        """Clones a repo into a temporary directory and cleans up automatically.

        Usage:
            with cloner.clone_repo("owner", "repo") as path:
                ...  # process files under path
        """
        token = self._get_token()

        # Pass token as HTTP header — never embedded in the URL or process list
        git_env = dict(os.environ)
        git_env["GIT_CONFIG_COUNT"] = "1"
        git_env["GIT_CONFIG_KEY_0"] = "http.extraheader"
        git_env["GIT_CONFIG_VALUE_0"] = f"Authorization: token {token}"

        # TemporaryDirectory guarantees cleanup even if an exception is raised
        with tempfile.TemporaryDirectory() as tmp_dir:
            clone_path = Path(tmp_dir) / repo
            Repo.clone_from(
                f"https://github.com/{owner}/{repo}.git",
                str(clone_path),
                env=git_env,
            )
            yield clone_path
