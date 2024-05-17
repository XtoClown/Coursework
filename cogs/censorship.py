import disnake
from disnake.ext import commands
import sqlite3

class Censorship(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def permissions():
        async def predicate(ctx):
            db = sqlite3.connect('Bot.db')
            cur = db.cursor()
            for role in ctx.author.roles:
                if cur.execute(f"SELECT * FROM censorship_permission WHERE role_id = {role.id}").fetchone() is not None or ctx.author.guild_permissions.administrator:
                    db.close()
                    return True
            db.close()
            return False
        return commands.check(predicate)

    @commands.slash_command()
    @permissions()
    async def add_ban_word(self, interaction, word: str):
        db = sqlite3.connect("Bot.db")
        cur = db.cursor()
        word = word.lower()
        if cur.execute(f"SELECT * FROM censored_words WHERE word = '{word}'").fetchone() is not None:
            embed = disnake.Embed(title="Error",
                                  description="This word is already banned",
                                  color=int("579596", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        embed = disnake.Embed(title="Word Banned",
                              description=f"The word **{word}** has been successfully added to the list of banned words",
                              color=int("579596", 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        cur.execute(f"INSERT INTO censored_words VALUES('{word}', {interaction.author.id})").fetchone()
        db.commit()
        db.close()

    @commands.slash_command()
    @permissions()
    async def remove_ban_word(self, interaction, word: str):
        db = sqlite3.connect("Bot.db")
        cur = db.cursor()
        word = word.lower()
        if cur.execute(f"SELECT * FROM censored_words WHERE word = '{word}'").fetchone() is None:
            embed = disnake.Embed(title="Error",
                                  description="This word is not banned",
                                  color=int("579596", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        embed = disnake.Embed(title="Word Unbanned",
                              description=f"The word **{word}** has been successfully remove from the list of banned words",
                              color=int("579596", 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        cur.execute(f"DELETE FROM censored_words WHERE word = '{word}'").fetchone()
        db.commit()
        db.close()

def setup(bot):
    bot.add_cog(Censorship(bot))