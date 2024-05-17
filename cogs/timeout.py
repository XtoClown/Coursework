import disnake
from disnake.ext import commands, tasks
import datetime
import sqlite3

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def permissions():
        async def predicate(ctx):
            db = sqlite3.connect('Bot.db')
            cur = db.cursor()
            for role in ctx.author.roles:
                if cur.execute(f"SELECT * FROM timeout_permission WHERE role_id = {role.id}").fetchone() is not None or ctx.author.guild_permissions.administrator:
                    db.close()
                    return True
            db.close()
            return False
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        self.delete_from_db.start()

    @tasks.loop(minutes=1.0)
    async def delete_from_db(self):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        for member in self.bot.get_all_members():
            if member.current_timeout is None and cur.execute(f"SELECT id FROM timeout WHERE id={member.id}").fetchone() is not None:
                cur.execute(f"DELETE FROM timeout WHERE id={member.id}")
                db.commit()
        db.close()

    @commands.slash_command(hidden=True)
    @permissions()
    async def timeout(self, interaction, member: disnake.Member, time: str, *, reason: str):
        if member.global_name is not None and member.display_name != self.bot.user.name and member.discriminator != self.bot.user.discriminator:
            db = sqlite3.connect('Bot.db')
            cur = db.cursor()
            cur.execute(f"INSERT INTO timeout VALUES ({member.id}, {interaction.user.id}, \"{reason}\")")
            cur.execute(f"UPDATE user SET timeouts = timeouts + 1 WHERE id = {member.id}")
            db.commit()
            db.close()
            embed = disnake.Embed(title="Timeout",
                                  description=f"{member.mention} got a timeout by {interaction.user.mention} for reason: **{reason}**, timeout time: **{time} min**",
                                  color=9509145)
            if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
            time = datetime.datetime.now() + datetime.timedelta(minutes=int(time))
            await member.timeout(reason=reason, until=time)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            await member.send(embed=embed)
        else:
            embed = disnake.Embed(title="Error",
                                  description="It's a bot...",
                                  color=9509145)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

    @commands.slash_command(hidden=True)
    @permissions()
    async def untimeout(self, interaction, member: disnake.Member, reason: str):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(f"SELECT * FROM timeout WHERE id={member.id}").fetchone():
            was_given_by = interaction.guild.get_member(cur.execute(f"SELECT was_given_by FROM timeout WHERE id={member.id}").fetchone()[0])
            timeout_reason = cur.execute(f"SELECT reason FROM timeout WHERE id={member.id}").fetchone()[0]
            cur.execute(f"UPDATE user SET timeouts = timeouts - 1 WHERE id = {member.id}")
            db.commit()
            db.close()
            await member.timeout(reason=reason, until=None)
            embed = disnake.Embed(title="Timeout canceled",
                                  description=f"For {member.mention} the timeout was canceled due to: **{reason}**",
                                  colour=disnake.Color.green())
            if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
            embed.set_author(name=f"Timeout was given by @{was_given_by.display_name} for reason: {timeout_reason}",
                             icon_url=was_given_by.avatar.url if hasattr(was_given_by.avatar, "url") else None)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            await member.send(embed=embed)
        else:
            db.close()
            embed = disnake.Embed(title="Error",
                                  description=f"{member.mention} not in timeout",
                                  colour=1872984)
            if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            return

def setup(bot):
    bot.add_cog(Timeout(bot))
