import discord
from discord.ext import commands
import json
import os
import asyncio
from discord.ext import commands, tasks
from datetime import datetime

os.chdir("")#insert your own ( ͡° ͜ʖ ͡°)

client = commands.Bot(command_prefix=">")

# list of channels bot will react to (copy channel ids and add it)
# add this to use:
# if !(message.channel.id in channelIDs)
#   return
allowedChannels = [600400648969650186]

@client.event
async def on_ready():
    print("Bot is ready")

@client.event
async def on_message(message):
    if not(message.channel.id in allowedChannels):
        return
    if "🎥" in message.content:
        notScore=message.content.count("🟥")
        score = 7 - notScore
        print(f"Score detected! Points: {score}")
        await join_game(message.author)
        user = message.author
        users = await get_stats()
        await message.reply(f"Score detected! {score} points added to {user}")
        users[str(user.id)]["points"] += score
        with open("mainstats.json","w") as f:
            json.dump(users,f)
    await client.process_commands(message)

@client.command()
async def balance(ctx):
    await join_game(ctx.author)
    user = ctx.author
    users = await get_stats()
    
    points_amt = users[str(user.id)]["points"]

    em = discord.Embed(title = f"{ctx.author.name}'s stats")
    em.add_field(name = "Points this week",value = points_amt)
    await ctx.send(embed = em)

@client.command()
async def beg(ctx):
    await join_game(ctx.author)
    user = ctx.author
    users = await get_stats()
    
    earnings = int(50)

    await ctx.send(f"50 points added!")

    users[str(user.id)]["points"] += earnings
    
    with open("mainstats.json","w") as f:
        json.dump(users,f)

@client.command(aliases = ["lb"])
async def leaderboard(ctx,x = 10):
    users = await get_stats()
    leader_board={}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["points"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total,reverse=True)

    em = discord.Embed(title = f"{x} best guessers this week!" , color = discord.Color(0xfa43ee))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = await client.fetch_user(id_)
        name = member.name
        em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed = em)

@client.command()
async def clear_stats(ctx):
    channel = client.get_channel()#insert your own ( ͡° ͜ʖ ͡°)
    await channel.send("Week over! Here are the final results for this week!")
    x=10
    users = await get_stats()
    leader_board={}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["points"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total,reverse=True)

    em = discord.Embed(title = f"{x} best guessers!" , color = discord.Color(0xfa43ee))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = await client.fetch_user(id_)
        name = member.name
        em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
        if index == x:
            break
        else:
            index += 1

    await channel.send(embed = em)
    await channel.send("Erasing data....")
    data = await get_stats()
    with open("mainstats.json","r") as f:
        data = json.load(f)
    for key in data:
        data[key]["points"] = 0
    with open("mainstats.json","w") as f:
        json.dump(data,f)
    await channel.send("New week started! Have fun guessing!")

@tasks.loop(minutes=60.0)
async def task(self):
    if datetime.now().day == 0 and datetime.now().hour == 0:
        channel = client.get_channel()#insert your own ( ͡° ͜ʖ ͡°)
        await channel.send("Week over! Here are the final results for this week!")
        x=10
        users = await get_stats()
        leader_board={}
        total = []
        for user in users:
            name = int(user)
            total_amount = users[user]["points"]
            leader_board[total_amount] = name
            total.append(total_amount)

        total = sorted(total,reverse=True)

        em = discord.Embed(title = f"{x} best guessers!" , color = discord.Color(0xfa43ee))
        index = 1
        for amt in total:
            id_ = leader_board[amt]
            member = await client.fetch_user(id_)
            name = member.name
            em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
            if index == x:
                break
            else:
                index += 1

        await channel.send(embed = em)
        await channel.send("Erasing data....")
        data = await get_stats()
        with open("mainstats.json","r") as f:
            data = json.load(f)
        for key in data:
            data[key]["points"] = 0
        with open("mainstats.json","w") as f:
            json.dump(data,f)
        await channel.send("New week started! Have fun guessing!")


async def join_game(user):

    users = await get_stats()
    with open("mainstats.json","r") as f:
        users = json.load(f)

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["points"] = 0

    with open("mainstats.json","w") as f:
        json.dump(users,f)
    return True

async def get_stats():
    with open("mainstats.json","r") as f:
        users = json.load(f)
        return users



client.run("youthought.jpg") #insert your own ( ͡° ͜ʖ ͡°)
