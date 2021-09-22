import discord
from discord.ext import commands

import asyncio
from replit import db

class Konsultasi(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def get_cto_member(self, guild):
		member1 = await guild.fetch_member(394083155994214411)
		member2 = await guild.fetch_member(455713207458201602)
		member3 = await guild.fetch_member(833640260910317610)
		member4 = await guild.fetch_member(360798464952500226)
		member5 = await guild.fetch_member(632402909983932416)
		member6 = await guild.fetch_member(631836244921548810)

		member_list = [member1, member2, member3, member4, member5, member6]

		return member_list

	async def get_settings(self, guild_id, channel_id):
		guild = await self.bot.fetch_guild(guild_id)
		channel = guild.get_channel(channel_id)

		try:
			settings = db['settings'][str(guild_id)]
		except KeyError:
			await channel.send('Settings haven\'t been set up on this server!\nSetup for the first time with `c!setup [category ID] [message ID]`')
			return

		return settings[1]

	async def get_cat(self, guild_id, channel_id):
		guild = await self.bot.fetch_guild(guild_id)
		channel = guild.get_channel(channel_id)

		try:
			category_id = int(db['settings'][str(guild_id)][0])
		except KeyError:
			await channel.send('Settings haven\'t been set up on this server!\nSetup for the first time with `c!setup [category ID] [message ID]`')
			return

		return category_id

	async def get_id_konsul(self):
		try:
			id_konsul = int(list(db['konsultasi'].keys())[-1])
		except KeyError:
			return 1

		return id_konsul

	@commands.command(name='setup', aliases=['set'], brief='Setup bot settings for a first time on a server', description='Setup bot settings for a first time on a server')
	@commands.check_any(commands.is_owner(), commands.has_permissions(administrator=True))
	async def setup(self, ctx, categoryID:int=None, messageID:int=None):
		if messageID is not None and categoryID is not None:
			try:
				db['settings'][str(ctx.guild.id)]
			except KeyError:
				try:
					db['settings'][ctx.guild.id] = [categoryID, messageID]
					await ctx.send('Setup successful!', delete_after=5)
					return
				except KeyError:
					db['settings'] = {ctx.guild.id:[categoryID,messageID]}
					await ctx.send('Setup successful!', delete_after=5)
					return

			await ctx.send('The settings on this server have been set up before', delete_after=5)
		else:
			await ctx.send('Correct usage : `c!setup [category ID] [message ID]`', delete_after=8)

	@commands.command(name='pubm', aliases=['pm'], brief='Make a main message', description='Make a main message')
	@commands.check_any(commands.is_owner(), commands.has_permissions(administrator=True))
	async def public_message(self, ctx):
		embed = discord.Embed(title='Konsultasi dengan CTO HMIF ITB!', color=discord.Colour.gold())
		embed.set_footer(text='React dengan emoji 🙋 untuk membuka channel konsultasi!')

		await ctx.message.delete()

		msg = await ctx.send(embed=embed)
		await msg.add_reaction('🙋')

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		channel = await self.bot.fetch_channel(payload.channel_id)

		if str(payload.message_id) == await self.get_settings(payload.guild_id, payload.channel_id) and str(payload.emoji) == '🙋':
			user = await self.bot.fetch_user(payload.user_id)
			guild = await self.bot.fetch_guild(payload.guild_id)
			message = await channel.fetch_message(payload.message_id)
			category = await self.bot.fetch_channel(await self.get_cat(payload.guild_id, payload.channel_id))

			overwrites = {
				guild.default_role: discord.PermissionOverwrite(view_channel=False),
				payload.member: discord.PermissionOverwrite(view_channel=True)
			}

			embed=discord.Embed(title='New Konsultasi!', description=channel)
			embed.set_footer(text=f'Created by {payload.member}')
			for cto_member in await self.get_cto_member(guild):
				overwrites[cto_member] = discord.PermissionOverwrite(view_channel=True)
				# await cto_member.send(embed=embed)
			
			current_id_konsul = await self.get_id_konsul()

			ch = await category.create_text_channel(f'konsultasi-{current_id_konsul}', overwrites=overwrites)

			desc_message = """
Selamat datang di channel konsultasi CTO HMIF ITB! Channel ini bersifat private antara Anda dengan CTO IIT ( + moderator dan owner discord HMIF ITB :(  )

Anda dapat melakukan konsultasi selama text channel ini ada. Jika Anda sudah selesai melakukan konsultasi, dimohon untuk mengisi form feedback [di sini](https://bit.ly/FeedbackIITConsultation) dan react dengan emoji 🔒 untuk menutup channel ini!

Terimakasih"""
			embed = discord.Embed(title=f'Halo {payload.member.nick}!', description=desc_message, color=discord.Colour.gold())

			msg = await ch.send(embed=embed)
			await msg.add_reaction('🔒')

			await message.remove_reaction('🙋', user)

			try:
				db['konsultasi'][str(current_id_konsul+1)] = [payload.member.id, payload.guild_id, ch.id]
			except KeyError:
				db['konsultasi'] = {1:[payload.member.id, payload.guild_id, ch.id]}

		if channel.name.startswith('konsultasi-'):
			try:
				if any(str(payload.channel_id) == str(l[-1]) for l in list(db['konsultasi'].values())):
					message = await channel.fetch_message(payload.message_id)

					def check_message(msg):
						return (msg.author.bot and 
							msg.embeds[0] and
							msg.embeds[0].title == f'Halo {payload.member.nick}!')

					if str(payload.emoji) == '🔒' and not(payload.member.bot) and check_message(message):
						await message.channel.send('Terima kasih telah melakukan konsultasi dengan CTO HMIF ITB!')
						msg = await message.channel.send('Menghapus channel dalam 3...')
						await asyncio.sleep(1)
						for i in range(2, 0, -1):
							await msg.edit(content=f'Menghapus channel dalam {i}...')
							await asyncio.sleep(1)
						await message.channel.delete()
			except KeyError:
				pass
	
	@commands.Cog.listener()
	async def on_message(self, message):
		if message.channel.name.startswith('konsultasi-') and message.content.lower() == 'tutup channel':
			try:
				if any(str(message.channel.id) == str(l[-1]) for l in list(db['konsultasi'].values())):
					if not(message.author.bot):
						await message.channel.send('Sebelum menutup channel ini, mohon isi link feedback berikut : https://bit.ly/FeedbackIITConsultation')
						confirmation = await message.channel.send('Apakah Anda ingin menutup channel ini sekarang?')
						await confirmation.add_reaction('✅')
						await confirmation.add_reaction('❌')

						def check(reaction, user):
							return user == message.author and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

						try:
							reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
						except asyncio.TimeoutError:
							await confirmation.clear_reactions()
							return

						if str(reaction.emoji) == '✅':
							await confirmation.edit(content='Terima kasih telah melakukan konsultasi dengan CTO HMIF ITB!')
							await confirmation.clear_reactions()

							msg = await message.channel.send('Menghapus channel dalam 3...')
							await asyncio.sleep(1)
							for i in range(2, 0, -1):
								await msg.edit(content=f'Menghapus channel dalam {i}...')
								await asyncio.sleep(1)
							await message.channel.delete()

						elif str(reaction.emoji) == '❌':
							await confirmation.edit(content='Dibatalkan!', delete_after=5)
							await confirmation.clear_reactions()

			except KeyError:
				pass
				
def setup(bot):
	bot.add_cog(Konsultasi(bot))
