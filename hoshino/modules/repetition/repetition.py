import re
import math
import random
import asyncio


from hoshino import Service, priv, util
from hoshino.typing import CQEvent
from hoshino.modules.yinglish import yinglish
import hoshino

sv = Service('repeater', help_='''
复读他人的话
'''.strip())

is_repeated = False
p=0.3

@sv.on_rex(r'(.*)我(.*)')
async def repeat(bot, ev: CQEvent):
    global is_repeated
    global p
    if is_repeated == False:
        if random.random() < p:
            msg = ev.message.extract_plain_text()
            uid = ev['user_id']
            if uid in hoshino.config.SUPERUSERS:
                msg = msg.replace("我",list(hoshino.config.NICKNAME)[0])
            else:
                msg = msg.replace("我","你")
            msg = yinglish.chs2yin(msg, random.random())
            await bot.send(ev, msg, at_sender=False)
            # is_repeated = True
            # await asyncio.sleep(random.randint(1,60))
            # is_repeated = False
            p=0.3
        else:
            p = 1 - (1 - p) / 1.5
