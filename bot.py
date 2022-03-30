# Are you sad enough?
import discord
import asyncio
import time
import datetime
import random
from discord.ext import commands
import keep_alive

# Log-in data
PREFIX = "!" # prefix
TOKEN = "DELETED" # bot token

bot = commands.Bot(command_prefix=PREFIX, case_insensitive=True)
bot.remove_command('help')

# Constants
ADMINS = "DELETED"
VERSION = "v0.4 - Unite! Stable (27.10.21)"
START_TIME = time.time()
HELP_TEXT = f"""{PREFIX}help: помощь по командам.
{PREFIX}join: добавляет юзера в очередь, если тот ещё не в ней.
{PREFIX}leave: удаляет юзера из очереди, если тот сейчас в ней.
{PREFIX}next: удаляет первого человека из очереди (доступно только администраторам).
{PREFIX}list: выводит текущую очередь с позициями.
{PREFIX}ping: пинг бота.
{PREFIX}version: текущая версия бота."""

queue = []

# Misc commands
def embed_gen(title, desc):
    embed = discord.Embed(title=title, description=desc, color=random.randint(0, 0xFFFFFF), timestamp=datetime.datetime.utcnow())
    embed.set_footer(text=VERSION)
    return embed

async def sync_queue(restore: bool):
    await bot.wait_until_ready()
    if restore:
        rfile = open('queue.txt', 'r')
        data = rfile.read().split('\n')
        for id in data:
            if id:
                user = await bot.fetch_user(int(id))
                queue.append(user)
        rfile.close()
    else:
        wfile = open('queue.txt', 'w')
        data = ""
        if queue:
            data = str(queue[0].id)
            for i in range(1, len(queue)):
                data += "\n" + str(queue[i].id)
        wfile.write(data)
        wfile.close()


async def notify_dm(name):
    DELETED = await bot.fetch_user(DELETED)
    channel = await DELETED.create_dm()
    await channel.send(f"{name} записался в очередь.")
    

@bot.command()
async def help(ctx):
    await ctx.send(embed=embed_gen("Помощь по командам", HELP_TEXT))


@bot.command()
async def ping(ctx):
    before = time.monotonic()
    message = await ctx.send("`Понг!`")
    ping = (time.monotonic() - before) * 1000
    await message.edit(content=f"`Понг! {int(ping)}ms`")


@bot.command()
async def version(ctx):
    await ctx.send(embed=embed_gen("Текущая версия", VERSION))


@bot.command()
async def uptime(ctx):
    await ctx.send(embed=embed_gen("Аптайм", f"Я работаю уже {int(time.time() - START_TIME)} секунд подряд!"))


@bot.command()
async def show_status(ctx):
    started = time.time()
    message = await ctx.send("pog")
    while True:
        await message.edit(content=f"`I'm doing this process for {int(time.time() - started)} seconds.`")
        await asyncio.sleep(10)


# Queue commands
@bot.command()
async def join(ctx, *forcing: discord.User):
    emb_title, emb_desc, text_field = "", "", ""
    user = ctx.author
    if forcing:
        forced = forcing[0]
        if user.id in ADMINS:
            if forced not in queue:
                queue.append(forced)
                emb_title = "Очередь обновлена!"
                emb_desc = f"{forced.mention} добавлен в очередь администратором {user.mention}."
                text_field = forced.mention
            else:
                emb_title = "Что-то пошло не так..."
                emb_desc = f"{forced.mention} уже находится в очереди на позиции {queue.index(forced) + 1}."
        else:
            emb_title = "Что-то пошло не так..."
            emb_desc = "У Вас недостаточно прав."
    else:
        if user not in queue:
            if (not queue):
                await notify_dm(user.name)
            emb_title = "Очередь обновлена!"
            emb_desc = f"{user.mention} добавлен в очередь."
            text_field = user.mention
            queue.append(user)
        else:
            emb_title = "Что-то пошло не так..."
            emb_desc = f"{user.mention} уже находится в очереди на позиции {queue.index(user) + 1}."
    await ctx.send(text_field, embed=embed_gen(emb_title, emb_desc))
    await sync_queue(False)


