from asyncio import tasks
import asyncio
from http import client
from sqlite3 import Timestamp
import discord
import random
import os
from discord.ext import commands
from webserver import keep_alive
import requests
import urllib
import json
from itertools import chain

_JOIN_LOG_CHANNEL_ID = 981213006467846144

Client = commands.Bot(command_prefix = 'd!', help_command=None)

@Client.event
async def on_ready():
    await Client.change_presence(activity=discord.Game(name=f"on {len(Client.guilds)} servers | d!help"))
    print('Bot is ready.')

@Client.event
async def on_guild_join(guild):
    log_chan = Client.get_channel(_JOIN_LOG_CHANNEL_ID)
    if not log_chan:
        print("Failed to fetch log channel.")
        return

    embed = discord.Embed(title="", description=f"I have been added to **{guild.name}**", color=discord.Color.blue())
    await log_chan.send(embed=embed)

@Client.event
async def on_guild_remove(guild):
    log_chan = Client.get_channel(_JOIN_LOG_CHANNEL_ID)
    if not log_chan:
        print("Failed to fetch log channel.")
        return

    embed = discord.Embed(title="", description=f"I have been removed from **{guild.name}**", color=discord.Color.blue())
    await log_chan.send(embed=embed)

@Client.command(description="`Check your internet quality.`")
async def ping(ctx):
    await ctx.send(f'{round(Client.latency * 1000)}ms')

@Client.command(aliases=['8ball', 'test'], description="`Put your luck on a test.`")
async def _8ball(ctx, *, question):
    responses = ['It is certain.',
                 'It is decidely to.',
                 'Without a doubt.',
                 'Yes - Definitely.',
                 'You may rely on it.',
                 'As i see it, yes.',
                 'Most likely.',
                 'Outlook good.',
                 'Yes',
                 'Signs point to yes.',
                 'Reply hazy, try again.',
                 'Ask again later.',
                 'Better not tell you now.',
                 'Cannot predict now.',
                 'Concentrate and ask again.',
                 "Don't count on it.",
                 'My reply is no.',
                 'My Sources say no.',
                 'Outlook not so good.',
                 'Very Doubtful.']
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

@Client.command()
async def help(ctx):
    embed = discord.Embed(title='Duke`s Commands', color=discord.Color.blue())
    embed.add_field(name= "🔵  Moderation", value='`clear` `kick` `ban` `unban` `mute` `unmute` `addrole` `removerole`', inline=False)
    embed.add_field(name='🔵  Channels', value='`createtc` `deltc` `createvc` `delvc` `createtac` `delcat` `lock` `unlock`', inline=False)
    embed.add_field(name='🔵  Information', value='`ping` `avatar` `feedback` `invite` `serverinfo` `stats` `whois` `support`', inline=False)
    embed.add_field(name='🔵  Announcements', value='`announce` `poll` `embed` `remind`', inline=False)
    embed.set_footer(text='Duke Bot © 2022')
    await ctx.send(embed=embed)

@Client.command(description='`Clears up unwanted messages.`')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount : int):
    await ctx.channel.purge(limit=amount)

@Client.command(description='`You can kick disrespectable members.`')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)

@Client.command(description='`Instead of kicking you can temporary **BAN** members.`')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)

@Client.command(description='`You can unban and let others back in.`')
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return

attributes = {
   'name': "hell",
   'aliases': ["help", "helps"],
   'cooldown': commands.Cooldown(2, 5.0, commands.BucketType.user)
} 
# For 2.0, you would use CooldownMapping.from_cooldown(rate, per, type)
# because Cooldown no longer have type as it's arguments.

# During declaration
help_object = commands.MinimalHelpCommand(command_attrs=attributes)

# OR through attribute assignment
help_object = commands.MinimalHelpCommand()
help_object.command_attrs = attributes

class MyHelp(commands.HelpCommand):
    async def send_error_message(self, error):
        embed = discord.Embed(title="Error", description=error)
        channel = self.get_destination()
        await channel.send(embed=embed)

class MyHelp(commands.MinimalHelpCommand):
    def get_command_brief(self, command):
        return command.short_doc or "Command is not documented."
    
    async def send_bot_help(self, mapping):
        all_commands = list(chain.from_iterable(mapping.values()))
        formatter = HelpPageSource(all_commands, self)
        menu = MyMenuPages(formatter, delete_message_after=True)
        await menu.start(self.context)

@Client.command(description="`Mutes the specified user.`")
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=True)

    await member.add_roles(mutedRole, reason=reason)
    await ctx.send(f'{member.mention} has been muted for {reason}')

@Client.command(descrption="Unmutes a specified user")
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

    await member.remove_roles(mutedRole)
    await ctx.send(f"{member.mention} has been unmuted")

@Client.command(description="`adds a role to a specified user.`")
async def addrole(ctx, role: discord.Role, user: discord.Member):
    if ctx.author.guild_permissions.administrator:
        await user.add_roles(role)
        await ctx.send(f'Succesfully given {role.mention} to {user.mention}')

