from sqids import Sqids
import random


def get_short_uuid() -> str:
    sqids = Sqids()
    message_id = random.randint(100, 999999)
    id = sqids.encode([message_id])
    return id
