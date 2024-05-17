import disnake
from disnake.ext import commands, tasks
import sqlite3

class Room(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS private_room_channel(channel_id INT)""")
        db.commit()
        db.close()
        self.check_if_empty.start()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel is not None:
            db = sqlite3.connect('Bot.db')
            cur = db.cursor()
            private_room_creation_channel = cur.execute(f"SELECT * FROM private_room_channel").fetchone()
            if private_room_creation_channel is not None and after.channel.id == private_room_creation_channel[0]:
                if cur.execute(f"SELECT * FROM temp_channel WHERE created_by={member.id}").fetchone() is None:
                    temp_channel = await member.guild.create_voice_channel(name=f"{member.name} Private Room")
                    cur.execute(f"INSERT INTO temp_channel VALUES({temp_channel.id}, {member.id})")
                    await member.move_to(temp_channel)
                    embed = disnake.Embed(title="Private room create",
                                          description=f"You create private room {temp_channel.mention}!",
                                          color=int("f0c584", 16))
                    embed.add_field(name="/lock_room", value=f"close the private room", inline=False)
                    embed.add_field(name="/open_room", value=f"open the private room", inline=False)
                    embed.add_field(name="/transfer_room", value=f"transfer a private room to another user", inline=False)
                    embed.add_field(name="/rename_room", value=f"rename the private room", inline=False)
                    embed.add_field(name="/delete_room", value=f"delete the private room", inline=False)
                    if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
                    await member.send(embed=embed, delete_after=60)
            db.commit()
            db.close()

    @tasks.loop(seconds=1)
    async def check_if_empty(self):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        for channel in self.bot.get_all_channels():
            if cur.execute(f"SELECT * FROM temp_channel WHERE id={channel.id}").fetchone() is not None:
                temp_voice = disnake.utils.get(channel.guild.voice_channels, id=channel.id)
                if len(temp_voice.members) == 0:
                    cur.execute(f"DELETE FROM temp_channel WHERE id={channel.id}").fetchone()
                    await channel.delete()
        db.commit()
        db.close()

    @commands.slash_command()
    async def lock_room(self, interaction):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        temp_room = cur.execute(f"SELECT id FROM temp_channel WHERE created_by={interaction.author.id}").fetchone()
        if temp_room is None:
            embed = disnake.Embed(title="Error",
                                  description=f"You don't have a private voice channel",
                                  color=int("f0c584", 16))
            if hasattr(interaction.author.avatar, "url"): embed.set_thumbnail(url=interaction.author.avatar.url)
            await interaction.send(embed=embed, ephemeral=True, delete_after=7)
            db.close()
            return
        temp_room = disnake.utils.get(interaction.guild.voice_channels, id=temp_room[0])
        for member in interaction.guild.members:
            await temp_room.set_permissions(member, connect=False)
        embed = disnake.Embed(title="Room closed",
                              description=f"{temp_room.mention} was closed successfully",
                              color=int("f0c584", 16))
        if hasattr(interaction.author.avatar, "url"): embed.set_thumbnail(url=interaction.author.avatar.url)
        await interaction.send(embed=embed, ephemeral=True, delete_after=7)
        db.close()

    @commands.slash_command()
    async def open_room(self, interaction):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        temp_room = cur.execute(f"SELECT id FROM temp_channel WHERE created_by={interaction.author.id}").fetchone()
        if temp_room is None:
            embed = disnake.Embed(title="Error",
                                  description=f"You don't have a private voice channel",
                              color=int("f0c584", 16))
            if hasattr(interaction.author.avatar, "url"): embed.set_thumbnail(url=interaction.author.avatar.url)
            await interaction.send(embed=embed, ephemeral=True, delete_after=7)
            db.close()
            return
        temp_room = disnake.utils.get(interaction.guild.voice_channels, id=temp_room[0])
        for member in interaction.guild.members:
            await temp_room.set_permissions(member, connect=True)
        embed = disnake.Embed(title="Room opened",
                              description=f"{temp_room.mention} was opened successfully",
                              color=int("f0c584", 16))
        if hasattr(interaction.author.avatar, "url"): embed.set_thumbnail(url=interaction.author.avatar.url)
        await interaction.send(embed=embed, ephemeral=True, delete_after=7)
        db.close()

    @commands.slash_command()
    async def transfer_room(self, interaction, member: disnake.Member):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        temp_room = cur.execute(f"SELECT id FROM temp_channel WHERE created_by={interaction.author.id}").fetchone()
        if temp_room is None:
            embed = disnake.Embed(title="Error",
                                  description=f"You don't have a private voice channel",
                              color=int("f0c584", 16))
            if hasattr(interaction.author.avatar, "url"): embed.set_thumbnail(url=interaction.author.avatar.url)
            await interaction.send(embed=embed, ephemeral=True, delete_after=7)
            db.close()
            return
        temp_room = disnake.utils.get(interaction.guild.voice_channels, id=temp_room[0])
        if member not in temp_room.members:
            embed = disnake.Embed(title="Error",
                                  description=f"Member **{member.mention}** is not in this voice channel",
                              color=int("f0c584", 16))
            if hasattr(interaction.author.avatar, "url"): embed.set_thumbnail(url=interaction.author.avatar.url)
            await interaction.send(embed=embed, ephemeral=True, delete_after=7)
            db.close()
            return
        embed = disnake.Embed(title="Leadership transferred",
                              description=f"Leadership of room **{temp_room.mention}** was transferred successfully to {member.mention}",
                              color=int("f0c584", 16))
        if hasattr(member.avatar, "url"): embed.set_thumbnail(url=member.avatar.url)
        await interaction.send(embed=embed, ephemeral=True, delete_after=7)
        cur.execute(f"UPDATE temp_channel SET created_by={member.id} WHERE id={temp_room.id}")
        db.commit()
        db.close()

    @commands.slash_command()
    async def rename_room(self, interaction, name: str):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        temp_room = cur.execute(f"SELECT id FROM temp_channel WHERE created_by={interaction.author.id}").fetchone()
        if temp_room is None:
            embed = disnake.Embed(title="Error",
                                  description=f"You don't have a private voice channel",
                                  color=int("f0c584", 16))
            if hasattr(interaction.author.avatar, "url"): embed.set_thumbnail(url=interaction.author.avatar.url)
            await interaction.send(embed=embed, ephemeral=True, delete_after=7)
            db.close()
            return
        temp_room = disnake.utils.get(interaction.guild.voice_channels, id=temp_room[0])
        await temp_room.edit(name=name)
        embed = disnake.Embed(title="Room renamed",
                              description=f"{temp_room.mention} was renamed successfully",
                              color=int("f0c584", 16))
        if hasattr(interaction.author.avatar, "url"): embed.set_thumbnail(url=interaction.author.avatar.url)
        await interaction.send(embed=embed, ephemeral=True, delete_after=7)
        db.close()

    @commands.slash_command()
    async def delete_room(self, interaction):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        temp_room = cur.execute(f"SELECT id FROM temp_channel WHERE created_by={interaction.author.id}").fetchone()
        if temp_room is None:
            embed = disnake.Embed(title="Error",
                                  description=f"You don't have a private voice channel",
                                  color=int("f0c584", 16))
            if hasattr(interaction.author.avatar, "url"): embed.set_thumbnail(url=interaction.author.avatar.url)
            await interaction.send(embed=embed, ephemeral=True, delete_after=7)
            db.close()
            return
        temp_room = disnake.utils.get(interaction.guild.voice_channels, id=temp_room[0])
        embed = disnake.Embed(title="Room delete",
                              description=f"{temp_room.mention} was deleted successfully",
                              color=int("f0c584", 16))
        if hasattr(interaction.author.avatar, "url"): embed.set_thumbnail(url=interaction.author.avatar.url)
        await interaction.send(embed=embed, ephemeral=True, delete_after=7)
        cur.execute(f"DELETE FROM temp_channel WHERE id={temp_room.id}").fetchone()
        await temp_room.delete()
        db.commit()
        db.close()

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def set_private_room_channel(self, ctx, channel: disnake.VoiceChannel):
        db = sqlite3.connect('Bot.db')
        cur = db.cursor()
        if cur.execute(f"SELECT * FROM private_room_channel WHERE channel_id = {channel.id}").fetchone() is not None:
            embed = disnake.Embed(title="Error",
                                  description=f"Channel {channel.mention} is already a **\"private-room-creation-channel\"**",
                                  color=int("f0c584", 16))
            await ctx.send(embed=embed, ephemeral=True, delete_after=10)
            db.commit()
            db.close()
            return
        embed = disnake.Embed(title="Successful",
                              description=f"Private room creation channel has been set to {channel.mention}",
                              color=int("f0c584", 16))
        await ctx.send(embed=embed, ephemeral=True, delete_after=10)
        if cur.execute("SELECT * FROM private_room_channel").fetchone() is None:
            cur.execute(f"INSERT INTO private_room_channel VALUES({channel.id})")
        else:
            room = disnake.utils.get(ctx.guild.voice_channels, id=channel.id)
            await room.edit(name=f"Create Private Room")
            cur.execute(f"UPDATE private_room_channel SET channel_id = {channel.id}")
        db.commit()
        db.close()

def setup(bot):
    bot.add_cog(Room(bot))