@Client.command(description="`removes a specified user's role.`")
async def removerole(ctx, role: discord.Role, user: discord.Member):
    if ctx.author.guild_permissions.administrator:
        await user.remove_roles(role)
        await ctx.send(f'Succesfully removed {role.mention} from {user.mention}')

@Client.command(description="`Inform others by making an announcement.`")
async def announce(ctx, *,message):
    embed = discord.Embed(title='Official announcement!',description=message, color=discord.Color.blue())
    embed.set_footer(text='Duke Bot © 2022')
    await ctx.send(embed=embed)

@Client.command(description="`Invite Duke to your server.`")
async def invite(ctx, invite_link=None):
    if invite_link == None:
        await ctx.message.author.send(embed=discord.Embed(
                        title='Invite Duke',
                        description = '[Click Here](https://discord.com/api/oauth2/authorize?client_id=974631926897999902&permissions=8&scope=bot) To invite **Duke** to your server',
                        color=discord.Color.blue()
                        ))
        return

@Client.command(description="`Become more democratic with polls.`")
async def poll(ctx, *, message):
    if ctx.author.guild_permissions.administrator:
        emb=discord.Embed(title=" Poll ", description=f'{message}', color=discord.Color.blue())
        m = await ctx.channel.send(embed=emb)
        await m.add_reaction('👍')
        await m.add_reaction('👎')

@Client.command(description="`Get to know a specificed server.`")
async def serverinfo(ctx):
    """Displaying server info"""
    embed = discord.Embed(title="Server Information",color = discord.Color.blue())
    embed.add_field(name="Server Name", value=ctx.message.guild.name, inline=False)
    embed.add_field(name="Roles:", value=ctx.message.guild.roles, inline=False)
    embed.add_field(name="Members", value=len(ctx.message.guild.members))
    embed.add_field(name="Channels",value=len(ctx.message.guild.channels))
    embed.add_field(name="Requested by",value=str(ctx.message.author.mention))
    embed.set_footer(text="Duke Bot © 2022")
    await ctx.send(embed=embed)

@Client.command(description="`Learn more about a specified user.`")
async def whois(ctx,user:discord.Member=None):

    embed = discord.Embed(color=discord.Color.blue(),Timestamp=ctx.message.created_at)

    embed.set_author(name=f"User Info - {user}")
    embed.set_thumbnail(url=user.avatar_url)
    embed.set_footer(text=f"Requested by - {ctx.author}",
icon_url=ctx.author.avatar_url)

    embed.add_field(name='ID:', value=user.id,inline=False)
    embed.add_field(name='Name:',value=user.display_name,inline=False)

    embed.add_field(name='Created at:',value=user.created_at,inline=False)
    embed.add_field(name='Joined at:',value=user.joined_at,inline=False)


    embed.add_field(name='Bot?',value=user.bot,inline=False)

    await ctx.send(embed=embed)

@Client.command(description="`Send some feedback about Duke.`")
async def feedback(ctx, *,message):
    emb=discord.Embed(title=f"Feedback from: {ctx.author}", description=f'{message}', color=discord.Color.blue())

    emb.set_footer(text=f"Sent by - {ctx.author}", icon_url=ctx.author.avatar_url)
    feedbk_chan = Client.get_channel(974564015072227349)
    m = await feedbk_chan.send(embed=emb)

@Client.command(description="`Never forget about anything.`")
async def remind(ctx, time, *, task):
    def convert(time):
        pos = ['s', 'm', 'h', 'd']

        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600*24}

        unit = time[-1]

        if unit not in pos:
            return -1
        try:
            val = int(time[:-1])
        except:
            return -2
 
        return val * time_dict[unit]

    converted_time = convert(time)

    if converted_time == -1:
        await ctx.send("You didn't answer the time correctly.")
        return

    if converted_time == -2:
        await ctx.send("The time must be an integer")
        return
    
    await ctx.send(f"Started reminder for **{task}** and will last **{time}**.")

    await asyncio.sleep(converted_time)
    await ctx.send(f"{ctx.author.mention} your reminder for **{task}** has finished!")

@Client.command(description="`Say something formal.`")
async def embed(ctx, *, message):
    if ctx.author.guild_permissions.administrator:
        emb=discord.Embed(title=f'Embed by - {ctx.author}',description=f'{message}', color=discord.Color.blue())
        emb.set_footer(text=f"Sent by - {ctx.author}", icon_url=ctx.author.avatar_url)
        m = await ctx.channel.send(embed=emb)



@Client.command(description="`Join Duke's support community.`")
async def support(ctx, invite_link=None):
    if invite_link == None:
        await ctx.message.author.send(embed=discord.Embed(
                        title='Join Support Server',
                        description = '[Click Here](https://discord.gg/kZfceh6Y2f) To join **Duke** support server',
                        color=discord.Color.blue()
                        ))
        return

