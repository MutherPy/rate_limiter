import uvicorn

from rate_limiter_service import RateLimiter

from strategies.types import StrategyType
from strategies.factory import strat_factory

from fastapi import FastAPI, Header, Depends, HTTPException, Response
from typing import Annotated



r = RateLimiter(strat_factory=strat_factory)
r.set_strat(StrategyType.TokenBucket)


def limiter() -> RateLimiter:
    return r

app = FastAPI()

@app.get("/check")
async def puk(x_forwarded_for: Annotated[str, Header()], r_l: Annotated[RateLimiter, Depends(limiter)]):
    if not await r_l.check_rate_limit(x_forwarded_for):
        raise HTTPException(status_code=429)
    return Response(status_code=200)

@app.get("/change")
async def change():
    r.set_strat(StrategyType.TokenBucket)
    return Response(status_code=200)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
