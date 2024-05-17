import disnake
from disnake.ext import commands, tasks
import sqlite3

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def permissions():
        async def predicate(ctx):
            db = sqlite3.connect('Bot.db')
            cur = db.cursor()
            for role in ctx.author.roles:
                if cur.execute(f"SELECT * FROM ban_permission WHERE role_id = {role.id}").fetchone() is not None or ctx.author.guild_permissions.administrator:
                    db.close()
                    return True
            db.close()
            return False
        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_ready(self):
        self.delete_from_db.start()

    @tasks.loop(hours=24.0)
    async def delete_from_db(self):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        for member in self.bot.get_all_members():
            if member and cur.execute(f"SELECT id FROM ban WHERE id={member.id}").fetchone() is not None:
                cur.execute(f"DELETE FROM ban WHERE id={member.id}")
                db.commit()
        db.close()

    @commands.slash_command(hidden=True)
    @permissions()
    async def ban(self, interaction, member: disnake.Member, reason):
        if member.global_name is not None and member.display_name != self.bot.user.name and member.discriminator != self.bot.user.discriminator:
            db = sqlite3.connect('Bot.db')
            cur = db.cursor()
            cur.execute(f"INSERT INTO ban VALUES ({member.id}, {interaction.user.id}, \"{reason}\", \"{member.name}\")")
            cur.execute(f"UPDATE user SET bans = bans + 1 WHERE id = {member.id}")
            db.commit()
            db.close()
            embed = disnake.Embed(title="Ban",
                                  description=f"{member.mention} was banned by {interaction.user.mention} for reason: **{reason}**",
                                  color=9509145)
            if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            await member.send(embed=embed)
            await member.ban(reason=reason)
        else:
            embed = disnake.Embed(title="Error",
                                  description="It's a bot...",
                                  color=9509145)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

    @commands.slash_command(hidden=True)
    @permissions()
    async def unban(self, interaction, member: str, reason: str):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(f"SELECT * FROM ban WHERE user_name=\"{member}\"").fetchone() is not None:
            member = await self.bot.fetch_user(cur.execute(f"SELECT id FROM ban WHERE user_name=\"{member}\"").fetchone()[0])
            was_given_by = interaction.guild.get_member(cur.execute(f"SELECT was_given_by FROM ban WHERE id={member.id}").fetchone()[0])
            ban_reason = cur.execute(f"SELECT reason FROM ban WHERE id={member.id}").fetchone()[0]
            cur.execute(f"UPDATE user SET bans = bans - 1 WHERE id = {member.id}")
            cur.execute(f"DELETE FROM ban WHERE id={member.id}")
            db.commit()
            db.close()
            await interaction.guild.unban(member)
            embed = disnake.Embed(title="Unbanned",
                                  description=f"For {member.mention} the ban was canceled due to: **{reason}**",
                                  colour=disnake.Color.green())
            if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
            embed.set_author(name=f"Ban was given by @{was_given_by.display_name} for reason: {ban_reason}",
                             icon_url=was_given_by.avatar.url if hasattr(was_given_by.avatar, "url") else None)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        else:
            db.close()
            embed = disnake.Embed(title="Error",
                                  description=f"@{member} not banned",
                                  colour=1872984)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

def setup(bot):
    bot.add_cog(Ban(bot))