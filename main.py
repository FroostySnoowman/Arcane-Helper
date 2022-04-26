import discord
import datetime as DT
import asyncio
import re
import aiosqlite

from discord import Client, app_commands
from discord.ext.commands import has_permissions, MissingPermissions, CommandNotFound
from datetime import datetime, timedelta
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands.errors import BadArgument
from typing import Union
from sellix import Sellix

intents = discord.Intents.all()
intents.message_content = True

class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Test Button', style=discord.ButtonStyle.green, custom_id='button:1')
    async def test(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cool test button!', ephemeral=True)
        return

watching = discord.Activity(type=discord.ActivityType.watching, name="Arcane Signals")
class PersistentViewBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('.'), owner_id=503641822141349888, intents=intents, activity=watching, status=discord.Status.dnd)
        self.persistent_views_added = False

    async def on_ready(self):
        if not self.persistent_views_added:
            self.add_view(PersistentView())
            self.persistent_views_added = True

        print(f'Signed in as {self.user}')

        await self.tree.sync(guild=discord.Object(id=962895434014154853))

    async def setup_hook(self):
        purchasesLoop.start()
        roleLoop.start()

client = PersistentViewBot()

apiclient = Sellix("", "")

@tasks.loop(seconds = 30)
async def purchasesLoop():
    await client.wait_until_ready()
    guild = client.get_guild(962895434014154853)
    logs = client.get_channel(967935877089226804)
    try:
        response = apiclient.get_orders()
        unid = [item['uniqid'] for item in response]
        uniq_id = unid[:1]
        db = await aiosqlite.connect('database.db')
        cursor = await db.execute('SELECT uniqid FROM nfts')
        a = await cursor.fetchall()
        for row in a:
            if uniq_id[0] == row[0]:
                continue
            else:
                product = [item['product_title'] for item in response]
                product_title = product[:1]
                #EMAIL FROM WEBSTORE
                emails = [item['customer_email'] for item in response]
                new_dict = dict(zip(emails, response)) 
                xmails = emails[:1]
                #DISCORD ID FROM WEBSTORE
                discord_id = [item['custom_fields'] for item in response]
                xdiscord = discord_id[:1]
                d_id = [item['discord_id'] for item in xdiscord]
                #CHECK FOR 1 WEEK NFT PURCHASE
                if product_title[0] == "1 Week ( NFT )":
                    await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`.')
                    cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                    cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                    try:
                        member = await guild.fetch_member(d_id[0])
                        x = datetime.now() + timedelta(seconds=604800)
                        timestamp = x.timestamp()
                        cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("NFT", timestamp, d_id[0]))
                        nft = discord.utils.get(guild.roles, id=967619199289671710)
                        await member.add_roles(nft)
                        await db.commit()
                        await db.close()
                        continue
                    except:
                        await db.commit()
                        await db.close()
                        continue
                #CHECK FOR 1 MONTH NFT PURCHASE
                if product_title[0] == "1 Month ( NFT )":
                    await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`.')
                    cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                    cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                    try:
                        member = await guild.fetch_member(d_id[0])
                        x = datetime.now() + timedelta(seconds=2592000)
                        timestamp = x.timestamp()
                        cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("NFT", timestamp, d_id[0]))
                        nft = discord.utils.get(guild.roles, id=967619199289671710)
                        await member.add_roles(nft)
                        await db.commit()
                        await db.close()
                        continue
                    except:
                        await db.commit()
                        await db.close()
                        continue
                #CHECK FOR LIFETIME NFT PURCHASE
                if product_title[0] == "Lifetime ( NFT )":
                    await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`.')
                    cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                    cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                    try:
                        member = await guild.fetch_member(d_id[0])
                        nft = discord.utils.get(guild.roles, id=967619199289671710)
                        await member.add_roles(nft)
                        await db.commit()
                        await db.close()
                        continue
                    except:
                        await db.commit()
                        await db.close()
                        continue
                #CHECK FOR 1 WEEK CRYPTO PURCHASE
                if product_title[0] == "1 Week ( Crypto )":
                    await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`.')
                    cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                    cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                    try:
                        member = await guild.fetch_member(d_id[0])
                        x = datetime.now() + timedelta(seconds=604800)
                        timestamp = x.timestamp()
                        cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("Crypto", timestamp, d_id[0]))
                        crypto = discord.utils.get(guild.roles, id=967619220047278150)
                        await member.add_roles(crypto)
                        await db.commit()
                        await db.close()
                        continue
                    except:
                        await db.commit()
                        await db.close()
                        continue
                #CHECK FOR 1 MONTH CRYPTO PURCHASE
                if product_title[0] == "1 Month ( Crypto )":
                    await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`.')
                    cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                    cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                    try:
                        member = await guild.fetch_member(d_id[0])
                        x = datetime.now() + timedelta(seconds=2592000)
                        timestamp = x.timestamp()
                        cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("Crypto", timestamp, d_id[0]))
                        crypto = discord.utils.get(guild.roles, id=967619220047278150)
                        await member.add_roles(crypto)
                        await db.commit()
                        await db.close()
                        continue
                    except:
                        await db.commit()
                        await db.close()
                        continue
                #CHECK FOR LIFETIME CRYPTO PURCHASE
                if product_title[0] == "Lifetime ( Crypto )":
                    await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`.')
                    cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                    cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                    try:
                        member = await guild.fetch_member(d_id[0])
                        crypto = discord.utils.get(guild.roles, id=967619220047278150)
                        await member.add_roles(crypto)
                        await db.commit()
                        await db.close()
                        continue
                    except:
                        await db.commit()
                        await db.close()
                        continue
                #CHECK FOR 1 WEEK ARCANE PURCHASE
                if product_title[0] == "1 Week ( Arcane )":
                    await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`.')
                    cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                    cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                    try:
                        member = await guild.fetch_member(d_id[0])
                        x = datetime.now() + timedelta(seconds=604800)
                        timestamp = x.timestamp()
                        cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("Arcane", timestamp, d_id[0]))
                        arcane = discord.utils.get(guild.roles, id=967619323550109786)
                        await member.add_roles(arcane)
                        await db.commit()
                        await db.close()
                        continue
                    except:
                        await db.commit()
                        await db.close()
                        continue
                #CHECK FOR 1 MONTH ARCANE PURCHASE
                if product_title[0] == "1 Month ( Arcane )":
                    await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`.')
                    cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                    cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                    try:
                        member = await guild.fetch_member(d_id[0])
                        x = datetime.now() + timedelta(seconds=2592000)
                        timestamp = x.timestamp()
                        cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("Arcane", timestamp, d_id[0]))
                        arcane = discord.utils.get(guild.roles, id=967619323550109786)
                        await member.add_roles(arcane)
                        await db.commit()
                        await db.close()
                        continue
                    except:
                        await db.commit()
                        await db.close()
                        continue
                #CHECK FOR LIFETIME ARCANE PURCHASE
                if product_title[0] == "Lifetime ( Arcane )":
                    await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`.')
                    cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                    cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                    try:
                        member = await guild.fetch_member(d_id[0])
                        arcane = discord.utils.get(guild.roles, id=967619323550109786)
                        await member.add_roles(arcane)
                        await db.commit()
                        await db.close()
                        continue
                    except:
                        await db.commit()
                        await db.close()
                        continue
    except Sellix.SellixException as e:
        print(e)
    await asyncio.sleep(30)

@client.tree.command(guild=discord.Object(id=962895434014154853), description="Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('{0} ms'.format(round(client.latency, 1)), ephemeral=True)

@client.tree.command(guild=discord.Object(id=962895434014154853), description="Add a role!")
async def role(interaction: discord.Interaction, member: discord.Member, role: discord.Role, time: str):
    if interaction.user.guild_permissions.administrator:
        if role.id == 967619323550109786:
            permanent_variable = ("none", "na", "n/a", "None", "Na", "NA", "N/A", "p", "P", "Permanent", "permanent", "perm", "Perm")
            try:
                if time in permanent_variable:
                    await member.add_roles(role)
                    await interaction.response.send_message(f"I've added {role} to {member} permanently!", ephemeral=True)
                    return
                else:
                    try:
                        time_list = re.split('(\d+)',time)
                        if time_list[2] == "s":
                            time_in_s = int(time_list[1])
                        if time_list[2] == "m":
                            time_in_s = int(time_list[1]) * 60
                        if time_list[2] == "h":
                            time_in_s = int(time_list[1]) * 60 * 60
                        if time_list[2] == "d":
                            time_in_s = int(time_list[1]) * 60 * 60 * 24
    
                        x = datetime.now() + timedelta(seconds=time_in_s)
                        timestamp = x.timestamp()

                        db = await aiosqlite.connect('database.db')
                        cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("Arcane", timestamp, member.id))

                        await member.add_roles(role)

                        await interaction.response.send_message(f"I've added {role} to {member} for {time}!", ephemeral=True)
                        await db.commit()
                        await db.close()
                        return
                    except:
                        await interaction.response.send_message('An error occured. Please assure that your time variables are: `s` for seconds, `m` for minutes, `h` for hours, and `d` for days. Ex: `7d`', ephemeral=True)
                        return
            except:
                await interaction.response.send_message('An error occured. \nPlease assure your permanent variables are one of the following: `none`, `na`, `n/a`, `None`, `Na`, `NA`, `N/A`, `p`, `P`, `Permanent`, `permanent`, `perm` or `Perm`. \nPlease assure that your time variables are: `s` for seconds, `m` for minutes, `h` for hours, and `d` for days. Ex: `7d`')
                return
        if role.id == 967619220047278150:
            permanent_variable = ("none", "na", "n/a", "None", "Na", "NA", "N/A", "p", "P", "Permanent", "permanent", "perm", "Perm")
            try:
                if time in permanent_variable:
                    await member.add_roles(role)
                    await interaction.response.send_message(f"I've added {role} to {member} permanently!", ephemeral=True)
                    return
                else:
                    try:
                        time_list = re.split('(\d+)',time)
                        if time_list[2] == "s":
                            time_in_s = int(time_list[1])
                        if time_list[2] == "m":
                            time_in_s = int(time_list[1]) * 60
                        if time_list[2] == "h":
                            time_in_s = int(time_list[1]) * 60 * 60
                        if time_list[2] == "d":
                            time_in_s = int(time_list[1]) * 60 * 60 * 24
    
                        x = datetime.now() + timedelta(seconds=time_in_s)
                        timestamp = x.timestamp()

                        db = await aiosqlite.connect('database.db')
                        cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("Crypto", timestamp, member.id))

                        await member.add_roles(role)

                        await interaction.response.send_message(f"I've added {role} to {member} for {time}!", ephemeral=True)
                        await db.commit()
                        await db.close()
                        return
                    except:
                        await interaction.response.send_message('An error occured. Please assure that your time variables are: `s` for seconds, `m` for minutes, `h` for hours, and `d` for days. Ex: `7d`', ephemeral=True)
                        return
            except:
                await interaction.response.send_message('An error occured. \nPlease assure your permanent variables are one of the following: `none`, `na`, `n/a`, `None`, `Na`, `NA`, `N/A`, `p`, `P`, `Permanent`, `permanent`, `perm` or `Perm`. \nPlease assure that your time variables are: `s` for seconds, `m` for minutes, `h` for hours, and `d` for days. Ex: `7d`')
                return
        if role.id == 967619199289671710:
            permanent_variable = ("none", "na", "n/a", "None", "Na", "NA", "N/A", "p", "P", "Permanent", "permanent", "perm", "Perm")
            try:
                if time in permanent_variable:
                    await member.add_roles(role)
                    await interaction.response.send_message(f"I've added {role} to {member} permanently!", ephemeral=True)
                    return
                else:
                    try:
                        time_list = re.split('(\d+)',time)
                        if time_list[2] == "s":
                            time_in_s = int(time_list[1])
                        if time_list[2] == "m":
                            time_in_s = int(time_list[1]) * 60
                        if time_list[2] == "h":
                            time_in_s = int(time_list[1]) * 60 * 60
                        if time_list[2] == "d":
                            time_in_s = int(time_list[1]) * 60 * 60 * 24
    
                        x = datetime.now() + timedelta(seconds=time_in_s)
                        timestamp = x.timestamp()

                        db = await aiosqlite.connect('database.db')
                        cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("NFT", timestamp, member.id))

                        await member.add_roles(role)

                        await interaction.response.send_message(f"I've added {role} to {member} for {time}!", ephemeral=True)
                        await db.commit()
                        await db.close()
                        return
                    except:
                        await interaction.response.send_message('An error occured. Please assure that your time variables are: `s` for seconds, `m` for minutes, `h` for hours, and `d` for days. Ex: `7d`', ephemeral=True)
                        return
            except:
                await interaction.response.send_message('An error occured. \nPlease assure your permanent variables are one of the following: `none`, `na`, `n/a`, `None`, `Na`, `NA`, `N/A`, `p`, `P`, `Permanent`, `permanent`, `perm` or `Perm`. \nPlease assure that your time variables are: `s` for seconds, `m` for minutes, `h` for hours, and `d` for days. Ex: `7d`')
                return
        else:
            await interaction.response.send_message("I don't have that role configured yet!", ephemeral=True)

@tasks.loop(seconds = 30)
async def roleLoop():
    await client.wait_until_ready()
    guild = client.get_guild(962895434014154853)
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('SELECT time_expired, user_ids, role FROM roles')
    a = await cursor.fetchall()
    for row in a:
        await asyncio.sleep(1)
        if row[0] == 'null':
            continue
        if row[0] == 'expired':
            continue
        if row[0] <= DT.datetime.now().timestamp():
            if row[2] == 'NFT':
                nft = discord.utils.get(guild.roles, id=967619199289671710)
                cursor = await db.execute('UPDATE roles SET time_expired=? WHERE time_expired=?', ('expired', row[0]))
                await db.commit()
                member = guild.get_member(row[1])
                await member.remove_roles(nft)
                cursor = await db.execute('SELECT * FROM roles')
                logs = client.get_channel(967935877089226804)
                await logs.send(f"{row[1]} had their `NFT` role removed by time expiration.")
            if row[2] == 'Crypto':
                crypto = discord.utils.get(guild.roles, id=967619220047278150)
                cursor = await db.execute('UPDATE roles SET time_expired=? WHERE time_expired=?', ('expired', row[0]))
                await db.commit()
                member = guild.get_member(row[1])
                await member.remove_roles(crypto)
                cursor = await db.execute('SELECT * FROM roles')
                logs = client.get_channel(967935877089226804)
                await logs.send(f"{row[1]} had their `Crypto` role removed by time expiration.")
            if row[2] == 'Arcane':
                arcane = discord.utils.get(guild.roles, id=967619323550109786)
                cursor = await db.execute('UPDATE roles SET time_expired=? WHERE time_expired=?', ('expired', row[0]))
                await db.commit()
                member = guild.get_member(row[1])
                await member.remove_roles(arcane)
                cursor = await db.execute('SELECT * FROM roles')
                logs = client.get_channel(967935877089226804)
                await logs.send(f"{row[1]} had their `Arcane` role removed by time expiration.")
    await db.close()
    await asyncio.sleep(30)

@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return
    nft1 = client.get_channel(967889223665471518)
    nft2 = client.get_channel(967889099732160552)
    nft3 = client.get_channel(967889263821742160)
    crypto1 = client.get_channel(967889377034375200)
    crypto2 = client.get_channel(967889443480567839)
    crypto3 = client.get_channel(967889465412550686)
    if message.channel == nft1:
        await message.delete()
        await message.channel.send("<@&967619199289671710> <@&967619323550109786>", delete_after=1)
        embed = discord.Embed(
            title="",
            description=
            f"{message.content}")
        embed.set_author(name=f"{message.author.name}", icon_url = message.author.avatar.url)
        embed.set_footer(text="discord.gg/signals")
        await message.channel.send(embed=embed)
    if message.channel == nft2:
        await message.delete()
        await message.channel.send("<@&967619199289671710> <@&967619323550109786>", delete_after=1)
        embed = discord.Embed(
            title="",
            description=
            f"{message.content}")
        embed.set_author(name=f"{message.author.name}", icon_url = message.author.avatar.url)
        embed.set_footer(text="discord.gg/signals")
        await message.channel.send(embed=embed)
    if message.channel == nft3:
        await message.delete()
        await message.channel.send("<@&967619199289671710> <@&967619323550109786>", delete_after=1)
        embed = discord.Embed(
            title="",
            description=
            f"{message.content}")
        embed.set_author(name=f"{message.author.name}", icon_url = message.author.avatar.url)
        embed.set_footer(text="discord.gg/signals")
        await message.channel.send(embed=embed)
    if message.channel == crypto1:
        await message.delete()
        await message.channel.send("<@&967619220047278150> <@&967619323550109786>", delete_after=1)
        embed = discord.Embed(
            title="",
            description=
            f"{message.content}")
        embed.set_author(name=f"{message.author.name}", icon_url = message.author.avatar.url)
        embed.set_footer(text="discord.gg/signals")
        await message.channel.send(embed=embed)
    if message.channel == crypto2:
        await message.delete()
        await message.channel.send("<@&967619220047278150> <@&967619323550109786>", delete_after=1)
        embed = discord.Embed(
            title="",
            description=
            f"{message.content}")
        embed.set_author(name=f"{message.author.name}", icon_url = message.author.avatar.url)
        embed.set_footer(text="discord.gg/signals")
        await message.channel.send(embed=embed)
    if message.channel == crypto3:
        await message.delete()
        await message.channel.send("<@&967619220047278150> <@&967619323550109786>", delete_after=1)
        embed = discord.Embed(
            title="",
            description=
            f"{message.content}")
        embed.set_author(name=f"{message.author.name}", icon_url = message.author.avatar.url)
        embed.set_footer(text="discord.gg/signals")
        await message.channel.send(embed=embed)
    await client.process_commands(message)








#\\\\\\\\\\\\\\\\\\ONLY USE IF YOU NEED TO RESET THE DATABASE//////////////////

#@client.command()
#@commands.has_permissions(administrator=True)
#async def nftsdatabase(ctx):
#    db = await aiosqlite.connect('database.db')
#    cursor = await db.execute("""
#   CREATE TABLE nfts (
#        uniqid TEXT
#    )""")
#    row = await cursor.fetchone()
#    rows = await cursor.fetchall()
#    await cursor.close()
#    cursor = await db.execute('INSERT INTO nfts VALUES (?);', ("d1b7c8-d6453894f5-d6a218", ))
#    await db.commit()
#    await db.close()
#    a = await ctx.reply('Done!')
#    await asyncio.sleep(5)
#    await a.delete()
#    await ctx.message.delete()

#@client.command()
#@commands.has_permissions(administrator=True)
#async def rolesdatabase(ctx):
#    db = await aiosqlite.connect('database.db')
#    cursor = await db.execute("""
#   CREATE TABLE roles (
#        role TEXT,
#        time_expired INTEGER,
#        user_ids INTEGER
#    )""")
#    row = await cursor.fetchone()
#    rows = await cursor.fetchall()
#    await cursor.close()
#    await db.commit()
#    await db.close()
#    a = await ctx.reply('Done!')
#    await asyncio.sleep(5)
#    await a.delete()
#    await ctx.message.delete()

"""@client.command()
@commands.is_owner()
async def deleteroles(ctx):
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('DROP TABLE roles;')
    await db.commit()
    await db.close()
    a = await ctx.reply('Done!')
    await asyncio.sleep(5)
    await ctx.message.delete()
    await a.delete()"""

"""@client.command()
@commands.has_permissions(administrator=True)
async def deletenfts(ctx):
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('DROP TABLE nfts;')
    await db.commit()
    await db.close()
    a = await ctx.reply('Done!')
    await asyncio.sleep(5)
    await ctx.message.delete()
    await a.delete()"""

#\\\\\\\\\\\\\\\\\\ARCHIVE (FOR TESTS)//////////////////

"""try:
    response = apiclient.get_orders()
    emails = [item['customer_email'] for item in response]
    new_dict = dict(zip(emails, response)) 
    xmails = emails[:1]
    discord_id = [item['custom_fields'] for item in response]
    xdiscord = discord_id[:1]
    print(*xmails)
    d_id = [item['discord_id'] for item in xdiscord]
    print(*d_id)
    unid = [item['uniqid'] for item in response]
    uniq_id = unid[:1]
    print(*uniq_id)
    unid = [item['product_title'] for item in response]
    uniq_id = unid[:1]
    print(*uniq_id)
except Sellix.SellixException as e:
    print(e)"""

client.run('')