@bot.command()
async def leave(ctx, *forcing: discord.Member):
    emb_title, emb_desc, text_field = "", "", ""
    user = ctx.author
    if forcing:
        forced = forcing[0]
        if user.id in ADMINS:
            if forced not in queue:
                emb_title = "Что-то пошло не так..."
                emb_desc = f"{forced.mention} и так не находится в очереди."
            else:
                emb_title = "Очередь обновлена!"
                emb_desc = f"{forced.mention} удалён из очереди администратором {user.mention}."
                text_field = forced.mention
                if queue.index(user) == 0 and len(queue) > 1:
                    emb_desc += f"\n{queue[1].mention}, Вы следующий!"
                    text_field += " " + queue[1].mention
                elif len(queue) == 1:
                    emb_desc += "\nТеперь очередь пуста!"
                queue.pop(queue.index(forced))
        else:
            emb_title = "Что-то пошло не так..."
            emb_desc = "У Вас недостаточно прав."
    else:
        if user not in queue:
            emb_title = "Что-то пошло не так..."
            emb_desc = f"{user.mention} и так не находится в очереди."
        else:
            emb_title = "Очередь обновлена!"
            emb_desc = f"{user.mention} вышел из очереди."
            text_field = user.mention
            if queue.index(user) == 0 and len(queue) > 1:
                emb_desc += f"\n{queue[1].mention}, Вы следующий!"
                text_field += " " + queue[1].mention
            elif len(queue) == 1:
                emb_desc += "\nТеперь очередь пуста!"
            queue.pop(queue.index(user))
    await ctx.send(text_field, embed=embed_gen(emb_title, emb_desc))
    await sync_queue(False)


@bot.command()
async def next(ctx):
    emb_title, emb_desc, text_field = "", "", ""
    author = ctx.author
    if author.id in ADMINS:
        if not len(queue):
            emb_title = "Что-то пошло не так..."
            emb_desc = "Очередь пуста."
        else:
            stop_rolling = False
            while not stop_rolling:
                emb_title = "Следующий!"
                emb_desc = f"{queue[0].mention}, настала Ваша очередь! Отреагируйте лайком под этим сообщением в течение трёх минут, чтобы удостовериться, что Вы ещё с нами."
                text_field = queue[0].mention
                message = await ctx.send(text_field, embed=embed_gen(emb_title, emb_desc))
                await message.add_reaction('👍')
                def check(reaction, user):
                    return user == queue[0] and str(reaction.emoji) == '👍'
                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=180.0, check=check)
                except asyncio.TimeoutError:
                    emb_title = "Только не это..."
                    emb_desc = f'{queue[0].mention} прозевал свою очередь!'
                else:
                    emb_title = "Получилось!"
                    emb_desc = f'{queue[0].mention} подтвердил, что он готов к сдаче.'
                    stop_rolling = True
                if len(queue) == 1:
                    emb_desc += "\nТеперь очередь пуста!"
                    stop_rolling = True
                elif stop_rolling:
                    emb_desc += f"{queue[1].mention}, Вы следующий!"
                    text_field = queue[1].mention
                queue.pop(0)
    else:
        emb_title = "Что-то пошло не так..."
        emb_desc = "У Вас недостаточно прав."
    await ctx.send(text_field, embed=embed_gen(emb_title, emb_desc))
    await sync_queue(False)


@bot.command()
async def list(ctx):
    emb_title, emb_desc = "Текущая очередь", ""
    user = ctx.author
    if not len(queue):
        emb_desc = "Очередь пуста."
    else:
        for i in range(len(queue)):
            emb_desc += f"{i + 1}: {queue[i].name}\n"
        if user in queue:
            position = queue.index(user) + 1
            emb_desc += f"\nВаша позиция: {position}. Примерное время ожидания: {15 * position}-{25 * position} минут."
    await ctx.send(embed=embed_gen(emb_title, emb_desc))


@bot.command()
async def clear(ctx):
    emb_title, emb_desc = "", ""
    author = ctx.author
    if author.id in ADMINS:
        emb_title = "Очередь обновлена!"
        emb_desc = "Очередь очищена."
        queue.clear()
    else:
        emb_title = "Что-то пошло не так..."
        emb_desc = "У Вас недостаточно прав."
    await ctx.send(embed=embed_gen(emb_title, emb_desc))
    await sync_queue(False)


keep_alive.keep_alive()
bot.loop.create_task(sync_queue(True))
bot.run(TOKEN)
