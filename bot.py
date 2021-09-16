import discord
import time
from flask import Flask
from threading import Thread
from discord.ext import commands

# Const
PREFIX = "" # prefix
TOKEN = "" # bot token
ADMIN_LIST = [] # list of admin ids
VERSION = "v0.2.1 - Better Interface+ (16.09.21)"
HELP_TEXT = f"""```
{PREFIX}join: добавляет юзера в очередь, если тот ещё не в ней.
{PREFIX}leave: удаляет юзера из очереди, если тот сейчас в ней.
{PREFIX}next: удаляет первого человека из очереди (доступно только администраторам).
{PREFIX}list: выводит текущую очередь с позициями.
{PREFIX}help: помощь по командам.```"""

app = Flask('')
bot = commands.Bot(command_prefix=PREFIX)
bot.remove_command('help')
queue = []


# Server part
@app.route('/')
def server_main():
    return "Server up."


def server_run():
    app.run(host='0.0.0.0', port=31567)


# Commands
@bot.command()
async def help(ctx):
    await ctx.send(HELP_TEXT)


@bot.command()
async def ping(ctx):
    before = time.monotonic()
    message = await ctx.send("`Pong!`")
    ping = (time.monotonic() - before) * 1000
    await message.edit(content=f"`Pong! {int(ping)}ms`")


@bot.command()
async def version(ctx):
    await ctx.send(f"`{VERSION}`")


@bot.command()
async def join(ctx):
    user = ctx.author
    if (user.name, user.mention) not in queue:
        queue.append((user.name, user.mention))
        await ctx.send(f"{user.mention}` добавлен в очередь.`")
    else:
        await ctx.send(f"{user.mention}` уже находится в очереди на позиции {queue.index((user.name, user.mention)) + 1}.`")


@bot.command()
async def leave(ctx):
    user = ctx.author
    if (user.name, user.mention) not in queue:
        await ctx.send(f"{user.mention}` и так не находится в очереди.`")
    else:
        if queue.index((user.name, user.mention)) == 0 and len(queue) > 1:
            await ctx.send(f"{user.mention}` вышел из очереди.` {queue[1][1]}`, ваша очередь подходит!`")
        else:
            if len(queue) > 1:
                await ctx.send(f"{user.mention}` вышел из очереди.`")
            else:
                await ctx.send(f"{user.mention}` вышел из очереди. Теперь очередь пуста!`")
        queue.pop(queue.index((user.name, user.mention)))


@bot.command()
async def next(ctx):
    user = ctx.author
    if user.id in ADMIN_LIST:
        if not len(queue):
            await ctx.send("`Очередь и так пуста.`")
        else:
            if len(queue) > 1:
                await ctx.send(f"{queue[0][1]}` удалён из очереди. `{queue[1][1]}`, ваша очередь подходит!`")
            else:
                await ctx.send(f"{queue[0][1]}` удалён из очереди. Теперь очередь пуста!`")
            queue.pop(0)
    else:
        await ctx.send(f"{user.mention}` не является админом.`")


@bot.command()
async def list(ctx):
    user = ctx.author
    if not len(queue):
        await ctx.send("```Очередь пуста.```")
    else:
        text = "```\n"
        for i in range(len(queue)):
            text += f"{i + 1}: {queue[i][0]}\n"
        if ((user.name, user.mention)) in queue:
            position = queue.index((user.name, user.mention)) + 1
            text += f"\nВаша позиция: {position}. Примерное время ожидания: {15 * position}-{25 * position} минут.\n"
        text += "```"
        await ctx.send(text)


appth = Thread(target=server_run)
appth.start()
bot.run(TOKEN)
