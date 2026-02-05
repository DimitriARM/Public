
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv() 
# =========================
# CONFIG
# =========================
TOKEN = os.getenv("DISCORD_TOKEN")

CHANNEL_ID = 1085425159420264502

PREFIX = '!'

intents = discord.Intents.default()
intents.members = True  # Needed to access member info
intents.message_content = True  # Needed for command prefix
intents.messages = True  # Needed for on_message event

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

banned_users = {}  # thread_id: set of user_ids

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    
    # Send online message to the specified channel
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("Hello, taxation is theft!")
    else:
        print("Channel not found. Check CHANNEL_ID.")

@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.Thread) and message.channel.id in banned_users and message.author.id in banned_users[message.channel.id] and not message.author.bot:
        await message.delete()
        # Optional: DM the user
        try:
            await message.author.send(f"You are banned from posting in the hill '{message.channel.name}'.")
        except discord.Forbidden:
            pass  # User has DMs disabled
        return
    
    await bot.process_commands(message)

@bot.command(name='hillban')
async def hillban(ctx, member: discord.Member):
    # Check if the command is used in a thread within a forum channel
    if not isinstance(ctx.channel, discord.Thread) or not isinstance(ctx.channel.parent, discord.ForumChannel):
        await ctx.send("This command can only be used at the hills.")
        return

    # Check if the thread has the #good-faith tag
    applied_tags = ctx.channel.applied_tags
    if not any(tag.name.lower() == 'good faith' for tag in applied_tags):
        await ctx.send("This command can only be used in threads tagged with 'good-faith'.")
        return

    # Check if the command issuer is the thread owner (creator)
    if ctx.author != ctx.channel.owner:
        await ctx.send("Only the creator of this hill can ban users here.")
        return

    thread_id = ctx.channel.id
    if thread_id not in banned_users:
        banned_users[thread_id] = set()
    
    if member.id in banned_users[thread_id]:
        await ctx.send(f"{member.mention} is already banned from this hill.")
        return
    
    banned_users[thread_id].add(member.id)
    
    await ctx.send(f"{member.mention} has been banned from posting in this hill but can still view it and participate in other hills.")

@bot.command(name='hillunban')
async def hillunban(ctx, member: discord.Member):
    # Check if the command is used in a thread within a forum channel
    if not isinstance(ctx.channel, discord.Thread) or not isinstance(ctx.channel.parent, discord.ForumChannel):
        await ctx.send("This command can only be used at the hills.")
        return

    # Check if the thread has the #good-faith tag
    applied_tags = ctx.channel.applied_tags
    if not any(tag.name.lower() == 'good faith' for tag in applied_tags):
        await ctx.send("This command can only be used in hills tagged with 'good-faith'.")
        return

    # Check if the command issuer is the thread owner (creator)
    if ctx.author != ctx.channel.owner:
        await ctx.send("Only the creator of this hill can unban users here.")
        return

    thread_id = ctx.channel.id
    if thread_id in banned_users and member.id in banned_users[thread_id]:
        banned_users[thread_id].remove(member.id)
        if not banned_users[thread_id]:
            del banned_users[thread_id]
        await ctx.send(f"{member.mention} has been unbanned from posting in this hill.")
    else:
        await ctx.send(f"{member.mention} is not banned from this hill.")

bot.run(TOKEN)
