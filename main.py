import discord
import datetime as DT
import asyncio
import re
import aiosqlite
import json
import pytz
import os

from discord import Client, app_commands
from discord.ext.commands import has_permissions, MissingPermissions, CommandNotFound, MemberConverter
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

class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='How much do I need to start?'),
            discord.SelectOption(label='I have no experience, can I still do it?'),
            discord.SelectOption(label='How frequent are the signals?'),
            discord.SelectOption(label='What are signals?'),
            discord.SelectOption(label="I just purchased but I haven't gotten my rank!"),
            discord.SelectOption(label="I can no longer see any of the signal channels!"),
            discord.SelectOption(emoji='📩', label='My question is not there, help me!')
        ]
        super().__init__(placeholder='Choose your option!', min_values=1, max_values=1, options=options, custom_id='dropdownview:1')

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "How much do I need to start?":
            await interaction.response.send_message('1-2 solana is ideal (roughly $75 - $150)', ephemeral=True)
            return
        if self.values[0] == "I have no experience, can I still do it?":
            await interaction.response.send_message("We will walk you through it all from A to Z and it is much easier than you think. (We had a member who didn't know what an NFT was make $900 in his first day)", ephemeral=True)
            return
        if self.values[0] == "How frequent are the signals?":
            await interaction.response.send_message("Usually 1-3 a day, there is always money to be made!", ephemeral=True)
            return
        if self.values[0] == "What are signals?":
            await interaction.response.send_message("Trading signals are triggers to buy or sell a security based on a pre-determined set of criteria. They can also be used to reconstitute a portfolio and shift sector allocations or take new positions.", ephemeral=True)
            return
        if self.values[0] == "I just purchased but I haven't gotten my rank!":
            await interaction.response.send_message("Please wait 1-2 hours after purchasing if you still haven't received your rank make a ticket.", ephemeral=True)
            return
        if self.values[0] == "I can no longer see any of the signal channels!":
            await interaction.response.send_message("That is most likely because your subscription has ran out please consider extending your subscription at https://arcane.cx/ if this is not the case open a ticket", ephemeral=True)
            return
        if self.values[0] == "My question is not there, help me!":
            creatingmessage = await interaction.response.send_message('The ticket is being created...', ephemeral=True)

            with open("data.json") as f:
                data = json.load(f)
        
            db = await aiosqlite.connect('database.db')
            cursor = await db.execute('SELECT ticket FROM counter')
            rows = await cursor.fetchone()
            await db.execute('UPDATE counter SET ticket=ticket + ?', (1,))
            await db.commit()

            category_channel = interaction.guild.get_channel(973038474334703656)
            ticket_channel = await category_channel.create_text_channel(
                f"ticket-{rows[0]}")
            await ticket_channel.set_permissions(interaction.guild.get_role(interaction.guild.id),
                                         send_messages=False,
                                         read_messages=False)

            for role_id in data["valid-roles"]:
                role = interaction.guild.get_role(role_id)
            
                await ticket_channel.set_permissions(role,
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                read_message_history=True,
                                                external_emojis=True)
        
            await ticket_channel.set_permissions(interaction.user,
                                                send_messages=True,
                                                read_messages=True,
                                                add_reactions=True,
                                                embed_links=True,
                                                attach_files=True,
                                                read_message_history=True,
                                                external_emojis=True)

            await interaction.edit_original_message(content=f'The ticket has been created at {ticket_channel.mention}.')

            def check(message):
                return message.channel == ticket_channel and message.author == interaction.user

            x = f'{interaction.user.mention}'

            view = TicketClose()

            a = discord.Embed(title="Question 1",
                                description=f"What do you need support with?",
                                color=discord.Color.purple())

            a.set_footer(text='Click the 🔒 button to close the ticket!')

            await ticket_channel.send(content=x, embed=a, view=view)

            question1 = await client.wait_for('message', check=check)

            b = discord.Embed(title="Question 2",
                                description=f"What is your order ID? (Reply with none if you have none)",
                                color=discord.Color.purple())

            await ticket_channel.send(embed=b)

            question2 = await client.wait_for('message', check=check)

      
            embed=discord.Embed(title="", 
            description=f"Support will be with you shortly! \nThis ticket will close in 24 hours of inactivity.", 
            color=discord.Color.green())

            em = discord.Embed(title="Responses",
                                description=f"**Issue**: {question1.content} \n**Order ID**: {question2.content}",
                                color=discord.Color.green())

            em.set_footer(text="Close this ticket by clicking the 🔒 button.")   

            view = TicketClose()

            supportping = '<@&973038661341941780>'

            await ticket_channel.send(content=supportping, embeds=[embed, em], view=view)

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        super().__init__(timeout=None)
        self.add_item(Dropdown())    

