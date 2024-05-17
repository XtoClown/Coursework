import disnake
from disnake.ext import commands
import sqlite3
import datetime

class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def stats(self, interaction):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        embed = disnake.Embed(title="Stats",
                              description=f"Info about user - {interaction.author.mention}",
                              color=int("52664e", 16))
        if hasattr(interaction.author.avatar, "url"): embed.set_thumbnail(url=interaction.author.avatar.url)
        current_level = cur.execute(f'SELECT level FROM user WHERE id = {interaction.author.id}').fetchone()[0]
        embed.add_field(name="Level",
                        value=f"User current level: {current_level}",
                        inline=False)
        current_xp = cur.execute(f'SELECT xp FROM user WHERE id = {interaction.author.id}').fetchone()[0]
        need_xp = cur.execute(f'SELECT xp FROM level_table WHERE level = {current_level}').fetchone()[0]
        embed.add_field(name="XP",
                        value=f"User current xp: {round(current_xp, 2)}/{round(need_xp, 2)}",
                        inline=False)
        embed.add_field(name="Balance",
                        value=f"User current balance: {cur.execute(f'SELECT balance FROM user WHERE id = {interaction.author.id}').fetchone()[0]}",
                        inline=False)
        embed.add_field(name="XP Booster",
                        value=f"User current xp booster: {cur.execute(f'SELECT booster FROM user WHERE id = {interaction.author.id}').fetchone()[0]}",
                        inline=False)
        appears_date = datetime.datetime.fromisoformat(f"{interaction.author.joined_at}"[:19]).strftime("%H:%M:%S %d.%m.%Y")
        embed.add_field(name="Server appears date",
                        value=f"{appears_date}",
                        inline=False)
        registration_date = datetime.datetime.fromisoformat(f"{interaction.author.created_at}"[:19]).strftime("%H:%M:%S %d.%m.%Y")
        embed.add_field(name="Discord registration date",
                        value=f"{registration_date}",
                        inline=False)
        embed.add_field(name="Mutes",
                        value=f"{cur.execute(f'SELECT mutes FROM user WHERE id = {interaction.author.id}').fetchone()[0]}",
                        inline=True)
        embed.add_field(name="Timeouts",
                        value=f"{cur.execute(f'SELECT timeouts FROM user WHERE id = {interaction.author.id}').fetchone()[0]}",
                        inline=True)
        embed.add_field(name="Bans",
                        value=f"{cur.execute(f'SELECT bans FROM user WHERE id = {interaction.author.id}').fetchone()[0]}",
                        inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=60)
        db.close()

    @commands.slash_command()
    async def transaction(self, interaction, member: disnake.Member, amount: float):
        if interaction.author.id == member.id:
            embed = disnake.Embed(title="Transaction failed",
                                  description="Why would you transfer money to yourself?",
                                  color=int("6d5675", 16))
            if hasattr(interaction.author.avatar, "url"): embed.set_thumbnail(url=interaction.author.avatar)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        current_balance = cur.execute(f"SELECT balance FROM user WHERE id = {interaction.author.id}").fetchone()[0]
        if current_balance < amount or amount < 0.1:
            embed = disnake.Embed(title="Transaction failed",
                                  description="Not enough money or invalid amount...",
                                  color=int("6d5675", 16))
            if hasattr(interaction.author.avatar, "url"): embed.set_thumbnail(url=interaction.author.avatar)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            cur.execute(f"UPDATE user set balance = balance - {amount} WHERE id = {interaction.author.id}").fetchone()
            cur.execute(f"UPDATE user set balance = balance + {amount} WHERE id = {member.id}").fetchone()
            current_time = datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")
            cur.execute(
                f"INSERT INTO transaction_table (transaction_by, amount, user_name, transaction_to_who, transaction_to_who_name, transaction_datetime) VALUES({interaction.author.id}, {amount}, '{interaction.author.name}', {member.id}, '{member.name}', '{current_time}')")
            db.commit()
            embed = disnake.Embed(title="Transaction succeeded",
                                  description=f"{interaction.author.mention} transferred **{amount}** money to {member.mention}",
                                  color=int("6d5675", 16))

            if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar)
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
        db.close()

    @commands.slash_command()
    async def transaction_list(self, interaction):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(f"SELECT * FROM transaction_table WHERE transaction_by = {interaction.author.id} or transaction_to_who = {interaction.author.id}").fetchone() is None:
            embed = disnake.Embed(title="None",
                                  description="Sorry, no transactions related to you were found",
                                  color=int("ffde4a", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
            db.close()
            return
        transaction_list = cur.execute(f"SELECT * FROM transaction_table WHERE transaction_by = {interaction.author.id} or transaction_to_who = {interaction.author.id}").fetchall()
        filtred_list = []
        for item in transaction_list:
            temp = []
            try:
                user = await self.bot.fetch_user(item[1])
            except Exception as ex:
                temp.append(item[3])
            else:
                temp.append(user)
            temp.append(item[2])
            try:
                user = await self.bot.fetch_user(item[4])
            except Exception as ex:
                temp.append(item[4])
            else:
                temp.append(user)
            filtred_list.append(tuple(temp))
        embed = disnake.Embed(title="Transaction List",
                              description="Information about all transactions related to your account",
                              color=int("ffde4a", 16))
        for item in filtred_list:
            transaction_by = f"**{item[0]}**" if type(item[0]) == str else item[0].mention
            amount = f"**{item[1]}**"
            transaction_recive = f"**{item[2]}**" if type(item[2]) == str else item[2].mention
            embed.add_field(name="",
                            value=f"{transaction_by} made a transaction of {amount} coins to {transaction_recive}",
                            inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=45)
        db.commit()
        db.close()

    @commands.slash_command(hidden=True)
    @commands.has_permissions(administrator=True)
    @commands.is_owner()
    async def owner_give_balance(self, interaction, member: disnake.Member, balance: float):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        cur.execute(f"UPDATE user SET balance = balance + {balance} WHERE id = {member.id}").fetchone()
        db.commit()
        db.close()
        embed = disnake.Embed(title="Owner add Money",
                              description=f"{balance} money has been added to user: {member.mention}",
                              color=994829)
        if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

    @commands.slash_command(hidden=True)
    @commands.has_permissions(administrator=True)
    @commands.is_owner()
    async def owner_give_xp(self, interaction, member: disnake.Member, xp: float):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        cur.execute(f"UPDATE user SET xp = xp + {xp} WHERE id = {member.id}").fetchone()
        db.commit()
        db.close()
        embed = disnake.Embed(title="Owner add Xp",
                              description=f"{xp} xp has been added to user: {member.mention}",
                              color=994829)
        if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

    @commands.slash_command(hidden=True)
    @commands.has_permissions(administrator=True)
    @commands.is_owner()
    async def owner_give_level(self, interaction, member: disnake.Member, level: int):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        cur.execute(f"UPDATE user SET level = level + {level} WHERE id = {member.id}").fetchone()
        db.commit()
        db.close()
        embed = disnake.Embed(title="Owner add Level",
                              description=f"{level} level's has been added to user: {member.mention}",
                              color=994829)
        if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)


def setup(bot):
    bot.add_cog(Statistics(bot))