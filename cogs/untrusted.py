import sqlite3

import disnake
from disnake.ext import commands

class VerifyModal(disnake.ui.Modal):
    def __init__(self, code):
        self.code = code
        components = [
            disnake.ui.TextInput(label="Enter code", placeholder=self.code, custom_id="code"),
        ]
        super().__init__(title="Verify", components=components, custom_id="verify_modal")

    async def callback(self, interaction: disnake.ModalInteraction):
        if self.code == int(interaction.text_values["code"]):
            db = sqlite3.connect("Bot.db")
            cur = db.cursor()
            role = cur.execute(f"SELECT * FROM untrusted_role").fetchone()
            if role is None:
                embed = disnake.Embed(title="Error",
                                      description=f"Untrusted role is not registered",
                                      color=int("78b3af", 16))
                await interaction.response.send_message(embed=embed,
                               ephemeral=True, delete_after=10)
                db.close()
                return
            role = interaction.guild.get_role(role[0])
            if role in interaction.author.roles:
                await interaction.author.remove_roles(role)
            embed = disnake.Embed(title="Verification completed",
                                  description=f"Congratulations! Verification has been successful and you now have access to the server channels",
                                  color=int("78b3af", 16))
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True, delete_after=10)
        else:
            embed = disnake.Embed(title="Verification failed",
                                  description=f"Unfortunately, you were not verified, please try again",
                                  color=int("78b3af", 16))
            await interaction.response.send_message(embed=embed,
                                                    ephemeral=True, delete_after=10)

class ButtonView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Verify", style=disnake.ButtonStyle.green, custom_id="button1")
    async def button1(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        import random
        code = random.randint(1000, 9999)
        await interaction.response.send_modal(VerifyModal(code))

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistents_view_added = False

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS untrusted_role(role_id INT)""")
        db.commit()
        db.close()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        role = cur.execute(f"SELECT * FROM untrusted_role").fetchone()
        if role is None:
            return
        role = member.guild.get_role(role[0])
        await member.add_roles(role)
        db.close()

    @commands.slash_command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_untrusted_role(self, interaction):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(f"SELECT * FROM untrusted_role").fetchone() is not None:
            embed = disnake.Embed(title="Error",
                                  description=f"Untrusted role is already registered",
                                  color=int("78b3af", 16))
            await interaction.response.send_message(embed=embed,
                       ephemeral=True, delete_after=10)
            db.close()
            return
        verify_role = await interaction.guild.create_role(name="Verify", reason="Untrusted role creation", color=int("3b3b3b", 16))
        embed = disnake.Embed(title="Verify Role",
                              description=f"Untrusted role has been create {verify_role.mention}",
                              color=int("78b3af", 16))
        await interaction.response.send_message(embed=embed,
                       ephemeral=True, delete_after=10)
        for channel in self.bot.get_all_channels():
            await channel.set_permissions(verify_role, view_channel=False)
        untrusted_channel = await interaction.guild.create_text_channel(name="Verification")
        if cur.execute("SELECT * FROM untrusted_role").fetchone() is None:
            cur.execute(f"INSERT INTO untrusted_role VALUES({verify_role.id})")
        else:
            cur.execute(f"UPDATE untrusted_role SET role_id = {verify_role.id}")
        db.commit()
        db.close()

    @commands.slash_command(hidden=True)
    async def verify(self, ctx):
        embed = disnake.Embed()
        embed.set_image(url="https://i.imgur.com/6zPN4Q7.jpeg")
        await ctx.send(embed=embed, view=ButtonView())

    @commands.Cog.listener()
    async def on_connect(self):
        if self.persistents_view_added:
            return

        self.bot.add_view(ButtonView(), message_id=...)

def setup(bot):
    bot.add_cog(Verify(bot))