class TicketClose(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(emoji='🔒', style=discord.ButtonStyle.gray, custom_id='ticketclose')
    async def ticketclose(self, interaction: discord.Interaction, button: discord.ui.Button):
        council = discord.utils.get(interaction.guild.roles,name='The Council')
        creator = discord.utils.get(interaction.guild.roles,name='The Creator')

        msg = [interaction.message async for interaction.message in interaction.channel.history(oldest_first=True, limit=1)]

        x = msg[0].mentions[0].id
        y = msg[0].mentions[0]

        if x == interaction.user.id:

            await interaction.channel.set_permissions(interaction.user,
                                         send_messages=False,
                                         read_messages=False,
                                         add_reactions=False,
                                         embed_links=False,
                                         attach_files=False,
                                         read_message_history=False,
                                         external_emojis=False)

            closed = discord.utils.get(interaction.guild.channels, name="Closed Tickets")
            await interaction.channel.edit(category=closed)

            view = AdminTicket()
            embed = discord.Embed(
                title="",
                description=
                f"Ticket Closed by {interaction.user.mention}",
                color=discord.Color.red())
            await interaction.channel.send(embed=embed, view=view)
            await interaction.response.send_message('Successfully closed the ticket!', ephemeral=True)
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(view=self)
            return

        else:

            await interaction.response.send_message('Closing the ticket...', ephemeral=True)

            await interaction.channel.set_permissions(y,
                                         send_messages=False,
                                         read_messages=False,
                                         add_reactions=False,
                                         embed_links=False,
                                         attach_files=False,
                                         read_message_history=False,
                                         external_emojis=False)

            closed = discord.utils.get(interaction.guild.channels, name="Closed Tickets")
            await interaction.channel.edit(category=closed)

            view = AdminTicket()
            embed = discord.Embed(
                title="",
                description=
                f"Ticket Closed by {interaction.user.mention}",
                color=discord.Color.red())
            await interaction.channel.send(embed=embed, view=view)
            await interaction.response.send_message('Successfully closed the ticket!', ephemeral=True)
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(view=self)
            return

class AdminTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red, custom_id='adminticketclose')
    async def adminticketoclose(self, interaction: discord.Interaction, button: discord.ui.Button):
    
            for item in self.children:
                item.disabled = True
            await interaction.message.edit(view=self)

            with open('data.json') as f:
                data = json.load(f)

            channel_id = interaction.channel_id

            with open("file.txt", "w", encoding="utf-8") as file:
                msg = [interaction.message async for interaction.message in interaction.channel.history(oldest_first=True, limit=1)]
                y = msg[0].mentions[0]
                async for message in interaction.channel.history(limit=None, oldest_first=True):
                    time = datetime.now(tz=pytz.timezone('America/Tijuana'))
                    formatted = time.strftime("%I:%M %p")
                    msgtime = message.created_at.strftime("%m/%d/%y, %I:%M %p")
                    file.write(str(f"({msgtime}) [{message.author}]: {message.content}" + "\n"))
                file.write(f"\nEnd of ticket log. \n============================================================================== \nServer Name: {interaction.guild.name} \nChannel Name: {interaction.channel.name} \n \n*If a message is from a bot, and appears empty, its because the bot sent a message with no text, only an embed. \n==============================================================================")

            with open("file.txt", "rb") as file:
                transcripts = interaction.guild.get_channel(972657586384031774)
                msg = await discord.utils.get(interaction.channel.history(oldest_first=True, limit=1))
                
                time = pytz.timezone('America/Tijuana')
                created_at = msg.created_at
                now = datetime.now(time)
                maths = now - created_at
                seconds = maths.total_seconds()
                math = round(seconds)

                embed = discord.Embed(
                    title=f"Ticket Closed!",
                    description=
                    f"├ **Channel Name:** {interaction.channel.name} \n├ **Opened By:** {y.mention} \n├ **Opened ID:** {y.id} \n├ **Closed By:** {interaction.user.mention} \n├ **Closed ID:** {interaction.user.id} \n└ **Time Opened:** {math} Seconds",
                color=0x202225)
                await transcripts.send(embed=embed)
                await transcripts.send(file=discord.File(file, f"{interaction.channel.name}.txt"))

            try:
                with open("file.txt", "rb") as file:
                    msg = await discord.utils.get(interaction.channel.history(oldest_first=True, limit=1))
                
                    time = pytz.timezone('America/Tijuana')
                    created_at = msg.created_at
                    now = datetime.now(time)
                    maths = now - created_at
                    seconds = maths.total_seconds()
                    math = round(seconds)

                    embed = discord.Embed(
                        title=f"Ticket Closed!",
                        description=
                        f"├ **Channel Name:** {interaction.channel.name} \n├ **Opened By:** {y.mention} \n├ **Opened ID:** {y.id} \n├ **Closed By:** {interaction.user.mention} \n├ **Closed ID:** {interaction.user.id} \n└ **Time Opened:** {math} Seconds",
                    color=0x202225)
                    await y.send(file=discord.File(file, f"{interaction.channel.name}.txt"))
            except:
                pass

            await interaction.response.send_message('Ticket will close in 15 seconds.', ephemeral=True)
            await asyncio.sleep(15)
            await interaction.channel.delete()

            with open('data.json', 'w') as f:
                json.dump(data, f)

    @discord.ui.button(label="Open", style=discord.ButtonStyle.green, custom_id='adminticketopen')
    async def adminticketopen(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        msg = [interaction.message async for interaction.message in interaction.channel.history(oldest_first=True, limit=1)]
        x = msg[0].mentions[0].id
        y = msg[0].mentions[0]

        await interaction.channel.set_permissions(y,
                                         send_messages=True,
                                         read_messages=True,
                                         add_reactions=True,
                                         embed_links=True,
                                         attach_files=True,
                                         read_message_history=True,
                                         external_emojis=True)
        
        closed = discord.utils.get(interaction.guild.channels, name="Open Tickets")
        await interaction.channel.edit(category=closed)

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)
        x = f'{interaction.user.mention}'
        embed=discord.Embed(title="", 
        description=f"Ticket Opened by {interaction.user.mention}", 
        color=discord.Color.green())
        
        await interaction.response.send_message('Successfully opened the ticket!', ephemeral=True)

        view = TicketClose()

        await interaction.channel.send(content=x, embed=embed, view=view)

