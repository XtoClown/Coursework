import disnake
from disnake.ext import commands, tasks
import sqlite3

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def permissions():
        async def predicate(ctx):
            db = sqlite3.connect('Bot.db')
            cur = db.cursor()
            for role in ctx.author.roles:
                if cur.execute(f"SELECT * FROM kick_permission WHERE role_id = {role.id}").fetchone() is not None or ctx.author.guild_permissions.administrator:
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
            if member and cur.execute(f"SELECT id FROM kick WHERE id={member.id}").fetchone() is not None:
                cur.execute(f"DELETE FROM kick WHERE id={member.id}")
                db.commit()
        db.close()

    @commands.slash_command(hidden=True, description="To kick a user")
    @permissions()
    async def kick(self, interaction, member: disnake.Member, *, reason):
        if member.global_name is not None and member.display_name != self.bot.user.name and member.discriminator != self.bot.user.discriminator:
            embed = disnake.Embed(title="Kick",
                                  description=f"{member.mention} was kicked by {interaction.user.mention} for reason: **{reason}**",
                                  color=9509145)
            if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            await member.send(embed=embed)
            await member.kick(reason=reason)
            db = sqlite3.connect('Bot.db')
            cur = db.cursor()
            cur.execute(f"INSERT INTO kick VALUES ({member.id}, {interaction.user.id}, \"{reason}\", \"{member.name}\")")
            cur.execute(f"UPDATE user SET kicks = kicks + 1 WHERE id = {member.id}")
            db.commit()
            db.close()
        else:
            embed = disnake.Embed(title="Error",
                                  description="It's a bot...",
                                  color=9509145)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

def setup (bot):
    bot.add_cog(Kick(bot))