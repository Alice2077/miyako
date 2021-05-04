import re
import math
import random
import asyncio


from hoshino import Service, priv, util
from hoshino.typing import CQEvent
import hoshino

sv = Service('repeater', help_='''
复读他人的话
'''.strip())

@sv.on_rex(r'(.*)我(.*)')
async def repeat(bot, ev: CQEvent):
    msg = ev.message.extract_plain_text()
    uid = ev['user_id']
    if uid in hoshino.config.SUPERUSERS:
        msg = msg.replace("我",hoshino.config.NICKNAME)
        await bot.send(ev, msg, at_sender=False)
    else:
        msg = msg.replace("我","你")
        await bot.send(ev, msg, at_sender=False)
    await asyncio.sleep(random.randint(1,60))