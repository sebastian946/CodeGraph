
from contextlib import asynccontextmanager
from fastapi import FastAPI
from indexer.redis_events import RedisEvents
from config.github_generate_token import GithubTokenManager


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_events = RedisEvents()
    github_manager = GithubTokenManager()
    github_client = github_manager.config_token()
    redis_events.save_redis("github_token", str(github_client), ex=3600)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}
