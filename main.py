import discord
import asyncio
import time
from discord.ext import commands
import os
import sys
from discord import FFmpegPCMAudio
import random

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

queue = []

def roll_dice():
    return random.randint(1, 6)

@bot.command()
async def parancsok(ctx):
    await ctx.send('>ping \n >hello \n >stop \n >join \n >leave \n >restart \n >mekercs \n >skip \n >kaszino')

@bot.command()
async def mekercs(ctx):
    await ctx.send('tekercs')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def hello(ctx):
    await ctx.send('Ne zavarj te geci')

@bot.command()
async def stop(ctx):
    await ctx.send('A bot leállítása...')
    await bot.close()

@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    if channel:
        await ctx.send("mindjárt megyek")
        time.sleep(2)
        voice_client = await channel.connect()
        if not voice_client.is_playing() and not queue:
            await play_random_audio(voice_client)
    else:
        await ctx.send("Nem vagy fent sehol")

@bot.command()
async def skip(ctx):
    if ctx.voice_client:
        await ctx.send('kövi zene')
        ctx.voice_client.stop()
        await play_random_audio(ctx.voice_client)

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.send("csa te geci")
        time.sleep(2)
        await ctx.guild.voice_client.disconnect()

@bot.command()
async def restart(ctx):
    await ctx.send("kimegyek wc-re")
    os.execv(sys.executable, ['python'] + sys.argv)

async def play_random_audio(voice_client):
    global queue
    current_directory = os.path.dirname(os.path.abspath(__file__))
    mp3_files = [file for file in os.listdir(current_directory) if file.endswith('.mp3')]
    if mp3_files:
        random_mp3 = random.choice(mp3_files)
        source = FFmpegPCMAudio(os.path.join(current_directory, random_mp3))
        voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(voice_client), bot.loop))
    else:
        print("Nincs mp3 szar")

async def play_next(voice_client):
    global queue
    if queue:
        next_song = queue.pop(0)
        source = FFmpegPCMAudio(next_song)
        voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(voice_client), bot.loop))
    else:
        await play_random_audio(voice_client)

@bot.command()
async def kaszino(ctx):
    await ctx.send("Üdvözöllek a kaszinóban!")
    balance = 1000 
    while True:
        await ctx.send(f"\nJelenlegi egyenleg: {balance}")
        await ctx.send("Mennyit szeretnél fogadni? (0 = kilépés)")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        bet_msg = await bot.wait_for('message', check=check)
        bet = int(bet_msg.content)
        if bet == 0:
            await ctx.send("Viszlát! Remélem jössz még vissza!")
            break
        if bet > balance:
            await ctx.send("Nincs elég pénzed a fogadásra!")
            continue
        
        await ctx.send("Melyik számra tippelsz? (1-6):")
        guess_msg = await bot.wait_for('message', check=check)
        guess = int(guess_msg.content)
        
        dice_result = roll_dice()
        await ctx.send(f"A dobott szám: {dice_result}")
        
        if guess == dice_result:
            await ctx.send("Gratulálok, nyertél!")
            balance += bet
        else:
            await ctx.send("Sajnos nem találtál, vesztettél.")
            balance -= bet
            
        if balance <= 0:
            await ctx.send("Sajnáljuk, elfogyott a pénzed. Viszlát!")
            break

bot.run('A token geci')