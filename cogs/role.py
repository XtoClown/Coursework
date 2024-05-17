import re
import disnake
from disnake.ext import commands
import sqlite3

class RoleModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(label="Role name",
                                 placeholder="Enter a role name",
                                 custom_id="role_name"),
            disnake.ui.TextInput(label="Role color",
                                 placeholder="Enter a role color",
                                 custom_id="role_color"),
            disnake.ui.TextInput(label="Enter a role xp booster",
                                 placeholder="",
                                 custom_id="role_xp_booster",
                                 value=1),
        ]
        super().__init__(title="Buy a new role", components=components, custom_id="buy_role_modal")

    async def callback(self, interaction: disnake.ModalInteraction):
        arr = [key[1] for key in interaction.text_values.items()]
        arr[0] = "Generic Name" if arr[0] == "Bot" or arr[0] == "Admin" or arr[0] == "Administrator" else arr[0]
        arr[2] = 1 if not bool(re.match(r'^\d+(\.\d+)?$', arr[2])) or float(arr[2]) < 1 else arr[2]
        try:
            int(arr[1][1:7], 16)
        except Exception as ex:
            arr[1] = "ffffff"
        else:
            arr[1] = arr[1][1:7]
        role_price = 1000 if float(arr[2]) == 1 else 1000 + 1000 * (float(arr[2]) - 1)
        embed = disnake.Embed(title="Buy a new role",
                              description="**You want to buy a role that will have:**")
        embed.add_field(name="", value=f"Role name: **{arr[0]}**"
                        ,inline=False)
        embed.add_field(name="", value=f"Role color: **#{arr[1]}**"
                        , inline=False)
        embed.add_field(name="", value=f"Role booster: **{arr[2]}**"
                        , inline=False)
        embed.add_field(name=f"Total role price: {role_price}", value=f"", inline=False)
        view = RoleView(arr, role_price)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True, delete_after=30)

class RoleView(disnake.ui.View):
    def __init__(self, arr, role_price):
        self.arr = arr
        self.role_price = role_price
        super().__init__(timeout=None)

    @disnake.ui.button(label="Confirm creation", style=disnake.ButtonStyle.green, custom_id="button1")
    async def button1(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        current_balance = cur.execute(f"SELECT balance FROM user WHERE id = {interaction.author.id}").fetchone()[0]
        if current_balance < self.role_price:
            embed = disnake.Embed(title="Error",
                                  description="Not enough money to create role",
                                  colour=int('e6caa8', 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        elif cur.execute(f"SELECT * FROM role_table WHERE role_name = '{self.arr[0]}'").fetchone():
            embed = disnake.Embed(title="Error",
                                  description=f"Role with name **\"{self.arr[0]}\"** already exist",
                                  colour=int('e6caa8', 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        embed = disnake.Embed(title="New role created",
                              description=f"Role create successfully",
                              colour=int('e6caa8', 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        role = await interaction.guild.create_role(name=self.arr[0], color=int(self.arr[1], 16), mentionable=True,
                                                   reason="User bought the role")
        await interaction.user.add_roles(role)
        cur.execute(f"UPDATE user SET balance = balance - {self.role_price} WHERE id = {interaction.author.id}").fetchone()
        cur.execute(
            f"INSERT into role_table values({interaction.author.id}, {role.id}, '{self.arr[0]}', '', {round(float(self.arr[2]), 2)})").fetchone()
        booster = 1
        for user_role in interaction.author.roles:
            role_booster = cur.execute(f"SELECT role_booster FROM role_table WHERE role_id={user_role.id}").fetchone()
            if role_booster is not None:
                booster += role_booster[0]
        cur.execute(f"UPDATE user SET booster = {booster} WHERE id = {interaction.author.id}")
        db.commit()
        db.close()

    @disnake.ui.button(label="Cancel creation", style=disnake.ButtonStyle.green, custom_id="button2")
    async def button2(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        embed = disnake.Embed(title="Creationg canceled",
                              description=f"Role creation successfully canceled",
                              colour=int('e6caa8', 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)

class ButtonView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Create role", style=disnake.ButtonStyle.green, custom_id="button1")
    async def button1(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.response.send_modal(RoleModal())

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistents_view_added = False

    @commands.slash_command(hidden=True)
    async def create_role(self, ctx):
        embed = disnake.Embed(title="Create role info",
                              description="This team is for people who want to spend money to create a personal role for themselves on this discount server.",
                              color=int('e6caa8', 16))
        embed.add_field(name="Info about role creation:",
                        value="First of all, after clicking on the button below the post, a window will open where you will have to enter the **role name**, **role color**, and the desired **xp booster**"
                        ,inline=False)
        embed.add_field(name="Role name",
                        value="- is the name of the role that will be shown to all users"
                        ,inline=False)
        embed.add_field(name="Role color",
                        value="- is the color of the role, it must be entered in the \"HEX\" format. To find the color you want, just enter \"html palette\" and choose the color you like."
                        , inline=False)
        embed.add_field(name="Role booster",
                        value="- experience booster for a role is the number of experience points received per 1 character in a message or per 1 second in a voice channel. Each increase in this indicator by 0.01 increases the initial cost of the role by 1 percent. **If you do not want to increase this parameter, leave the default value in the field**."
                        , inline=False)
        embed.add_field(name="The cost of creating a role - 1000",
                        value="",
                        inline=True)
        await ctx.send(embed=embed, view=ButtonView(), ephemeral=True, delete_after=15)

    @commands.Cog.listener()
    async def on_connect(self):
        if self.persistents_view_added:
            return

        self.bot.add_view(ButtonView(), message_id=...)

def setup(bot):
    bot.add_cog(Role(bot))