watching = discord.Activity(type=discord.ActivityType.watching, name="arcane.cx")
class PersistentViewBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('.'), owner_id=503641822141349888, intents=intents, activity=watching, status=discord.Status.dnd)
        self.persistent_views_added = False

    async def on_ready(self):
        if not self.persistent_views_added:
            self.add_view(PersistentView())
            self.add_view(DropdownView())
            self.add_view(TicketClose())
            self.add_view(AdminTicket())
            self.persistent_views_added = True

        print(f'Signed in as {self.user}')

        await self.tree.sync(guild=discord.Object(id=962895434014154853))

    async def setup_hook(self):
        purchasesLoop.start()
        roleLoop.start()

client = PersistentViewBot()

apiclient = Sellix("", "signals")

@client.tree.command(guild=discord.Object(id=962895434014154853), description="Add time to a subscription!")
@app_commands.describe(member='Member to add subscription time to!')
@app_commands.describe(role='Which role do you want to add time to?')
@app_commands.describe(role='How long do you want to add to it?')
async def subadd(interaction: discord.Interaction, member: discord.Member, role: discord.Role, time: str):
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('SELECT time_expired, user_ids, role FROM roles')
    a = await cursor.fetchall()
    
    role1 = interaction.guild.get_role(967619323550109786)
    role2 = interaction.guild.get_role(967619220047278150)
    role3 = interaction.guild.get_role(967619199289671710)

    role_variable = (role1, role2, role3)
    if role in role_variable:
        for row in a:
            await asyncio.sleep(1)
            if row[1] == member.id:
                if row[2] == "Arcane":
                    if role1 == role:
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
                            oldtimestamp = row[0]
                            x = datetime.fromtimestamp(oldtimestamp)
                            y = x + timedelta(seconds=time_in_s)
                            timestamp = y.timestamp()
                            await db.execute('UPDATE roles SET time_expired=? WHERE user_ids=? AND time_expired=? AND role=?', (timestamp, member.id, oldtimestamp, "Arcane"))
                            await interaction.response.send_message(f"I've added {time} to {member.mention}'s {role} time.", ephemeral=True)
                        except:
                            await interaction.response.send_message('An error occured.', ephemeral=True)
                    else:
                        pass
                if row[2] == "Crypto":
                    if role2 == role:
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
                            oldtimestamp = row[0]
                            x = datetime.fromtimestamp(oldtimestamp)
                            y = x + timedelta(seconds=time_in_s)
                            timestamp = y.timestamp()
                            await db.execute('UPDATE roles SET time_expired=? WHERE user_ids=? AND time_expired=? AND role=?', (timestamp, member.id, oldtimestamp, "Crypto"))
                            await interaction.response.send_message(f"I've added {time} to {member.mention}'s {role} time.", ephemeral=True)
                        except:
                            await interaction.response.send_message('An error occured.', ephemeral=True)
                if row[2] == "NFT":
                    if role3 == role:
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
                            oldtimestamp = row[0]
                            x = datetime.fromtimestamp(oldtimestamp)
                            y = x + timedelta(seconds=time_in_s)
                            timestamp = y.timestamp()
                            await db.execute('UPDATE roles SET time_expired=? WHERE user_ids=? AND time_expired=? AND role=?', (timestamp, member.id, oldtimestamp, "NFT"))
                            await interaction.response.send_message(f"I've added {time} to {member.mention}'s {role} time.", ephemeral=True)
                        except:
                            await interaction.response.send_message('An error occured.', ephemeral=True)
                else:
                    await interaction.response.send_message("That user doesn't have the Arcane, Crypto, or NFT role available.", ephemeral=True)
    else:
        await interaction.response.send_message(f"That role isn't available!", ephemeral=True)
    await db.commit()
    await db.close()

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
        cursor2 = await db.execute('SELECT role, time_expired, user_ids FROM roles')
        b = await cursor2.fetchall()
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
                    cursor3 = await db.execute('SELECT user_ids FROM roles WHERE user_ids=?', (d_id[0], ))
                    c = await cursor3.fetchone()
                    cursor4 = await db.execute('SELECT time_expired FROM roles WHERE user_ids=?', (d_id[0], ))
                    d = await cursor4.fetchone()
                    if c is not None:
                        await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`. The subscription time has been updated.')
                        cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                        cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                        try:
                            if d_id[0].isdigit():
                                member = await guild.fetch_member(d_id[0])
                                oldtimestamp = d[0]
                                ots = datetime.fromtimestamp(oldtimestamp)
                                y = ots + timedelta(seconds=604800)
                                timestamp = y.timestamp()
                                await db.execute('UPDATE roles SET time_expired=? WHERE user_ids=? AND time_expired=?', (timestamp, d_id[0], oldtimestamp))
                                nft = discord.utils.get(guild.roles, id=967619199289671710)
                                await member.add_roles(nft)
                                continue
                            else:
                                member = guild.get_member_named(d_id[0])
                                x = datetime.now() + timedelta(seconds=604800)
                                timestamp = x.timestamp()
                                await db.execute('UPDATE roles SET time_expired=? WHERE user_ids=? AND time_expired=?', (timestamp, d_id[0], oldtimestamp))
                                nft = discord.utils.get(guild.roles, id=967619199289671710)
                                await member.add_roles(nft)
                                continue
                        except:
                            continue
                    else:
                        await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`. A role has been added for the first time.')
                        cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                        cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                        try:
                            if d_id[0].isdigit():
                                member = await guild.fetch_member(d_id[0])
                                x = datetime.now() + timedelta(seconds=604800)
                                timestamp = x.timestamp()
                                cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("NFT", timestamp, d_id[0]))
                                nft = discord.utils.get(guild.roles, id=967619199289671710)
                                await member.add_roles(nft)
                                continue
                            else:
                                member = guild.get_member_named(d_id[0])
                                x = datetime.now() + timedelta(seconds=604800)
                                timestamp = x.timestamp()
                                cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("NFT", timestamp, d_id[0]))
                                nft = discord.utils.get(guild.roles, id=967619199289671710)
                                await member.add_roles(nft)
                                continue
                        except:
                            continue
                #CHECK FOR 1 MONTH NFT PURCHASE
                if product_title[0] == "1 Month ( NFT )":
                    cursor3 = await db.execute('SELECT user_ids FROM roles WHERE user_ids=?', (d_id[0], ))
                    c = await cursor3.fetchone()
                    cursor4 = await db.execute('SELECT time_expired FROM roles WHERE user_ids=?', (d_id[0], ))
                    d = await cursor4.fetchone()
                    if c is not None:
                        await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`. The subscription time has been updated.')
                        cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                        cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                        try:
                            if d_id[0].isdigit():
                                member = await guild.fetch_member(d_id[0])
                                oldtimestamp = d[0]
                                ots = datetime.fromtimestamp(oldtimestamp)
                                y = ots + timedelta(seconds=2592000)
                                timestamp = y.timestamp()
                                await db.execute('UPDATE roles SET time_expired=? WHERE user_ids=? AND time_expired=?', (timestamp, d_id[0], oldtimestamp))
                                nft = discord.utils.get(guild.roles, id=967619199289671710)
                                await member.add_roles(nft)
                                continue
                            else:
                                member = guild.get_member_named(d_id[0])
                                x = datetime.now() + timedelta(seconds=2592000)
                                timestamp = x.timestamp()
                                await db.execute('UPDATE roles SET time_expired=? WHERE user_ids=? AND time_expired=?', (timestamp, d_id[0], oldtimestamp))
                                nft = discord.utils.get(guild.roles, id=967619199289671710)
                                await member.add_roles(nft)
                                continue
                        except:
                            continue
                    else:
                        await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`. A role has been added for the first time.')
                        cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                        cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                        try:
                            if d_id[0].isdigit():
                                member = await guild.fetch_member(d_id[0])
                                x = datetime.now() + timedelta(seconds=2592000)
                                timestamp = x.timestamp()
                                cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("NFT", timestamp, d_id[0]))
                                nft = discord.utils.get(guild.roles, id=967619199289671710)
                                await member.add_roles(nft)
                                continue
                            else:
                                member = guild.get_member_named(d_id[0])
                                x = datetime.now() + timedelta(seconds=2592000)
                                timestamp = x.timestamp()
                                cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("NFT", timestamp, d_id[0]))
                                nft = discord.utils.get(guild.roles, id=967619199289671710)
                                await member.add_roles(nft)
                                continue
                        except:
                            continue
                #CHECK FOR LIFETIME NFT PURCHASE
                if product_title[0] == "Lifetime ( NFT )":
                    await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`.')
                    cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                    cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                    try:
                        if d_id[0].isdigit():
                            member = await guild.fetch_member(d_id[0])
                            nft = discord.utils.get(guild.roles, id=967619199289671710)
                            await member.add_roles(nft)
                            continue
                        else:
                            member = guild.get_member_named(d_id[0])
                            nft = discord.utils.get(guild.roles, id=967619199289671710)
                            await member.add_roles(nft)
                            continue
                    except:
                        continue
                #CHECK FOR 1 WEEK CRYPTO PURCHASE
                if product_title[0] == "1 Week ( Crypto )":
                    cursor3 = await db.execute('SELECT user_ids FROM roles WHERE user_ids=?', (d_id[0], ))
                    c = await cursor3.fetchone()
                    cursor4 = await db.execute('SELECT time_expired FROM roles WHERE user_ids=?', (d_id[0], ))
                    d = await cursor4.fetchone()
                    if c is not None:
                        await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`. The subscription time has been updated.')
                        cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                        cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                        try:
                            if d_id[0].isdigit():
                                member = await guild.fetch_member(d_id[0])
                                oldtimestamp = d[0]
                                ots = datetime.fromtimestamp(oldtimestamp)
                                y = ots + timedelta(seconds=604800)
                                timestamp = y.timestamp()
                                await db.execute('UPDATE roles SET time_expired=? WHERE user_ids=? AND time_expired=?', (timestamp, d_id[0], oldtimestamp))
                                crypto = discord.utils.get(guild.roles, id=967619220047278150)
                                await member.add_roles(crypto)
                                continue
                            else:
                                member = guild.get_member_named(d_id[0])
                                x = datetime.now() + timedelta(seconds=604800)
                                timestamp = x.timestamp()
                                await db.execute('UPDATE roles SET time_expired=? WHERE user_ids=? AND time_expired=?', (timestamp, d_id[0], oldtimestamp))
                                crypto = discord.utils.get(guild.roles, id=967619220047278150)
                                await member.add_roles(crypto)
                                continue
                        except:
                            continue
                    else:
                        await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`. A role has been added for the first time.')
                        cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                        cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                        try:
                            if d_id[0].isdigit():
                                member = await guild.fetch_member(d_id[0])
                                x = datetime.now() + timedelta(seconds=604800)
                                timestamp = x.timestamp()
                                cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("Crypto", timestamp, d_id[0]))
                                crypto = discord.utils.get(guild.roles, id=967619220047278150)
                                await member.add_roles(crypto)
                                continue
                            else:
                                member = guild.get_member_named(d_id[0])
                                x = datetime.now() + timedelta(seconds=604800)
                                timestamp = x.timestamp()
                                cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("Crypto", timestamp, d_id[0]))
                                crypto = discord.utils.get(guild.roles, id=967619220047278150)
                                await member.add_roles(crypto)
                                continue
                        except:
                            continue
                #CHECK FOR 1 MONTH CRYPTO PURCHASE
                if product_title[0] == "1 Month ( Crypto )":
                    cursor3 = await db.execute('SELECT user_ids FROM roles WHERE user_ids=?', (d_id[0], ))
                    c = await cursor3.fetchone()
                    cursor4 = await db.execute('SELECT time_expired FROM roles WHERE user_ids=?', (d_id[0], ))
                    d = await cursor4.fetchone()
                    if c is not None:
                        await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`. The subscription time has been updated.')
                        cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                        cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                        try:
                            if d_id[0].isdigit():
                                member = await guild.fetch_member(d_id[0])
                                oldtimestamp = d[0]
                                ots = datetime.fromtimestamp(oldtimestamp)
                                y = ots + timedelta(seconds=2592000)
                                timestamp = y.timestamp()
                                await db.execute('UPDATE roles SET time_expired=? WHERE user_ids=? AND time_expired=?', (timestamp, d_id[0], oldtimestamp))
                                crypto = discord.utils.get(guild.roles, id=967619220047278150)
                                await member.add_roles(crypto)
                                continue
                            else:
                                member = guild.get_member_named(d_id[0])
                                x = datetime.now() + timedelta(seconds=2592000)
                                timestamp = x.timestamp()
                                await db.execute('UPDATE roles SET time_expired=? WHERE user_ids=? AND time_expired=?', (timestamp, d_id[0], oldtimestamp))
                                crypto = discord.utils.get(guild.roles, id=967619220047278150)
                                await member.add_roles(crypto)
                                continue
                        except:
                            continue
                    else:
                        await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`. A role has been added for the first time.')
                        cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                        cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                        try:
                            if d_id[0].isdigit():
                                member = await guild.fetch_member(d_id[0])
                                x = datetime.now() + timedelta(seconds=2592000)
                                timestamp = x.timestamp()
                                cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("Crypto", timestamp, d_id[0]))
                                crypto = discord.utils.get(guild.roles, id=967619199289671710)
                                await member.add_roles(crypto)
                                continue
                            else:
                                member = guild.get_member_named(d_id[0])
                                x = datetime.now() + timedelta(seconds=2592000)
                                timestamp = x.timestamp()
                                cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("Crypto", timestamp, d_id[0]))
                                crypto = discord.utils.get(guild.roles, id=967619199289671710)
                                await member.add_roles(crypto)
                                continue
                        except:
                            continue
                #CHECK FOR LIFETIME CRYPTO PURCHASE
                if product_title[0] == "Lifetime ( Crypto )":
                    await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`.')
                    cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                    cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                    try:
                        if d_id[0].isdigit():
                            member = await guild.fetch_member(d_id[0])
                            crypto = discord.utils.get(guild.roles, id=967619220047278150)
                            await member.add_roles(crypto)
                            continue
                        else:
                            member = guild.get_member_named(d_id[0])
                            crypto = discord.utils.get(guild.roles, id=967619220047278150)
                            await member.add_roles(crypto)
                            continue
                    except:
                        continue
                #CHECK FOR 1 WEEK ARCANE PURCHASE
                if product_title[0] == "1 Week ( Arcane )":
                    cursor3 = await db.execute('SELECT user_ids FROM roles WHERE user_ids=?', (d_id[0], ))
                    c = await cursor3.fetchone()
                    cursor4 = await db.execute('SELECT time_expired FROM roles WHERE user_ids=?', (d_id[0], ))
                    d = await cursor4.fetchone()
                    if c is not None:
                        await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`. The subscription time has been updated.')
                        cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                        cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                        try:
                            if d_id[0].isdigit():
                                member = await guild.fetch_member(d_id[0])
                                oldtimestamp = d[0]
                                ots = datetime.fromtimestamp(oldtimestamp)
                                y = ots + timedelta(seconds=604800)
                                timestamp = y.timestamp()
                                await db.execute('UPDATE roles SET time_expired=? WHERE user_ids=? AND time_expired=?', (timestamp, d_id[0], oldtimestamp))
                                arcane = discord.utils.get(guild.roles, id=967619323550109786)
                                await member.add_roles(arcane)
                                continue
                            else:
                                member = guild.get_member_named(d_id[0])
                                x = datetime.now() + timedelta(seconds=604800)
                                timestamp = x.timestamp()
                                await db.execute('UPDATE roles SET time_expired=? WHERE user_ids=? AND time_expired=?', (timestamp, d_id[0], oldtimestamp))
                                arcane = discord.utils.get(guild.roles, id=967619323550109786)
                                await member.add_roles(arcane)
                                continue
                        except:
                            continue
                    else:
                        await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`. A role has been added for the first time.')
                        cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                        cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                        try:
                            if d_id[0].isdigit():
                                member = await guild.fetch_member(d_id[0])
                                x = datetime.now() + timedelta(seconds=604800)
                                timestamp = x.timestamp()
                                cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("Arcane", timestamp, d_id[0]))
                                arcane = discord.utils.get(guild.roles, id=967619323550109786)
                                await member.add_roles(arcane)
                                continue
                            else:
                                member = guild.get_member_named(d_id[0])
                                x = datetime.now() + timedelta(seconds=604800)
                                timestamp = x.timestamp()
                                cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("Arcane", timestamp, d_id[0]))
                                arcane = discord.utils.get(guild.roles, id=967619323550109786)
                                await member.add_roles(arcane)
                                continue
                        except:
                            continue
                #CHECK FOR 1 MONTH ARCANE PURCHASE
                if product_title[0] == "1 Month ( Arcane )":
                    cursor3 = await db.execute('SELECT user_ids FROM roles WHERE user_ids=?', (d_id[0], ))
                    c = await cursor3.fetchone()
                    cursor4 = await db.execute('SELECT time_expired FROM roles WHERE user_ids=?', (d_id[0], ))
                    d = await cursor4.fetchone()
                    if c is not None:
                        await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`. The subscription time has been updated.')
                        cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                        cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                        try:
                            if d_id[0].isdigit():
                                member = await guild.fetch_member(d_id[0])
                                oldtimestamp = d[0]
                                ots = datetime.fromtimestamp(oldtimestamp)
                                y = ots + timedelta(seconds=2592000)
                                timestamp = y.timestamp()
                                await db.execute('UPDATE roles SET time_expired=? WHERE user_ids=? AND time_expired=?', (timestamp, d_id[0], oldtimestamp))
                                arcane = discord.utils.get(guild.roles, id=967619323550109786)
                                await member.add_roles(arcane)
                                continue
                            else:
                                member = guild.get_member_named(d_id[0])
                                x = datetime.now() + timedelta(seconds=2592000)
                                timestamp = x.timestamp()
                                await db.execute('UPDATE roles SET time_expired=? WHERE user_ids=? AND time_expired=?', (timestamp, d_id[0], oldtimestamp))
                                arcane = discord.utils.get(guild.roles, id=967619323550109786)
                                await member.add_roles(arcane)
                                continue
                        except:
                            continue
                    else:
                        await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`. A role has been added for the first time.')
                        cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                        cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                        try:
                            if d_id[0].isdigit():
                                member = await guild.fetch_member(d_id[0])
                                x = datetime.now() + timedelta(seconds=2592000)
                                timestamp = x.timestamp()
                                cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("Arcane", timestamp, d_id[0]))
                                arcane = discord.utils.get(guild.roles, id=967619323550109786)
                                await member.add_roles(arcane)
                                continue
                            else:
                                member = guild.get_member_named(d_id[0])
                                x = datetime.now() + timedelta(seconds=2592000)
                                timestamp = x.timestamp()
                                cursor = await db.execute('INSERT INTO roles VALUES (?,?,?);', ("Arcane", timestamp, d_id[0]))
                                arcane = discord.utils.get(guild.roles, id=967619323550109786)
                                await member.add_roles(arcane)
                                continue
                        except:
                            continue
                #CHECK FOR LIFETIME ARCANE PURCHASE
                if product_title[0] == "Lifetime ( Arcane )":
                    await logs.send(f'`{xmails[0]}` has purchased `{product_title[0]}`. The ID of the user is `{d_id[0]}`.')
                    cursor = await db.execute('DELETE FROM nfts WHERE uniqid=?', (row[0], ))
                    cursor = await db.execute('INSERT INTO nfts VALUES (?);', (uniq_id[0], ))
                    try:
                        if d_id[0].isdigit():
                            member = await guild.fetch_member(d_id[0])
                            arcane = discord.utils.get(guild.roles, id=967619323550109786)
                            await member.add_roles(arcane)
                            continue
                        else:
                            member = guild.get_member_named(d_id[0])
                            arcane = discord.utils.get(guild.roles, id=967619323550109786)
                            await member.add_roles(arcane)
                            continue
                    except:
                        continue
    except Sellix.SellixException as e:
        print(e)
    await db.commit()
    await db.close()
    await asyncio.sleep(30)

