import discord
from discord.ext import commands

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

			embed = discord.Embed(title=f'Halo {payload.member.name}!', description='Selamat datang di channel konsultasi CTO HMIF ITB!', color=discord.Colour.gold())
			embed.set_footer(text='React dengan emoji 🔒 untuk menutup channel ini')

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
							msg.embeds[0].title == f'Halo {payload.member.name}!')

					if str(payload.emoji) == '🔒' and not(payload.member.bot) and check_message(message):
						await channel.delete()
			except KeyError:
				pass
				
def setup(bot):
	bot.add_cog(Konsultasi(bot))
