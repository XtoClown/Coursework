from config import token
import disnake
from disnake.ext import commands
import os
import sqlite3

bot = commands.Bot(command_prefix="!", intents=disnake.Intents.all(), test_guilds=[1230544156405792911])

@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready to work!")
    db = sqlite3.connect('Bot.db')
    cur = db.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS user(
                id INT,
                balance REAL,
                level INT,
                xp REAL,
                timeouts INT,
                mutes INT,
                warns INT,
                kicks INT,
                bans INT,
                booster REAL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS transaction_table(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_by INT,
                    amount REAL,
                    user_name TEXT,
                    transaction_to_who INT,
                    transaction_to_who_name TEXT,
                    transaction_datetime TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS role_table(
                        owner_id INT,
                        role_id INT,
                        role_name TEXT,
                        role_has TEXT,
                        role_booster REAL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS timeout(
                id INT,
                was_given_by INT,
                reason TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS ban(
                   id INT,
                   was_given_by INT,
                   reason TEXT,
                   user_name TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS mute(
                       id INT,
                       was_given_by INT,
                       reason TEXT,
                       unmute_time TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS kick(
                           id INT,
                           was_given_by INT,
                           reason TEXT,
                           user_name TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS temp_channel(
                           id INT,
                           created_by INT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS censored_words(
                               word TEXT,
                               added_by INT)""")
    for member in bot.get_all_members():
        if cur.execute(f"SELECT id FROM user WHERE id={member.id}").fetchone() is None:
            cur.execute(f"INSERT INTO user VALUES ({member.id}, 0, 1, 0, 0, 0, 0, 0, 0, 1)")
    db.commit()
    db.close()

@bot.event
async def on_member_join(member):
    db = sqlite3.connect('Bot.db')
    cur = db.cursor()
    if cur.execute(f"SELECT id FROM user WHERE id={member.id}").fetchone() is None:
        cur.execute(f"INSERT INTO user VALUES ({member.id}, 0, 1, 0, 0, 0, 0, 0, 0, 1)")
        db.commit()
    db.close()

import os
for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        bot.load_extension(f"cogs.{file[:-3]}")

bot.run(token)