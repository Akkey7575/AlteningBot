import yaml
import nextcord
import requests
from nextcord.ext import commands

config = ""
bot = commands.Bot(command_prefix="!", help_command=None, intents=nextcord.Intents(messages=True, message_content=True))

def reload_config():
    global config
    with open("config.yml", "r", encoding="utf-8") as file:
        new_config = yaml.safe_load(file)
    config = new_config

async def update_api(altening_token):
    global config
    config["alteningToken"] = altening_token
    with open("config.yml", "w", encoding="utf-8") as file:
        yaml.dump(config, file, indent=4)

async def generate_alt():
    api_key = config["alteningToken"]
    response = requests.get(f"https://api.thealtening.com/v2/generate?key={api_key}&info=false")
    return response.json()

async def check_license(altening_token):
    response = requests.get(f"https://api.thealtening.com/v2/license?key={altening_token}")
    return response.json()

@bot.event
async def on_ready():
    print(f"Logged In | {bot.user.name}#{bot.user.discriminator}")

@bot.command()
async def help(help):
    await help.reply("!generate - Generate available Alt from TheAltening.\n!setkey - Set the ApiKey for TheAltening from Discord.\n\n**__Note: Only the user specified in config can execute it.__**")

@bot.command()
async def generate(generate):
    if int(config["allowId"]) != generate.author.id:
        await generate.reply("**Failed**\nThis command is available only to configured users.")
        return
    alt_data = await generate_alt()
    alt_token = alt_data.get("token")
    alt_limit = alt_data.get("limit")
    if alt_token == None:
        await generate.reply("**Failed**\nAn unexpected error occurred and it could not be generated.")
        return
    if alt_limit == True:
        await generate.reply(f"**Success**\nToken: {alt_token}\n\n**__Note: It appears that the daily generation limit has already been reached. The same account may have been generated.__**")
    elif alt_limit == False:
        await generate.reply(f"**Success**\nToken: {alt_token}")

@bot.command()
async def setkey(setkey, altening_token=None):
    if int(config["allowId"]) != setkey.author.id:
        await generate.reply("**Failed**\nThis command is available only to configured users.")
        return
    if altening_token == None:
        await setkey.reply("**Failed**\nThe ApiKey to be set must be specified.")
        return
    token_info = await check_license(altening_token)
    if token_info.get("hasLicense") != True:
        await setkey.reply("ApiKey is invalid or you do not have a license.")
        return
    if token_info.get("licenseType") != "premium" and token_info.get("licenseType") != "trial":
        await setkey.reply("Plan must be Premium or Trial.\n\n**__Note: Api access is only available on Premium or Trial.__**")
        return
    await update_api(altening_token)
    reload_config()
    await setkey.reply("**Success**\nA new ApiKey is set.")

reload_config()
bot.run(config["botToken"])