import json
import os
import asyncio
from datetime import datetime

import discord
from discord.ext.commands import Bot
from discord.ext import commands, tasks

intents = discord.Intents.all()

# Create Bot object, give all intents.
bot = discord.ext.commands.Bot(intents=intents, command_prefix="/")

# list of channels bot will react to (copy channel ids and add it)
# add this to use:
# if !(message.channel.id in allowedChannels):
#   return
# Currently #netflix-n-chill, insert your own ( ͡° ͜ʖ ͡°)
allowedChannels = [600400648969650186]

# Currently bardaks, insert your own ( ͡° ͜ʖ ͡°)
allowedServers = [568517834498637836]


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

        # get list of all users
        users = await load_stats()

        # Get current user and add to players if new.
        current_user = message.author
        await join_game(current_user, users)

        # Display score, increment points for user
        users[str(current_user.id)]["points"] += score
        await message.reply(f"Score detected! {score} points added to {current_user}")

        await save_stats(users)

    await bot.process_commands(message)


@bot.slash_command(guild_ids=allowedServers, name="stats", description="Shows how many points you have")
async def stats(ctx):
    users = await load_stats()
    user = ctx.author
    await join_game(user, users)

    points_amt = users[str(user.id)]["points"]

    em = discord.Embed(
        title=f"{ctx.author.name}'s stats", color=discord.Color(0xF20000))
    em.add_field(name="Points this week", value=points_amt)
    await ctx.respond(embed=em)


# test command please ignore
@bot.slash_command(guild_ids=allowedServers, description="test command please ignore")
async def beg(ctx):
    users = await load_stats()
    user = ctx.author
    await join_game(user, users)

    earnings = int(50)

    await ctx.respond(f"50 points added!")

    users[str(user.id)]["points"] += earnings

    await save_stats(users)


@bot.slash_command(guild_ids=allowedServers, name="leaderboard", description="See the current Top 10 guessers")
async def leaderboard(ctx, x=10):
    """
    Create leaderboard and create embedded text to display it.
    If no one has scored yet, appropriate (?) message is displayed.
    :param ctx: Discord info variable (I think)
    :param x: Number of leaders to display. Default is 10.
    :return:
    """
    users = await load_stats()
    leader_board = []
    for user in users:
        name = int(user)
        user_total = users[user]["points"]
        leader_board.append((name, user_total))  # Tuples with the username and score are appended to leaderboard list.

    leader_board.sort(key=lambda entry: entry[1], reverse=True)  # Sorts in place, using score as key (I hope)

    em = discord.Embed(
        title=f"Top {x} best guessers this week!", color=discord.Color(0xF20000))

    if leader_board[0][1] == 0:
        em.add_field(name="Scores?", value="We ain't got none yet! Start guessing!", inline=False)
    else:
        for i in range(0, x):
            id_ = leader_board[i][0]
            member = await bot.fetch_user(id_)
            name = member.name
            em.add_field(name=f"{i+1}. {name}", value=f"{leader_board[i][1]}",  inline=False)

    await ctx.respond(embed=em)


@bot.slash_command(guild_ids=allowedServers)
async def clear_stats(ctx):
    """
    Display weekly results and clear stats.
    :param ctx: Discord info variable (I think)
    :return:
    """
    channel_id = 600400648969650186  # NetflixAndChill
    # ikauns testing channel, insert your own ( ͡° ͜ʖ ͡°)
    # channel_id = 430333455566503940
    channel = bot.get_channel(channel_id)
    await ctx.respond("Week over! Here are the final results for this week!")
    x = 10
    await leaderboard(ctx, x)  # Displaying the leaderboard only needs to be coded once. I think. I hope.

    await channel.send("Erasing data....")

    users = await load_stats()

    for user in users:
        try:  # Added to provide safety in case different fields (non-user Users fields) are added later.
            users[user]["points"] = 0
        except KeyError:
            continue

    await save_stats(users)

    await channel.send("New week started! Have fun guessing!")


@tasks.loop(minutes=60.0)
async def task():
    """
    Runs clear_stats() once a week on Monday.
    :return:
    """
    channel_id = 600400648969650186  # NetflixAndChill
    channel = bot.get_channel(channel_id)
    if datetime.now().day == 0 and datetime.now().hour == 0:
        await clear_stats()
    else:
        await channel.send("tick <@300188652884197376>")
        print("Tick")


async def join_game(user, users):
    """
    Add user to running stats.
    :param user: User to add. If present in users, nothing is done.
    :param users: Current list of users.
    :return: (possibly) modified list of users
    """
    if str(user.id) not in users:
        users[str(user.id)] = {"points": 0}
    return users


async def load_stats():
    """
    Gets stats from JSON file and return JSON object.
    :return: dictionary of current participants, scores, and other stats. Returns blank dict if file not found.
    """
    try:
        with open("mainstats.json", "r") as f:
            users = json.load(f)
    except OSError:
        print("File not found or error occurred. Creating empty stats file.")
        users = {}
    return users


async def save_stats(users):
    """
    Save user stats as JSON file.
    :param users: dict of users and info.
    :return:
    """
    try:
        with open("mainstats.json", "w") as f:
            json.dump(users, f)
    except OSError:
        print("File write error.")


bot.run(os.getenv('BOT_TOKEN'))  # insert your own bot token ( ͡° ͜ʖ ͡°)
