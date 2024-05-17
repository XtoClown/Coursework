import disnake
from disnake.ext import commands
import sqlite3
import re

class ChangeName(disnake.ui.Modal):
    def __init__(self, role):
        components = [
            disnake.ui.TextInput(label="Role name",
                                 placeholder="Enter a role name",
                                 custom_id="role_name",
                                 value=role.name),
        ]
        self.role = role
        super().__init__(title="Change role name", components=components, custom_id="change_role_modal")

    async def callback(self, interaction: disnake.ModalInteraction):
        db = sqlite3.connect("Bot.db")
        cur = db.cursor()
        arr = [key[1] for key in interaction.text_values.items()]
        if cur.execute(f"SELECT * FROM role_table WHERE role_name = '{arr[0]}'").fetchone() is not None:
            db.close()
            embed = disnake.Embed(title="Error",
                                  description="Role with this name already exists",
                                  colour=int("5b5182", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            return
        embed = disnake.Embed(title="Role name changed",
                              description="Role name successfully changed",
                              colour=int("5b5182", 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        cur.execute(f"UPDATE role_table SET role_name = '{arr[0]}' WHERE role_id = '{self.role.id}'").fetchone()
        await self.role.edit(name=arr[0])
        db.commit()
        db.close()

class ChangeColor(disnake.ui.Modal):
    def __init__(self, role):
        components = [
            disnake.ui.TextInput(label="Role color",
                                 placeholder="Enter a role color",
                                 custom_id="role_color",
                                 value=f"{role.color}"),
        ]
        self.role = role
        super().__init__(title="Change role name", components=components, custom_id="change_role_modal")

    async def callback(self, interaction: disnake.ModalInteraction):
        arr = [key[1] for key in interaction.text_values.items()]
        try:
            int(arr[0][1:7], 16)
        except Exception as ex:
            arr[0] = f"{self.role.color}"[1:7]
            embed = disnake.Embed(title="Error",
                                  description="Incorrect color entered",
                                  colour=int("5b5182", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            return
        else:
            arr[0] = arr[0][1:7]
            await self.role.edit(color=int(arr[0], 16))
            embed = disnake.Embed(title="Role color changed",
                                  description="Role color successfully changed",
                                  colour=int(arr[0], 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            return

class ChangeBooster(disnake.ui.Modal):
    def __init__(self, role):
        db = sqlite3.connect("Bot.db")
        cur = db.cursor()
        self.current_booster = cur.execute(f"SELECT role_booster FROM role_table WHERE role_id = {role.id}").fetchone()[0]
        db.close()
        components = [
            disnake.ui.TextInput(label="Role booster",
                                 placeholder="Enter a role booster",
                                 custom_id="role_name",
                                 value=f"{self.current_booster}"),
        ]
        self.role = role
        super().__init__(title="Change role name", components=components, custom_id="change_role_modal")

    async def callback(self, interaction: disnake.ModalInteraction):
        arr = [key[1] for key in interaction.text_values.items()]
        arr[0] = self.current_booster if not bool(re.match(r'^\d+(\.\d+)?$', arr[0])) or  float(arr[0]) < self.current_booster else arr[0]
        change_booster_price = 0 if float(arr[0]) == self.current_booster else round(1000 * (float(arr[0]) - float(self.current_booster)), 2)
        if change_booster_price == 0:
            embed = disnake.Embed(title="Error",
                                  description="You are joking? Right?",
                                  colour=int("5b5182", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            return
        booster_increases = float(arr[0]) - float(self.current_booster)
        embed = disnake.Embed(title="Price",
                              description=f"The price of changing the role xp booster is **{change_booster_price}**",
                              colour=int("5b5182", 16))
        await interaction.send(embed=embed,
                               view=ChangeBoosterButton(self.role, change_booster_price, booster_increases),
                               ephemeral=True, delete_after=20)

class ChangeBoosterButton(disnake.ui.View):
    def __init__(self, role, change_booster_price, booster_increases):
        self.role = role
        self.change_booster_price = change_booster_price
        self.booster_increases = booster_increases
        super().__init__(timeout=None)

    @disnake.ui.button(label="Confirm", style=disnake.ButtonStyle.green, custom_id="confirm_change_booster")
    async def confirm_change_booster(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        db = sqlite3.connect("Bot.db")
        cur = db.cursor()
        current_balance = cur.execute(f"SELECT balance FROM user WHERE id = {interaction.author.id}").fetchone()[0]
        if self.change_booster_price > current_balance:
            embed = disnake.Embed(title="Error",
                                  description="Not enough money to increase the role booster",
                                  colour=int("5b5182", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        cur.execute(
            f"UPDATE user SET balance = {current_balance - self.change_booster_price} WHERE id = {interaction.author.id}").fetchone()
        cur.execute(
            f"UPDATE role_table SET role_booster = role_booster + {self.booster_increases} WHERE role_id = {self.role.id}").fetchone()
        embed = disnake.Embed(title="Role booster changed",
                              description="Role booster successfully changed",
                              colour=int("5b5182", 16))
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
        db.commit()
        db.close()

class ChangePosition(disnake.ui.View):
    def __init__(self, role, price, pos):
        self.role = role
        self.price = price
        self.pos = pos
        super().__init__(timeout=None)

    @disnake.ui.button(label="Change role position", style=disnake.ButtonStyle.green, custom_id="change_position")
    async def change_position(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        db = sqlite3.connect("Bot.db")
        cur = db.cursor()
        current_balance = cur.execute(f"SELECT balance FROM user WHERE id={interaction.author.id}").fetchone()[0]
        if current_balance < self.price:
            embed = disnake.Embed(title="Error",
                                  description="Not enough money to change role position",
                                  colour=int("5b5182", 16))
            await interaction.send(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        cur.execute(f"UPDATE user SET balance = {current_balance - self.price} WHERE id = {interaction.author.id}")
        await self.role.edit(position=self.pos)
        embed = disnake.Embed(title="Role position changed",
                              description="Role position successfully changed",
                              colour=int("5b5182", 16))
        await interaction.send(embed=embed, ephemeral=True, delete_after=10)
        db.commit()
        db.close()

class ChangeHoist(disnake.ui.View):
    def __init__(self, role, price):
        self.role = role
        self.price = price
        super().__init__(timeout=None)

    @disnake.ui.button(label="Confirm", style=disnake.ButtonStyle.green, custom_id="confirm_add_hoist")
    async def confirm_add_hoist(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        db = sqlite3.connect("Bot.db")
        cur = db.cursor()
        current_balance = cur.execute(f"SELECT balance FROM user WHERE id={interaction.author.id}").fetchone()[0]
        if current_balance < self.price:
            embed = disnake.Embed(title="Error",
                                  description="Not enough money to change role hoist",
                                  colour=int("5b5182", 16))
            await interaction.send(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        cur.execute(f"UPDATE user SET balance = {current_balance - self.price} WHERE id = {interaction.author.id}")
        await self.role.edit(hoist=not self.role.hoist)
        embed = disnake.Embed(title="Role hoist changed",
                              description="Role position successfully changed",
                              colour=int("5b5182", 16))
        await interaction.send(embed=embed, ephemeral=True, delete_after=10)
        db.commit()
        db.close()

class MyRoleButton(disnake.ui.View):
    def __init__(self, role):
        self.role = role
        super().__init__(timeout=None)

    @disnake.ui.button(label="Change role name", style=disnake.ButtonStyle.green, custom_id="change_name")
    async def change_name(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.response.send_modal(ChangeName(self.role))

    @disnake.ui.button(label="Change role color", style=disnake.ButtonStyle.green, custom_id="change_color")
    async def change_color(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.response.send_modal(ChangeColor(self.role))

    @disnake.ui.button(label="Change role booster", style=disnake.ButtonStyle.green, custom_id="change_booster")
    async def change_booster(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.response.send_modal(ChangeBooster(self.role))

    @disnake.ui.button(label="Change role position", style=disnake.ButtonStyle.green, custom_id="change_position")
    async def change_position(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        max_pos = max([role.position for role in interaction.author.roles])
        increase_price = (max_pos - self.role.position) * 100
        if increase_price <= 0:
            embed = disnake.Embed(title="Error",
                                  description="It is impossible to raise the role higher",
                                  colour=int("5b5182", 16))
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            return
        embed = disnake.Embed(title="Price",
                              description=f"The price of changing the role position is **{increase_price}**",
                              colour=int("5b5182", 16))
        await interaction.response.send_message(embed=embed,
                                                view=ChangePosition(self.role, increase_price, max_pos),
                                                ephemeral=True, delete_after=10)

    @disnake.ui.button(label="Change role hoist", style=disnake.ButtonStyle.green, custom_id="change_hoist")
    async def change_hoist(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        price = 7500
        embed = disnake.Embed(title="Price",
                              description=f"The price of changing the role hoist is **{price}**",
                              colour=int("5b5182", 16))
        await interaction.response.send_message(embed=embed,
                                                view=ChangeHoist(self.role, price),
                                                ephemeral=True, delete_after=10)

class MyRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistents_view_added = False

    @commands.slash_command()
    async def my_role(self, ctx, role: disnake.Role):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        role_booster = cur.execute(f"SELECT role_booster FROM role_table WHERE owner_id = {ctx.author.id} AND role_id = {role.id}").fetchone()
        if role_booster is None:
            embed = disnake.Embed(title="Error",
                                  description=f"You are not the owner of **{role.mention}** role",
                                  colour=int("5b5182", 16))
            await ctx.send(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        db.close()
        embed = disnake.Embed(title="My Role",
                              description=f"Info about youre role **{role.mention}**",
                              color=int('173b61', 16))
        embed.add_field(name="", value=f"Role name: **{role.name}**"
                        , inline=False)
        embed.add_field(name="", value=f"Role color: **{role.color}**"
                        , inline=False)
        embed.add_field(name="", value=f"Role booster: **{role_booster[0]}**"
                        , inline=False)
        if hasattr(ctx.author.avatar, "url"): embed.set_thumbnail(url=ctx.author.avatar.url)
        await ctx.send(embed=embed, ephemeral=True, view=MyRoleButton(role))

    @commands.slash_command()
    async def give_my_role(self, ctx, member: disnake.Member, role: disnake.Role):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        role_booster = cur.execute(
            f"SELECT role_booster FROM role_table WHERE owner_id = {ctx.author.id} AND role_id = {role.id}").fetchone()
        if role_booster is None:
            embed = disnake.Embed(title="Error",
                                  description=f"You are not the owner of **{role.mention}** role",
                                  colour=int("5b5182", 16))
            await ctx.send(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        elif member.global_name is None and member.display_name == self.bot.user.name and member.discriminator == self.bot.user.discriminator:
            embed = disnake.Embed(title="Error",
                                  description=f"It's a bot...",
                                  colour=int("5b5182", 16))
            await ctx.send(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        elif ctx.author.id == member.id and role in ctx.author.roles:
            embed = disnake.Embed(title="Error",
                                  description=f"You already own this role...",
                                  colour=int("5b5182", 16))
            await ctx.send(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        current_users = cur.execute(
            f"SELECT role_has FROM role_table WHERE owner_id = {ctx.author.id} AND role_id = {role.id}").fetchone()[0]
        if f"{member.id}" in current_users:
            embed = disnake.Embed(title="Error",
                                  description=f"User already own this role...",
                                  colour=int("5b5182", 16))
            await ctx.send(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        embed = disnake.Embed(title="Role assignment",
                              description=f"You are gave the role **{role.mention}** to the user **{member.mention}**",
                              color=int('173b61', 16))
        if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
        await member.add_roles(role)
        await ctx.send(embed=embed, ephemeral=True)
        current_users += f",{member.id}" if current_users != "" else f"{member.id}"
        cur.execute(f"UPDATE role_table SET role_has = '{current_users}' WHERE owner_id = {ctx.author.id} AND role_id = {role.id}").fetchone()
        db.commit()
        db.close()

    @commands.slash_command()
    async def remove_my_role(self, ctx, member: disnake.Member, role: disnake.Role):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        role_booster = cur.execute(
            f"SELECT role_booster FROM role_table WHERE owner_id = {ctx.author.id} AND role_id = {role.id}").fetchone()
        if role_booster is None:
            embed = disnake.Embed(title="Error",
                                  description=f"You are not the owner of **{role.mention}** role",
                                  colour=int("5b5182", 16))
            await ctx.send(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        elif member.global_name is None and member.display_name == self.bot.user.name and member.discriminator == self.bot.user.discriminator:
            embed = disnake.Embed(title="Error",
                                  description=f"It's a bot...",
                                  colour=int("5b5182", 16))
            await ctx.send(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        role_owner = cur.execute(
            f"SELECT owner_id FROM role_table WHERE owner_id = {ctx.author.id} AND role_id = {role.id}").fetchone()[0]
        current_users = cur.execute(
            f"SELECT role_has FROM role_table WHERE owner_id = {ctx.author.id} AND role_id = {role.id}").fetchone()[0]
        if f"{member.id}" not in current_users and member.id != role_owner:
            embed = disnake.Embed(title="Error",
                                  description=f"User doesn't have this role...",
                                  colour=int("5b5182", 16))
            await ctx.send(embed=embed, ephemeral=True, delete_after=10)
            db.close()
            return
        embed = disnake.Embed(title="Role remove",
                              description=f"You are remove the role **{role.mention}** from the user **{member.mention}**",
                              color=int('173b61', 16))
        if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
        await member.remove_roles(role)
        await ctx.send(embed=embed, ephemeral=True, delete_after=10)
        current_users = current_users.replace(f"{member.id},", "", 1) if current_users != f"{member.id}" else ""
        cur.execute(
            f"UPDATE role_table SET role_has = '{current_users}' WHERE owner_id = {ctx.author.id} AND role_id = {role.id}").fetchone()
        db.commit()
        db.close()

def setup(bot):
    bot.add_cog(MyRole(bot))