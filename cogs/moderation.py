import disnake
from disnake.ext import commands
import sqlite3

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS censorship_permission(role_id INT, gives_by INT, gives_by_name  TEXT)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS mute_permission(role_id INT, gives_by INT, gives_by_name  TEXT)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS timeout_permission(role_id INT, gives_by INT, gives_by_name  TEXT)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS kick_permission(role_id INT, gives_by INT, gives_by_name  TEXT)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS ban_permission(role_id INT, gives_by INT, gives_by_name  TEXT)""")
        db.commit()
        db.close()

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def add_access_to_censorship(self, interaction, role: disnake.Role):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(
                f"SELECT * FROM censorship_permission WHERE role_id={role.id}").fetchone() is not None or role.name == "Bot":
            embed = disnake.Embed(title="Error",
                                  description=f"Role {role.mention} is already have a censorship permission",
                                  color=int("911d46", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        embed = disnake.Embed(title="Permission set",
                              description=f"Role {role.mention} now have a censorship permission",
                              color=int("911d46", 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        cur.execute(
            f"INSERT INTO censorship_permission VALUES({role.id}, {interaction.author.id}, '{interaction.author.name}')").fetchone()
        db.commit()
        db.close()

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def remove_access_to_censorship(self, interaction, role: disnake.Role):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(
                f"SELECT * FROM censorship_permission WHERE role_id={role.id}").fetchone() is None or role.name == "Bot":
            embed = disnake.Embed(title="Error",
                                  description=f"Role {role.mention} don't have a censorship permission",
                                  color=int("911d46", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        embed = disnake.Embed(title="Permission remove",
                              description=f"Role {role.mention} now don't have a censorship permission",
                              color=int("911d46", 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        cur.execute(f"DELETE FROM censorship_permission WHERE role_id={role.id}").fetchone()
        db.commit()
        db.close()

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def add_access_to_mute(self, interaction, role: disnake.Role):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(f"SELECT * FROM mute_permission WHERE role_id={role.id}").fetchone() is not None or role.name == "Bot":
            embed = disnake.Embed(title="Error",
                                  description=f"Role {role.mention} is already have a mute permission",
                                  color=int("911d46", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        embed = disnake.Embed(title="Permission set",
                              description=f"Role {role.mention} now have a mute permission",
                              color=int("911d46", 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        cur.execute(f"INSERT INTO mute_permission VALUES({role.id}, {interaction.author.id}, '{interaction.author.name}')").fetchone()
        db.commit()
        db.close()

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def remove_access_to_mute(self, interaction, role: disnake.Role):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(
                f"SELECT * FROM mute_permission WHERE role_id={role.id}").fetchone() is None or role.name == "Bot":
            embed = disnake.Embed(title="Error",
                                  description=f"Role {role.mention} don't have a mute permission",
                                  color=int("911d46", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        embed = disnake.Embed(title="Permission remove",
                              description=f"Role {role.mention} now don't have a mute permission",
                              color=int("911d46", 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        cur.execute(f"DELETE FROM mute_permission WHERE role_id={role.id}").fetchone()
        db.commit()
        db.close()

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def add_access_to_timeout(self, interaction, role: disnake.Role):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(
                f"SELECT * FROM timeout_permission WHERE role_id={role.id}").fetchone() is not None or role.name == "Bot":
            embed = disnake.Embed(title="Error",
                                  description=f"Role {role.mention} is already have a timeout permission",
                                  color=int("911d46", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        embed = disnake.Embed(title="Permission set",
                              description=f"Role {role.mention} now have a timeout permission",
                              color=int("911d46", 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        cur.execute(
            f"INSERT INTO timeout_permission VALUES({role.id}, {interaction.author.id}, '{interaction.author.name}')").fetchone()
        db.commit()
        db.close()

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def remove_access_to_timeout(self, interaction, role: disnake.Role):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(
                f"SELECT * FROM timeout_permission WHERE role_id={role.id}").fetchone() is None or role.name == "Bot":
            embed = disnake.Embed(title="Error",
                                  description=f"Role {role.mention} don't have a timeout permission",
                                  color=int("911d46", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        embed = disnake.Embed(title="Permission remove",
                              description=f"Role {role.mention} now don't have a timeout permission",
                              color=int("911d46", 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        cur.execute(f"DELETE FROM timeout_permission WHERE role_id={role.id}").fetchone()
        db.commit()
        db.close()

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def add_access_to_kick(self, interaction, role: disnake.Role):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(
                f"SELECT * FROM kick_permission WHERE role_id={role.id}").fetchone() is not None or role.name == "Bot":
            embed = disnake.Embed(title="Error",
                                  description=f"Role {role.mention} is already have a kick permission",
                                  color=int("911d46", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        embed = disnake.Embed(title="Permission set",
                              description=f"Role {role.mention} now have a kick permission",
                              color=int("911d46", 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        cur.execute(
            f"INSERT INTO kick_permission VALUES({role.id}, {interaction.author.id}, '{interaction.author.name}')").fetchone()
        db.commit()
        db.close()

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def remove_access_to_kick(self, interaction, role: disnake.Role):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(
                f"SELECT * FROM kick_permission WHERE role_id={role.id}").fetchone() is None or role.name == "Bot":
            embed = disnake.Embed(title="Error",
                                  description=f"Role {role.mention} don't have a kick permission",
                                  color=int("911d46", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        embed = disnake.Embed(title="Permission remove",
                              description=f"Role {role.mention} now don't have a kick permission",
                              color=int("911d46", 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        cur.execute(f"DELETE FROM kick_permission WHERE role_id={role.id}").fetchone()
        db.commit()
        db.close()

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def add_access_to_ban(self, interaction, role: disnake.Role):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(
                f"SELECT * FROM ban_permission WHERE role_id={role.id}").fetchone() is not None or role.name == "Bot":
            embed = disnake.Embed(title="Error",
                                  description=f"Role {role.mention} is already ban a kick permission",
                                  color=int("911d46", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        embed = disnake.Embed(title="Permission set",
                              description=f"Role {role.mention} now have a ban permission",
                              color=int("911d46", 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        cur.execute(
            f"INSERT INTO ban_permission VALUES({role.id}, {interaction.author.id}, '{interaction.author.name}')").fetchone()
        db.commit()
        db.close()

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def remove_access_to_ban(self, interaction, role: disnake.Role):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(
                f"SELECT * FROM ban_permission WHERE role_id={role.id}").fetchone() is None or role.name == "Bot":
            embed = disnake.Embed(title="Error",
                                  description=f"Role {role.mention} don't have a ban permission",
                                  color=int("911d46", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        embed = disnake.Embed(title="Permission remove",
                              description=f"Role {role.mention} now don't have a ban permission",
                              color=int("911d46", 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        cur.execute(f"DELETE FROM ban_permission WHERE role_id={role.id}").fetchone()
        db.commit()
        db.close()

def setup(bot):
    bot.add_cog(Moderation(bot))