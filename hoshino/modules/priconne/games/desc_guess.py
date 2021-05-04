# ref: https://github.com/GWYOG/GWYOG-Hoshino-plugins/blob/master/pcrdescguess
# Originally written by @GWYOG
# Reflacted by @Ice-Cirno
# GPL-3.0 Licensed
# Thanks to @GWYOG for his great contribution!

import asyncio
import os
import random

import hoshino
from hoshino import Service
from hoshino.modules.priconne import chara
from hoshino.typing import CQEvent, MessageSegment as Seg

from .. import _pcr_desc_data
from . import GameMaster

import math, sqlite3, os, random, asyncio
from hoshino.modules.priconne import daylimiter
COUNT_PATH = os.path.expanduser("~/.hoshino/pcr_descguess.db")
db = daylimiter.RecordDAO(COUNT_PATH)
MAX_GUESS_NUM = 3#每日最多获得金币次数
INIT_TIME = 5 #每日重置时间
daily_desc_limiter = daylimiter.DailyAmountLimiter("descguess", MAX_GUESS_NUM, INIT_TIME, db)
_tlmt = hoshino.util.DailyNumberLimiter(3)  #限制调用功能次数
SCORE_DB_PATH = os.path.expanduser('~/.hoshino/pcr_running_counter.db')





PREPARE_TIME = 5
ONE_TURN_TIME = 12
TURN_NUMBER = 5
DB_PATH = os.path.expanduser("~/.hoshino/pcr_desc_guess.db")

gm = GameMaster(DB_PATH)
sv = Service("pcr-desc-guess", bundle="pcr娱乐", help_="""
[猜角色] 猜猜bot在描述哪位角色
[猜角色排行] 显示小游戏的群排行榜(只显示前十)
""".strip()
)

class ScoreCounter2:
    def __init__(self):
        os.makedirs(os.path.dirname(SCORE_DB_PATH), exist_ok=True)
        self._create_table()

    def _connect(self):
        return sqlite3.connect(SCORE_DB_PATH)

    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS SCORECOUNTER
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           SCORE           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建表发生错误')

    def _add_score(self, gid, uid, score):
        try:
            current_score = self._get_score(gid, uid)
            conn = self._connect()
            conn.execute("INSERT OR REPLACE INTO SCORECOUNTER (GID,UID,SCORE) \
                                VALUES (?,?,?)", (gid, uid, current_score + score))
            conn.commit()
        except:
            raise Exception('更新表发生错误')

    def _reduce_score(self, gid, uid, score):
        try:
            current_score = self._get_score(gid, uid)
            if current_score >= score:
                conn = self._connect()
                conn.execute("INSERT OR REPLACE INTO SCORECOUNTER (GID,UID,SCORE) \
                                VALUES (?,?,?)", (gid, uid, current_score - score))
                conn.commit()
            else:
                conn = self._connect()
                conn.execute("INSERT OR REPLACE INTO SCORECOUNTER (GID,UID,SCORE) \
                                VALUES (?,?,?)", (gid, uid, 0))
                conn.commit()
        except:
            raise Exception('更新表发生错误')

    def _get_score(self, gid, uid):
        try:
            r = self._connect().execute("SELECT SCORE FROM SCORECOUNTER WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找表发生错误')

    # 判断金币是否足够下注
    def _judge_score(self, gid, uid, score):
        try:
            current_score = self._get_score(gid, uid)
            if current_score >= score:
                return 1
            else:
                return 0
        except Exception as e:
            raise Exception(str(e))

async def get_user_card_dict(bot, group_id):
    mlist = await bot.get_group_member_list(group_id=group_id)
    d = {}
    for m in mlist:
        d[m['user_id']] = m['card'] if m['card']!='' else m['nickname']
    return d

def uid2card(uid, user_card_dict):
    return str(uid) if uid not in user_card_dict.keys() else user_card_dict[uid]
    
    
    
@sv.on_fullmatch(("猜角色排行", "猜角色排名", "猜角色排行榜", "猜角色群排行"))
async def description_guess_group_ranking(bot, ev: CQEvent):
    ranking = gm.db.get_ranking(ev.group_id)
    msg = ["【猜角色小游戏排行榜】"]
    for i, item in enumerate(ranking):
        uid, count = item
        m = await bot.get_group_member_info(self_id=ev.self_id, group_id=ev.group_id, user_id=uid)
        name = m["card"] or m["nickname"] or str(uid)
        msg.append(f"第{i + 1}名：{name} 猜对{count}次")
    await bot.send(ev, "\n".join(msg))


@sv.on_fullmatch(("猜角色", "猜人物"))
async def description_guess(bot, ev: CQEvent):
    if gm.is_playing(ev.group_id):
        await bot.finish(ev, "游戏仍在进行中…")
    """-----------------------------------------------------------"""
    uid = ev['user_id']
    if uid not in hoshino.config.SUPERUSERS:
        if not _tlmt.check(uid):
            await bot.finish(ev, "让大家都参与进来会更有意思哦~")
        else:
            _tlmt.increase(uid,1)
    else:
        await bot.send(ev, "我知道你偷偷改代码作弊了！")
    """-----------------------------------------------------------"""
    with gm.start_game(ev.group_id) as game:
        game.answer = random.choice(list(_pcr_desc_data.CHARA_PROFILE.keys()))
        c = chara.fromid(game.answer)
        #print(c.name)
        profile = _pcr_desc_data.CHARA_PROFILE[game.answer]
        kws = list(profile.keys())
        kws.remove('名字')
        random.shuffle(kws)
        kws = kws[:TURN_NUMBER]
        await bot.send(ev, f"{PREPARE_TIME}秒后每隔{ONE_TURN_TIME}秒我会给出某位角色的一个描述，根据这些描述猜猜她是谁~")
        await asyncio.sleep(PREPARE_TIME)
        for i, k in enumerate(kws):
            await bot.send(ev, f"提示{i + 1}/{len(kws)}:\n她的{k}是 {profile[k]}")
            await asyncio.sleep(ONE_TURN_TIME)
            if game.winner:
                return

    await bot.send(ev, f"正确答案是：{c.name} {c.icon.cqcode}\n很遗憾，没有人答对~")


@sv.on_message()
async def on_input_chara_name(bot, ev: CQEvent):
    game = gm.get_game(ev.group_id)
    gid = ev.group_id
    uid = ev.user_id      

    if not game or game.winner:
        return
    c = chara.fromname(ev.message.extract_plain_text())
    if c.id != chara.UNKNOWN and c.id == game.answer:
        game.winner = ev.user_id
        n = game.record()
        user_card_dict = await get_user_card_dict(bot, ev.group_id)
        user_card = uid2card(ev.user_id, user_card_dict)     
        msg = f"正确答案是：{c.name}{c.icon.cqcode}\n{Seg.at(ev.user_id)}猜对了，真厉害！TA已经猜对{n}次了~\n(此轮游戏将在几秒后自动结束，请耐心等待)"
        guid = gid,uid
        if  daily_desc_limiter.check(guid):
            score_counter = ScoreCounter2() 
            daily_desc_limiter.increase(guid)
            dailynum = daily_desc_limiter.get_num(guid)
            score_counter._add_score(gid,uid,200)            
            msg += f'\n{user_card}获得了200金币哦。(今天第{dailynum}/{MAX_GUESS_NUM}次)'

        await bot.send(ev, msg)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
