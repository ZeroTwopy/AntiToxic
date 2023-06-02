# made by ZeroTwo#1337 using chatgpt
# You use it at your own risk.
from datetime import timedelta
import discord
from discord import utils as Utils
from discord.ext import commands
import requests


# config
TOKEN = '1234' # your discord bot token
SERVER_ID = 1234 # works only in this guild
PERSPECTIVE_API_KEY = '1234' # your perspective api key from google
ignored_role_id = 1234 # ignored role id
mute_time = 60 # mute time in seconds
toxiclevel = 0.6 # toxic level (0.1 - 0.9)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)


def check_toxicity(message_content, language):
    url = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key=' + PERSPECTIVE_API_KEY
    analyze_request = {
        'comment': {'text': message_content},
        'languages': [language],
        'requestedAttributes': {'TOXICITY': {}}
    }
    try:
        response = requests.post(url, json=analyze_request)
        data = response.json()
        toxicity_score = data['attributeScores']['TOXICITY']['summaryScore']['value']
        return toxicity_score
    except requests.exceptions.RequestException as error:
        print(f'An error occurred: {error}')
        return 0.0




@bot.event
async def on_ready():
    print('Bot is ready.')


@bot.event
async def on_message(message):
    if not message.guild.id == SERVER_ID:
        return
    if message.author.bot:
        return

    if ignored_role_id in [role.id for role in message.author.roles]:
        return

    toxicity_threshold = toxiclevel
    toxicity_score_en = check_toxicity(message.content, 'en')
    toxicity_score_pl = check_toxicity(message.content, 'pl')
    toxicity_score_de = check_toxicity(message.content, 'de')
    if toxicity_score_en >= toxicity_threshold or toxicity_score_pl >= toxicity_threshold or toxicity_score_de >= toxicity_threshold:
        try:
            await message.channel.send(f"{message.author.mention} Your message was toxic.")
            await message.delete()
            await message.author.timeout(Utils.utcnow()+timedelta(seconds=mute_time), reason="toxic message")

        except:
            pass

    await bot.process_commands(message)

bot.run(TOKEN)
