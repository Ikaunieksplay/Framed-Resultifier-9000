"""
manages stats
"""
import json
async def save(users):
    """
    Save user stats as JSON file.
    :param users: dict of users and info.
    :return:
    """
    # TODO Should be placed into a try/except statement.
    with open("mainstats.json", "w") as f:
        json.dump(users, f)

async def load():
    """
    Gets stats from JSON file and return JSON object.
    :return: dictionary of current participants, scores, and other stats.
    """
    # TODO Should be placed into a try/except statement.
    with open("mainstats.json", "r") as f:
        users = json.load(f)
    return users

async def clear():
    data = await load()

    for key in data:
        data[key]["points"] = 0

    await save(data)