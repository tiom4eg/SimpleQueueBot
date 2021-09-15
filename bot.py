import discord
from discord.ext import commands

# Const
PREFIX = "" # prefix
TOKEN = "" # bot token
ADMIN_LIST = [] # list of admin ids
HELP_TEXT = f"""```
    {PREFIX}add: добавляет юзера в очередь, если тот ещё не в ней.
    {PREFIX}pop: удаляет первого человека из очереди (доступно только администраторам).
    {PREFIX}list: выводит текущую очередь с позициями.
    {PREFIX}help: помощь по командам.
    ```"""

bot = commands.Bot(command_prefix=PREFIX)
bot.remove_command('help')
queue = []


@bot.command()
async def help(ctx):
    await ctx.send(HELP_TEXT)


@bot.command()
async def add(ctx):
    user = ctx.author
    if (user.name, user.mention) not in queue:
        queue.append((user.name, user.mention))
        await ctx.send(f"{user.mention}` добавлен в очередь.`")
    else:
        await ctx.send(f"{user.mention}` уже находится в очереди на позиции {queue.index((user.name, user.mention)) + 1}.`")


@bot.command()
async def pop(ctx):
    user = ctx.author
    if user.id in ADMIN_LIST:
        if not len(queue):
            await ctx.send("`Очередь и так пуста.`")
        else:
            await ctx.send(f"{queue[0][1]}` удалён из очереди. `{queue[1][1]}`, ваша очередь подходит!`")
            queue.pop(0)
    else:
        await ctx.send(f"{user.mention}` не является админом.`")


@bot.command()
async def list(ctx):
    if not len(queue):
        await ctx.send("`Очередь пуста.`")
    else:
        text = "```\n"
        for i in range(len(queue)):
            text += f"{i + 1}: {queue[i][0]}\n"
        text += "```"
        await ctx.send(text)


bot.run(TOKEN)