@Client.command(description="`Some info about Duke.`")
async def stats(ctx):
  embed = discord.Embed(title=":bar_chart: Bot Statistics", color=discord.Color.blue())
  
  embed.add_field(name="Developer:", value=":hammer: coco.py#9632", inline=True)
  embed.add_field(name="Servers Count:", value=f":homes: {len(Client.guilds)}", inline=True)
  embed.add_field(name="Total members:", value="N/A", inline=True)
  embed.add_field(name="Python Version:", value="3.10.4", inline=True)
  embed.add_field(name="Latency:", value=f":ping_pong: {round(Client.latency * 1000)}ms", inline=True)
  embed.add_field(name="Commands:", value=f":gear: {len(Client.commands)}", inline=True)
  embed.add_field(name="Status:", value=":green_circle: Online")

  await ctx.send(embed=embed)

@Client.command(description="`Are you trying to steal someone's profile?`")
async def avatar(ctx, member : discord.Member = None):
  if member == None:
    member = ctx.author

  memberAvatar = member.avatar_url

  avaEmbed = discord.Embed(title = f"{member.name}'s Avatar")
  avaEmbed.set_image(url = memberAvatar)

  await ctx.send(embed = avaEmbed)

@Client.command(description="`Delete a specified Text Channel.`")
async def deltc(ctx, channel: discord.TextChannel):
  mbed = discord.Embed(
    title= 'Success',
    description = f'Channel: **{channel}** has been deleted'
  )
  if ctx.author.guild_permissions.manage_channels:
    await ctx.send(embed=mbed)
    await channel.delete()

@Client.command(description="`Create a random Text Channel.`")
async def createtc(ctx, channelName):
  guild = ctx.guild

  mbed = discord.Embed(
    title = 'Success',
    description = "**{}** has been successfully created.".format(channelName) 
  )
  if ctx.author.guild_permissions.manage_channels:
    await guild.create_text_channel(name='{}'.format(channelName))
    await ctx.send(embed=mbed)

@Client.command(description="`Create a random server category.`")
async def createcat(ctx, categoryName):
  guild = ctx.guild

  mbed = discord.Embed(
    title = 'Success',
    description = "**{}** has been successfully created.".format(categoryName) 
  )
  if ctx.author.guild_permissions.manage_channels:
    await guild.create_category(name='{}'.format(categoryName))
    await ctx.send(embed=mbed)


@Client.command("`Delete a specified server category.`")
async def delcat(ctx, category: discord.CategoryChannel):
  mbed = discord.Embed(
    title= 'Success',
    description = f'Category: **{category}** has been deleted'
  )
  if ctx.author.guild_permissions.manage_channels:
    await ctx.send(embed=mbed)
    await category.delete()

@Client.command(description="`Create a random Voice Channel.`")
async def createvc(ctx, VoiceChannelName):
  guild = ctx.guild

  mbed = discord.Embed(
    title = 'Success',
    description = "**{}** has been successfully created.".format(VoiceChannelName) 
  )
  if ctx.author.guild_permissions.manage_channels:
    await guild.create_voice_channel(name='{}'.format(VoiceChannelName))
    await ctx.send(embed=mbed)

@Client.command(description="`Delete a specified Voice Channel.`")
async def delvc(ctx, VoiceChannel: discord.VoiceChannel):
  mbed = discord.Embed(
    title= 'Success',
    description = f'Voice Channel: **{VoiceChannel}** has been deleted'
  )
  if ctx.author.guild_permissions.manage_channels:
    await ctx.send(embed=mbed)
    await VoiceChannel.delete()

@Client.command(description="`Put a specified channel or the whole server into a lockdown.`")
async def lock(ctx, channel : discord.TextChannel=None, setting = None):
  if setting =="--server":
    for channel in ctx.guild.channels:
      await channel.set_permissions(ctx.guild.default_role, reason=f"{ctx.author.name} locked {channel.name} with --server", send_messages=False)
    await ctx.send('locked down server')
    return
  if channel is None:
    channel = ctx.message.channel
  await channel.set_permissions(ctx.guild.default_role, reason=f"{ctx.author.name} locked {channel.name}", send_messages=False)
  await ctx.send('locked channel down')

@Client.command(description="`Remove a specified channel or the whole server out of a lockdown.`")
async def unlock(ctx, channel : discord.TextChannel=None, setting = None):
  if setting =="--server":
    for channel in ctx.guild.channels:
      await channel.set_permissions(ctx.guild.default_role, reason=f"{ctx.author.name} unlocked {channel.name} with --server", send_messages=True)
    await ctx.send('unlocked server.')
    return
  if channel is None:
    channel = ctx.message.channel
  await channel.set_permissions(ctx.guild.default_role, reason=f"{ctx.author.name} unlocked {channel.name}", send_messages=True)
  await ctx.send('unlocked channel.')

keep_alive()
TOKEN = os.environ.get("DISCORD_BOT_SECRET")
Client.run(TOKEN)
