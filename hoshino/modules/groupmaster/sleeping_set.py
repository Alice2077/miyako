import re
import math
import random



from hoshino import Service, priv, util
from hoshino.typing import CQEvent

sv = Service('sleeping-set', help_='''
[精致睡眠] 8小时精致睡眠(bot需具有群管理权限)
[给我来一份精致昏睡下午茶套餐] 叫一杯先辈特调红茶(bot需具有群管理权限)
'''.strip())

@sv.on_fullmatch(('睡眠套餐', '休眠套餐', '精致睡眠', '来一份精致睡眠套餐'))
async def sleep_8h(bot, ev):
    await util.silence(ev, 8*60*60, skip_su=False)


@sv.on_rex(r'(来|來)(.*(份|个)(.*)(睡|茶)(.*))套餐')
async def sleep(bot, ev: CQEvent):
    base = 0 if '午' in ev.plain_text else 5*60*60
    length = len(ev.plain_text)
    sleep_time = base + round(math.sqrt(length) * 60 * 30 + 60 * random.randint(-15, 15))
    await util.silence(ev, sleep_time, skip_su=False)


@sv.on_rex(r'(.*)(狗|苟|早泄)(群|裙)主(.*)')
async def sleep(bot, ev: CQEvent):
    sleep_time = random.randint(30,60)*60
    await util.silence(ev, sleep_time, skip_su=True)

@sv.on_rex(r'(.*)(狗|苟|臭)(布丁|机器人)(.*)')
async def sleep(bot, ev: CQEvent):
    sleep_time = random.randint(10,30)*60
    await util.silence(ev, sleep_time, skip_su=True)