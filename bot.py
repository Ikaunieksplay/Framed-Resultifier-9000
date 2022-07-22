import statistics
import discord
from discord.ext import tasks
from discord.ext.commands import Bot
import os
from datetime import datetime
import scoreboard

os.chdir("") # insert your own, full path to folder where bot is ( ͡° ͜ʖ ͡°)

intents = discord.Intents.all()

# Create Bot object, give all intents.
bot = discord.ext.commands.Bot(intents=intents)

# list of channels bot will react to (copy channel ids and add it)
# add this to use:
# if !(message.channel.id in allowedChannels):
#   return
allowedChannels = [430333455566503940]  # Currently Ikaun's bot testing server general, insert your own ( ͡° ͜ʖ ͡°)

allowedServers = [430333455566503937] # Currently Ikaun's bot testing server, insert your own ( ͡° ͜ʖ ͡°)


@bot.event
async def on_ready():
    print("Bot is ready")


@bot.event
async def on_message(message):
    # Checks if message channel ID is in list of approved channels.
    if message.channel.id not in allowedChannels:
        return

    if "🎥" and "Framed" in message.content:
        # Get score from current message.
        not_score = message.content.count("🟥")
        score = 7 - not_score
        print(f"Score detected! Points: {score}")

        # Get current user and add to players if new.
        current_user = message.author
        await join_game(current_user)

        # get list of all users
        users = await statistics.load()

        # Display score, increment points for user
        users[str(current_user.id)]["points"] += score
        await message.reply(f"Score detected! {score} points added to {current_user}")

        await statistics.save(users)

    await bot.process_commands(message)


@bot.slash_command(guild_ids=allowedServers, name="stats", description="Shows how many points you have")
async def stats(ctx):
    await join_game(ctx.author)
    user = ctx.author
    users = await statistics.load()

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
    users = await statistics.load()

    earnings = int(-50)                         #sneaky anti cheat added

    await ctx.respond(f"50 points added!")

    users[str(user.id)]["points"] += earnings

    await statistics.save(users)


@bot.slash_command(guild_ids=allowedServers, name="leaderboard", description="See the current Top 10 guessers")
async def leaderboard(ctx):
    """
    Create leaderboard and create embedded text to display it.
    :param ctx:
    :return:
    """
    x = 10
    em = await scoreboard.get_embed(x, bot)

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
    channel_id = allowedChannels[0]
    channel = bot.get_channel(channel_id)
    await ctx.respond("Week over! Here are the final results for this week!")
    x = 10
    em = await scoreboard.get_embed(x, bot)

    await channel.send(embed=em)
    await channel.send("Erasing data....")

    await statistics.clear()

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
    users = await statistics.load()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {"points": 0}

    await statistics.save(users)
    return True

# insert your own bot token ( ͡° ͜ʖ ͡°)
bot.run("youthought.jpg")
