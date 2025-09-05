import asyncio
import logging
import signal
import sys

import redis.asyncio as redis
from db import session_factory
from models import User
from sqlalchemy import asc, desc, select

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class TokenStopper:
    def __init__(self, event):
        self.stop_event = event
        signal.signal(signal.SIGINT, self.stop_cleaner)
        signal.signal(signal.SIGTERM, self.stop_cleaner)

    def stop_cleaner(self, signum, frame):
        self.stop_event.set()
        sys.exit(0)


class TokenCleaner:
    WAITING_TIME = 1500  # 25 mins

    def __init__(self, event):
        self.end = None
        self.start = None
        self.redis = redis.Redis(host="127.0.0.1", db=1, decode_responses=True)
        self.stop_event = event

    async def close(self):
        await self.redis.aclose()

    async def get_end_of_iter(self):
        async with session_factory() as session:
            start_query = select(User).order_by(asc(User.id)).limit(1)
            end_query = select(User).order_by(desc(User.id)).limit(1)
            result_1 = await session.execute(start_query)
            result_2 = await session.execute(end_query)
            user_start = result_1.scalar_one_or_none()
            if user_start:
                self.start = user_start.id
            user_end = result_2.scalar_one_or_none()
            if user_end:
                self.end = user_end.id

    async def delete_expired_tokens_redis(self, uid):
        expired_tokens = []
        tokens = list(await self.redis.smembers(f"user:{uid}"))
        if not tokens:
            return 0
        token_case = [f"{uid}:{token}" for token in tokens]
        tokens_chk = await self.redis.mget(*token_case)
        for i, value in enumerate(tokens_chk):
            if value is None:
                expired_tokens.append(tokens[i])
        await self.redis.srem(f"user:{uid}", *expired_tokens)

    async def take_timeout(self, time: float):
        try:
            logging.info("CLEANER IS SLEEP")
            await asyncio.wait_for(self.stop_event.wait(), timeout=time)
        except asyncio.TimeoutError:
            pass

    async def users_clean(self):
        try:
            count = 0
            for i in range(self.start, self.end, 1000):
                ids = [f"user:{j}" for j in range(i, i + 1000)]
                pipeline = self.redis.pipeline()
                for user_key in ids:
                    await pipeline.exists(user_key)
                result = await pipeline.execute()
                count += 1
                for number, line in enumerate(result):
                    if line:
                        uid = int(ids[number].split(":")[1])
                        await self.delete_expired_tokens_redis(uid)
                if count % 10 == 0:
                    await self.take_timeout(300.0)
            self.end = None
        except Exception as e:
            logging.error(f"The circle have a some error :{e}")

    async def run(self):
        try:
            logging.info("CLEANER START WORK")
            while not self.stop_event.is_set():
                await self.get_end_of_iter()
                if self.start and self.end and self.start <= self.end:
                    await self.users_clean()
                await self.take_timeout(300)
        finally:
            await self.close()
            logging.info("CLEANER HAS STOPPED")


async def main():
    event = asyncio.Event()
    TokenStopper(event)
    cleaner = TokenCleaner(event)

    await cleaner.run()


if __name__ == "__main__":
    asyncio.run(main())