@tasks.loop(seconds = 30)
async def roleLoop():
    await client.wait_until_ready()
    guild = client.get_guild(962895434014154853)
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('SELECT time_expired, user_ids, role FROM roles')
    a = await cursor.fetchall()
    for row in a:
        await asyncio.sleep(1)
        if row[0] == 'expired':
            cursor = await db.execute('DELETE FROM roles WHERE time_expired=?', ('expired',))
            continue
        if row[0] <= DT.datetime.now().timestamp():
            if row[2] == 'NFT':
                nft = discord.utils.get(guild.roles, id=967619199289671710)
                cursor = await db.execute('DELETE FROM roles WHERE time_expired=?', (row[0],))
                try:
                    if row[1].isdigit():
                        member = guild.get_member(row[1])
                        await member.remove_roles(nft)
                        cursor = await db.execute('SELECT * FROM roles')
                        logs = client.get_channel(967935877089226804)
                        await logs.send(f"{row[1]} had their `NFT` role removed by time expiration.")
                    else:
                        member = guild.get_member_named(row[1])
                        await member.remove_roles(nft)
                        cursor = await db.execute('SELECT * FROM roles')
                        logs = client.get_channel(967935877089226804)
                        await logs.send(f"{row[1]} had their `NFT` role removed by time expiration.")
                except:
                    logs = client.get_channel(967935877089226804)
                    await logs.send(f"{row[1]} has failed the removal of the `NFT` role.")
            if row[2] == 'Crypto':
                crypto = discord.utils.get(guild.roles, id=967619220047278150)
                cursor = await db.execute('DELETE FROM roles WHERE time_expired=?', (row[0],))
                try:
                    if row[1].isdigit():
                        member = guild.get_member(row[1])
                        await member.remove_roles(crypto)
                        cursor = await db.execute('SELECT * FROM roles')
                        logs = client.get_channel(967935877089226804)
                        await logs.send(f"{row[1]} had their `Crypto` role removed by time expiration.")
                    else:
                        member = guild.get_member_named(row[1])
                        await member.remove_roles(crypto)
                        cursor = await db.execute('SELECT * FROM roles')
                        logs = client.get_channel(967935877089226804)
                        await logs.send(f"{row[1]} had their `Crypto` role removed by time expiration.")
                except:
                    logs = client.get_channel(967935877089226804)
                    await logs.send(f"{row[1]} has failed the removal of the `NFT` role.")
            if row[2] == 'Arcane':
                arcane = discord.utils.get(guild.roles, id=967619323550109786)
                cursor = await db.execute('DELETE FROM roles WHERE time_expired=?', (row[0],))
                try:
                    if row[1].isdigit():
                        member = guild.get_member(row[1])
                        await member.remove_roles(arcane)
                        cursor = await db.execute('SELECT * FROM roles')
                        logs = client.get_channel(967935877089226804)
                        await logs.send(f"{row[1]} had their `Arcane` role removed by time expiration.")
                    else:
                        member = guild.get_member_named(row[1])
                        await member.remove_roles(arcane)
                        cursor = await db.execute('SELECT * FROM roles')
                        logs = client.get_channel(967935877089226804)
                        await logs.send(f"{row[1]} had their `Arcane` role removed by time expiration.")
                except:
                    logs = client.get_channel(967935877089226804)
                    await logs.send(f"{row[1]} has failed the removal of the `NFT` role.")
    await db.commit()
    await db.close()
    await asyncio.sleep(30)

