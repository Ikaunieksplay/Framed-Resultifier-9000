import json
import os
import asyncio
from datetime import datetime

import discord
from discord.ext.commands import Bot
from discord.ext import commands, tasks

intents = discord.Intents.all()

# Create Bot object, give all intents.
bot = discord.ext.commands.Bot(intents=intents)

# list of channels bot will react to (copy channel ids and add it)
# add this to use:
# if !(message.channel.id in allowedChannels):
#   return
# Currently Ikaun's bot testing server general, insert your own ( ͡° ͜ʖ ͡°)
allowedChannels = [430333455566503940]

# Currently Ikaun's bot testing server, insert your own ( ͡° ͜ʖ ͡°)
allowedServers = [430333455566503937]


@bot.event
async def on_ready():
    print("Bot is ready")


@bot.event
async def on_message(message):
    # Checks if message channel ID is in list of approved channels.
    if not(message.channel.id in allowedChannels):
        return

    if "🎥" in message.content:
        # Get score from current message.
        not_score = message.content.count("🟥")
        score = 7 - not_score
        print(f"Score detected! Points: {score}")

        # Get current user and add to players if new.
        current_user = message.author
        await join_game(current_user)

        # get list of all users
        users = await load_stats()

        # Display score, increment points for user
        await message.reply(f"Score detected! {score} points added to {current_user}")
        users[str(current_user.id)]["points"] += score

        await save_stats(users)

    await bot.process_commands(message)


@bot.slash_command(guild_ids=allowedServers, name="stats", description="Shows how many points you have")
async def stats(ctx):
    await join_game(ctx.author)
    user = ctx.author
    users = await load_stats()

    points_amt = users[str(user.id)]["points"]

    em = discord.Embed(
        title=f"{ctx.author.name}'s stats", color=discord.Color(0xF20000))
    em.add_field(name="Points this week", value=points_amt)
    await ctx.respond(embed=em)


# test command please ignore
@bot.slash_command(guild_ids=allowedServers, description="test command please ignore")
async def beg(ctx):
    await join_game(ctx.author)
    user = ctx.author
    users = await load_stats()

    earnings = int(50)

    await ctx.respond(f"50 points added!")

    users[str(user.id)]["points"] += earnings

    await save_stats(users)


@bot.slash_command(guild_ids=allowedServers, name="leaderboard", description="See the current Top 10 guessers")
async def leaderboard(ctx, x=10):
    """
    Create leaderboard and create embedded text to display it.
    TODO Add a thing that replaces the leaderboard with some text if no one has scored yet? Getting something like https://imgur.com/YVUZbur is just silly
    :param ctx:
    :param x: Number of leaders to display
    :return:
    """
    users = await load_stats()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["points"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total, reverse=True)

    em = discord.Embed(
        title=f"Top {x} best guessers this week!", color=discord.Color(0xF20000))

    index = 1

    for amt in total:
        id_ = leader_board[amt]
        member = await bot.fetch_user(id_)
        name = member.name
        em.add_field(name=f"{index}. {name}", value=f"{amt}",  inline=False)
        if index == x:
            break
        else:
            index += 1

    await ctx.respond(embed=em)


@bot.slash_command(guild_ids=allowedServers)
async def clear_stats(ctx):
    """
    Display weekly results and clear stats.
    ctx parameter unused... wat do?
    """
    # ikaun - it freaks out if ctx is not there so i think its best to just add it without actually using it? idk works for me
    """
    :param ctx:
    :return:
    """
    # channel_id = 600400648969650186  # NetflixAndChill
    # ikauns testing channel, insert your own ( ͡° ͜ʖ ͡°)
    channel_id = 430333455566503940
    channel = bot.get_channel(channel_id)
    await ctx.respond("Week over! Here are the final results for this week!")
    x = 10
    users = await load_stats()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["points"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total, reverse=True)

    em = discord.Embed(title=f"{x} best guessers!",
                       color=discord.Color(0xF20000))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = await bot.fetch_user(id_)
        name = member.name
        em.add_field(name=f"{index}. {name}", value=f"{amt}",  inline=False)
        if index == x:
            break
        else:
            index += 1

    await channel.send(embed=em)
    await channel.send("Erasing data....")

    data = await load_stats()

    for key in data:
        data[key]["points"] = 0

    await save_stats(data)

    await channel.send("New week started! Have fun guessing!")


@tasks.loop(minutes=60.0)
async def task():
    """
    Runs clear_stats() once a week on Monday.
    :return:
    """
    if datetime.now().day == 0 and datetime.now().hour == 0:
        await clear_stats()


async def join_game(user):
    """
    Add user to running stats.
    :param user:
    :return: Boolean showing whether user exists already (False) or has been added (True)
    """
    users = await load_stats()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {"points": 0}

    await save_stats(users)
    return True


async def load_stats():
    """
    Gets stats from JSON file and return JSON object.
    :return: dictionary of current participants, scores, and other stats.
    """
    # TODO Should be placed into a try/except statement.
    with open("mainstats.json", "r") as f:
        users = json.load(f)
    return users


async def save_stats(users):
    """
    Save user stats as JSON file.
    :param users: dict of users and info.
    :return:
    """
    # TODO Should be placed into a try/except statement.
    with open("mainstats.json", "w") as f:
        json.dump(users, f)


bot.run(os.getenv('BOT_TOKEN'))  # insert your own bot token ( ͡° ͜ʖ ͡°)
