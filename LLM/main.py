from contextlib import asynccontextmanager
from fastapi import FastAPI
from indexer.redis_events import RedisEvents
from config.github_generate_token import GithubTokenManager


@asynccontextmanager
async def lifespan(_: FastAPI):
    token = GithubTokenManager().get_installation_token()
    RedisEvents().save_encrypted("github_token", token, ex=3600)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}