@client.tree.command(guild=discord.Object(id=962895434014154853), description="Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('{0} ms'.format(round(client.latency, 1)), ephemeral=True)

@client.tree.command(guild=discord.Object(id=962895434014154853), description="Add a role!")
@app_commands.describe(member='Member to add the role to!')
@app_commands.describe(role='Which role do you want to give them?')
@app_commands.describe(time='How long do you want them to have it for?')
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

@client.command()
async def support(ctx):
    if ctx.author.guild_permissions.administrator:
        view = DropdownView()
        embed = discord.Embed(
            title="Signal's Help Desk",
            description=
            f"Welcome to Ardcane Signals! Here you will find FAQ and support tickets. Choose the option that fits your needs.")
        embed.set_footer(text="discord.gg/signals")
        await ctx.message.delete()
        await ctx.send(embed=embed, view=view)
        return
    else:
        a = await ctx.reply("You don't have permission to use this command!")
        await asyncio.sleep(5)
        await a.delete()
        await ctx.message.delete()
        return




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
#    cursor = await db.execute('INSERT INTO nfts VALUES (?);', ("fd9582-66dc2fc73e-d7c3cb", ))
#    await db.commit()
#    await db.close()
#    a = await ctx.reply('Done!')
#    await asyncio.sleep(5)
#    await a.delete()
#    await ctx.message.delete()

@client.command()
@commands.has_permissions(administrator=True)
async def rolesdatabase(ctx):
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute("""
   CREATE TABLE roles (
        role TEXT,
        time_expired INTEGER,
        user_ids INTEGER
    )""")
    row = await cursor.fetchone()
    rows = await cursor.fetchall()
    await cursor.close()
    await db.commit()
    await db.close()
    a = await ctx.reply('Done!')
    await asyncio.sleep(5)
    await a.delete()
    await ctx.message.delete()

#@client.command()
#@commands.has_permissions(administrator=True)
#async def counter(ctx):
#    db = await aiosqlite.connect('database.db')
#    cursor = await db.execute("""
#   CREATE TABLE counter (
#        ticket INTEGER
#    )""")
#    row = await cursor.fetchone()
#    rows = await cursor.fetchall()
#    await cursor.close()
#    cursor = await db.execute('INSERT INTO counter VALUES (?);', (0, ))
#    await db.commit()
#    await db.close()
#    a = await ctx.reply('Done!')
#    await asyncio.sleep(5)
#    await a.delete()
#    await ctx.message.delete()

"""@client.command()
@commands.is_owner()
async def deletecounter(ctx):
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('DROP TABLE counter;')
    await db.commit()
    await db.close()
    a = await ctx.reply('Done!')
    await asyncio.sleep(5)
    await ctx.message.delete()
    await a.delete()"""

@client.command()
@commands.is_owner()
async def deleteroles(ctx):
    db = await aiosqlite.connect('database.db')
    cursor = await db.execute('DROP TABLE roles;')
    await db.commit()
    await db.close()
    a = await ctx.reply('Done!')
    await asyncio.sleep(5)
    await ctx.message.delete()
    await a.delete()

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

"""@client.command()
async def dd(ctx):
    timestamp = 1653616266
    x = datetime.fromtimestamp(timestamp)
    y = x + timedelta(seconds=9)
    a = await ctx.send(f'{x}')
    b = await ctx.send(f'{y}')
    await asyncio.sleep(5)
    await ctx.message.delete()
    await a.delete()
    await b.delete()"""

client.run('')
