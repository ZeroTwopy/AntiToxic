from datetime import timedelta
from discord import utils
from discord.ext import commands
from dotenv import load_dotenv
import discord
import requests
import config
import os
import re

userWarnings = {} # map of warnings for every member

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)


@bot.event
async def on_ready():
    print("[Log] Bot is ready.")
    print(f"[Log] Logged in as {bot.user}")


async def requestMessageCheck(message_content, language):
    url = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key=' + os.getenv('PERSPECTIVE_API_KEY')

    analyzeRequest = {
        'comment': {'text': message_content},
        'languages': [language],
        'requestedAttributes': {'TOXICITY': {}}
    }

    try:
        response = requests.post(url, json=analyzeRequest)
        data = response.json()
        toxicityScore = data['attributeScores']['TOXICITY']['summaryScore']['value']
        return toxicityScore

    except requests.exceptions.RequestException as error:
        print(f"[Log] An error occurred: {error}")
        return 0.0


async def discordMessageCheck(message, requestType):

    whitelistedPatterns = [re.compile(pattern) for pattern in config.whitelistedWords]
    blacklistedPatterns = [re.compile(pattern) for pattern in config.blacklistedWords]

    if any(pattern.search(message.content) for pattern in whitelistedPatterns):
        for pattern in whitelistedPatterns:
            messageContent = re.sub(pattern, "", message.content)
    else:
        messageContent = message.content

    if len(messageContent) == 0:
        messageContent += ""

    toxicityScore = await requestMessageCheck(messageContent, 'en')

    if any(pattern.search(message.content) for pattern in blacklistedPatterns):
        for pattern in blacklistedPatterns:
            if pattern.search(message.content):
                toxicityScore += 1

    if toxicityScore >= config.toxicityThreshold:
        try:
            userId = message.author.id

            try:
                test = userWarnings[userId]
            except:
                userWarnings[userId] = 0

            if requestType == 1: # edited or normal message
                msg = "message"
            elif requestType == 2:
                msg = "edited message"
            else:
                msg = "message"

            if userWarnings[userId] >= 3:

                await message.channel.send(
                    f"{message.author.mention} Your {msg} was toxic or breaking rules. Warning number 4/4. You got muted!")
                await message.delete()
                await message.author.timeout(utils.utcnow() + timedelta(seconds=config.muteTime), reason="Toxic or breaking rules message")
                userWarnings[userId] = 0
            else:
                userWarnings[userId] += 1
                await message.channel.send(
                    f"{message.author.mention} Your {msg} was toxic or breaking rules. Warning number {userWarnings[userId]}/4.")
                await message.delete()
        except:
            print("error in except line 81")
            pass


@bot.event
async def on_message(message):
    if not message.guild.id == config.serverId:
        return

    if message.author.bot:
        return

    if config.ignoredRoleId in [role.id for role in message.author.roles]:
        return

    await discordMessageCheck(message, 1)
    await bot.process_commands(message)


@bot.event
async def on_message_edit(before, after):
    message = after

    if not message.guild.id == config.serverId:
        return

    if message.author.bot:
        return

    if config.ignoredRoleId in [role.id for role in message.author.roles]:
        return

    await discordMessageCheck(message, 2)
    await bot.process_commands(message)


bot.run(os.getenv('TOKEN'))
