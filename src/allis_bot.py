import discord
import asyncio
import os
from discord.ext import commands
from supabase import create_client, Client
from dotenv import load_dotenv


load_dotenv("C:/Users/SCSM11/Documents/Bot/src/api-keys.env")

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if not all([SUPABASE_URL, SUPABASE_KEY, DISCORD_TOKEN]):
    raise ValueError("Missing one or more required environment variables.")

# Discord Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready: {bot.user.name}")

@bot.command(name="apply")
async def apply(ctx):
    try:
        await ctx.author.send("👋 Hello! Let's start your application.")
    except discord.Forbidden:
        await ctx.reply("❌ I can't DM you. Please enable DMs and try again.")
        return

    def check(m):
        return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

    try:
        await ctx.author.send("Which **BRM component party** do you want to join?")
        party_msg = await bot.wait_for("message", check=check, timeout=60)
        party_of_choice = party_msg.content.strip()

        await ctx.author.send("What is your **Roblox username**?")
        username_msg = await bot.wait_for("message", check=check, timeout=60)
        username = username_msg.content.strip()

        await ctx.author.send("Now, please provide your **Roblox profile link**:")
        roblox_msg = await bot.wait_for("message", check=check, timeout=60)
        roblox_link = roblox_msg.content.strip()

        # Store in Supabase
        supabase.table("applications").insert({
            "party_of_choice": party_of_choice,
            "discord_username": str(ctx.author),
            "roblox_username": username,
            "roblox_link": roblox_link
        }).execute()

        await ctx.author.send("✅ Application submitted! Thank you.")
    except asyncio.TimeoutError:
        await ctx.author.send("⏰ You took too long. Please try again using `!apply`.")

@bot.command(name="shutdown")
async def shutdown(ctx):
    allowed_user_ids = [519105090502787084]  # Replace with your Discord user ID
    if ctx.author.id not in allowed_user_ids:
        await ctx.reply("❌ You’re not allowed to shut me down.")
        return

    await ctx.reply("🛑 Shutting down. Bye!")
    await bot.close()

bot.run(DISCORD_TOKEN)
