import disnake
from disnake.ext import commands, tasks
import sqlite3

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' and name='level_table'").fetchone() is None:
            cur.execute("""CREATE TABLE level_table(
                                level INT,
                                xp REAL,
                                gold REAL)""")
            number = 128
            for item in range(1, 101):
                if item < 6:
                    cur.execute(f"INSERT INTO level_table VALUES ({item}, {number}, 10)")
                    number = number * 1.5
                elif item < 11:
                    cur.execute(f"INSERT INTO level_table VALUES ({item}, {number}, 20)")
                    number = number * 1.25
                elif item < 16:
                    cur.execute(f"INSERT INTO level_table VALUES ({item}, {number}, 40)")
                    number = number * 1.15
                elif item < 21:
                    cur.execute(f"INSERT INTO level_table VALUES ({item}, {number}, 60)")
                    number = number * 1.1
                elif item < 31:
                    cur.execute(f"INSERT INTO level_table VALUES ({item}, {number}, 80)")
                    number = number * 1.08
                elif item < 41:
                    cur.execute(f"INSERT INTO level_table VALUES ({item}, {number}, 100)")
                    number = number * 1.05
                elif item < 51:
                    cur.execute(f"INSERT INTO level_table VALUES ({item}, {number}, 120)")
                    number = number * 1.04
                elif item < 61:
                    cur.execute(f"INSERT INTO level_table VALUES ({item}, {number}, 150)")
                    number = number * 1.03
                elif item < 71:
                    cur.execute(f"INSERT INTO level_table VALUES ({item}, {number}, 180)")
                    number = number * 1.02
                elif item < 81:
                    cur.execute(f"INSERT INTO level_table VALUES ({item}, {number}, 250)")
                    number = number * 1.011
                elif item < 91:
                    cur.execute(f"INSERT INTO level_table VALUES ({item}, {number}, 500)")
                    number = number * 1.01
                elif item < 100:
                    cur.execute(f"INSERT INTO level_table VALUES ({item}, {number}, 1000)")
                    number = number * 1.015
                else:
                    cur.execute(f"INSERT INTO level_table VALUES ({item}, {number}, 1000000)")
        db.commit()
        db.close()
        self.check_voice.start()

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        booster = 1
        for role in after.roles:
            role_booster = cur.execute(f"SELECT role_booster FROM role_table WHERE role_id={role.id}").fetchone()
            if role_booster is not None:
                booster += role_booster[0]
        cur.execute(f"UPDATE user SET booster = {booster} WHERE id = {after.id}")
        db.commit()
        db.close()

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author == self.bot.user:
            return
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        ban_list = cur.execute(f"SELECT word FROM censored_words").fetchall()
        ban_list = [word for db_tuple in ban_list for word in db_tuple]
        for word in ban_list:
            if word in ctx.content.lower():
                db.close()
                embed = disnake.Embed(title="Warning",
                                      description=f"**Your message contains prohibited words, please do not write such messages.**",
                                      color=int("6e1313", 16))
                await ctx.reply(embed=embed, delete_after=5)
                await ctx.delete()
                return
        cur.execute(f"UPDATE user SET xp = xp + booster * {len(ctx.content)} WHERE id = {ctx.author.id}")
        db.commit()
        db.close()
        await self.level_up(ctx.author.id)

    @tasks.loop(seconds=5)
    async def check_voice(self):
        for member in self.bot.get_all_members():
            if member.voice is None:
                return
            await self.voice_reward(member)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            await self.voice_reward(member)
        else:
            return

    async def voice_reward(self, member):
        if member.voice is None or member.voice.deaf or member.voice.mute or member.voice.self_deaf or member.voice.suppress:
            return
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        cur.execute(f"UPDATE user SET xp = xp + (5 * booster) WHERE id = {member.id}")
        db.commit()
        db.close()

    async def level_up(self, id):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        current_xp = cur.execute(f"SELECT xp FROM user WHERE id = {id}").fetchone()[0]
        current_level = cur.execute(f"SELECT level FROM user WHERE id = {id}").fetchone()[0]
        needed_xp = cur.execute(f"SELECT xp FROM level_table WHERE level = {current_level}").fetchone()[0]
        if current_xp >= needed_xp:
            current_xp = current_xp - needed_xp
            gold_reward = cur.execute(f"SELECT gold FROM level_table WHERE level = {current_level}").fetchone()[0]
            cur.execute(f"UPDATE user SET xp = {current_xp} WHERE id = {id}").fetchone()
            cur.execute(f"UPDATE user SET level = {current_level + 1} WHERE id = {id}").fetchone()
            cur.execute(f"UPDATE user SET balance = balance + booster * {gold_reward} WHERE id = {id}").fetchone()
            db.commit()
            db.close()
        else:
            db.commit()
            db.close()
            return
        await self.level_up(id)

def setup(bot):
    bot.add_cog(Level(bot))