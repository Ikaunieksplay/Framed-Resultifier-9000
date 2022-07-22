"""
Generates leaderboards of players
"""
import discord
from discord.ext.commands import Bot
import statistics

class player:
    def __init__(self, id, points):
        self.id = id
        self.points = points


async def get_embed(x, bot: discord.ext.commands.Bot):
    """
    Creates embedded leaderboard text of top x contestants.
    TODO Add a thing that replaces the leaderboard with some text if no one has scored yet? Getting something like https://imgur.com/YVUZbur is just silly
    :param x: Number of leaders to display
    :param bot: the discord bot to get usernames from
    :return: discord.Embed object
    """
    leaderboard = await get_list()

    em = discord.Embed(title=f"{x} best guessers!", color=discord.Color(0xF20000))
    
    index = 1
    for user in leaderboard:
        member = await bot.fetch_user(user.id)
        name = member.name
        points = user.points
        em.add_field(name=f"{index}. {name}", value=f"{points}",  inline=False)
        if index == x:
            break
        index += 1
    return em

async def get_list():
    """
    Creates a sorted list of contestants.
    :return: list of player objects
    """
    users = await statistics.load()
    leaderboard= []
    for user in users:
        newPlayer = player(int(user), users[user]['points'])
        leaderboard.append(newPlayer)
    
    leaderboard = sorted(leaderboard, key=lambda k: k.points, reverse=True)
    return leaderboard
