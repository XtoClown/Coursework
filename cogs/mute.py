import disnake
from disnake.ext import commands, tasks
import sqlite3
import datetime

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def permissions():
        async def predicate(ctx):
            db = sqlite3.connect('Bot.db')
            cur = db.cursor()
            for role in ctx.author.roles:
                if cur.execute(f"SELECT * FROM mute_permission WHERE role_id = {role.id}").fetchone() is not None or ctx.author.guild_permissions.administrator:
                    db.close()
                    return True
            db.close()
            return False
        return commands.check(predicate)

    @tasks.loop(minutes=1)
    async def check_mute(self):
        for member in self.bot.get_all_members():
            db = sqlite3.connect('Bot.db')
            cur = db.cursor()
            if cur.execute(f"SELECT * FROM mute_role") is not None:
                try:
                    mute_role = disnake.utils.get(member.guild.roles,
                                                  id=(int(cur.execute(f"SELECT * FROM mute_role").fetchone()[0])))
                    unmute_time = datetime.datetime.strptime(
                        cur.execute(f"SELECT unmute_time FROM mute WHERE id={member.id}").fetchone()[0],
                        '%H:%M:%S %d.%m.%Y')
                except Exception as e:
                    pass
                else:
                    current_time = datetime.datetime.now()
                    if mute_role in member.roles:
                        for channel in self.bot.get_all_channels():
                            await channel.set_permissions(mute_role, read_messages=True, send_messages=False)
                        if unmute_time < current_time:
                            await member.remove_roles(mute_role)
                            embed = disnake.Embed(title="Unmute",
                                                  description=f"The time of mute has expired",
                                                  colour=1872984)
                            if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
                            await member.send(embed=embed)
                    else:
                        cur.execute(f"DELETE FROM mute WHERE id={member.id}")
                        db.commit()
                finally:
                    db.close()
            db.close()


    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS mute_role(role_id INT)""")
        db.commit()
        db.close()
        await self.check_mute.start()

    @commands.slash_command()
    @permissions()
    async def mute(self, interaction, member: disnake.Member, time: int, reason: str):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(f"SELECT * FROM mute_role").fetchone() is None:
            embed = disnake.Embed(title="Error",
                                  description="Mute role is not set",
                                  color=int("e0e0e0", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        unmute_time = datetime.datetime.now() + datetime.timedelta(minutes=time)
        unmute_time = unmute_time.strftime("%H:%M:%S %d.%m.%Y")
        embed = disnake.Embed(title="Mute",
                              description=f"{member.mention} got muted by {interaction.user.mention} for reason: **{reason}**, mute time: **{time} min**",
                              color=9509145)
        if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True,  delete_after=20)
        await member.send(embed=embed)
        await member.add_roles(disnake.utils.get(member.guild.roles, id=int(cur.execute(f"SELECT * FROM mute_role").fetchone()[0])))
        cur.execute(f"INSERT INTO mute VALUES({member.id}, {interaction.author.id}, '{reason}', '{unmute_time}')")
        cur.execute(f"UPDATE user SET mutes = mutes + 1 WHERE id = {member.id}")
        db.commit()
        db.close()

    @commands.slash_command()
    @permissions()
    async def unmute(self, interaction, member: disnake.Member, reason: str):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(f"SELECT * FROM mute WHERE id={member.id}").fetchone() is None:
            db.close()
            embed = disnake.Embed(title="Error",
                                  description=f"{member.mention} not muted",
                                  colour=1872984)
            if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            return
        was_given_by = interaction.guild.get_member(
            cur.execute(f"SELECT was_given_by FROM mute WHERE id={member.id}").fetchone()[0])
        mute_reason = cur.execute(f"SELECT reason FROM mute WHERE id={member.id}").fetchone()[0]
        embed = disnake.Embed(title="Mute canceled",
                              description=f"For {member.mention} the mute was canceled due to: **{reason}**",
                              colour=disnake.Color.green())
        if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
        embed.set_author(name=f"Mute was given by @{was_given_by.display_name} for reason: {mute_reason}",
                         icon_url=was_given_by.avatar.url if hasattr(was_given_by.avatar, "url") else None)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=20)
        await member.send(embed=embed)
        mute_role = disnake.utils.get(member.guild.roles,
                                      id=(int(cur.execute(f"SELECT * FROM mute_role").fetchone()[0])))
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
        cur.execute(f"DELETE FROM mute WHERE id={member.id}")
        cur.execute(f"UPDATE user SET mutes = mutes - 1 WHERE id = {member.id}")
        db.commit()
        db.close()

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def set_mute_role(self, ctx, role: disnake.Role):
        if role.name == "Bot":
            embed = disnake.Embed(title="Error",
                                  description=f"You can't set a **Bot role** as mute-role",
                                  colour=int("8f5999", 16))
            if hasattr(ctx.author.avatar, "url"): embed.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.send(embed=embed, ephemeral=True, delete_after=10)
            return
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(f"SELECT * FROM mute_role WHERE role_id = {role.id}").fetchone() is not None:
            embed = disnake.Embed(title="Error",
                                  description=f"Role {role.mention} is already a **\"mute-role\"**",
                                  colour=int("8f5999", 16))
            if hasattr(ctx.author.avatar, "url"): embed.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.send(embed=embed, ephemeral=True, delete_after=10)
            db.commit()
            db.close()
            return
        embed = disnake.Embed(title="Successful",
                              description=f"Mute role has been set to {role.mention}",
                              colour=int("8f5999", 16))
        if hasattr(ctx.author.avatar, "url"): embed.set_thumbnail(url=ctx.author.avatar.url)
        await ctx.send(embed=embed, ephemeral=True, delete_after=10)
        if cur.execute("SELECT * FROM mute_role").fetchone() is None:
            cur.execute(f"INSERT INTO mute_role VALUES({role.id})")
        else:
            cur.execute(f"UPDATE mute_role SET role_id = {role.id}")
        db.commit()
        db.close()

def setup(bot):
    bot.add_cog(Mute(bot))