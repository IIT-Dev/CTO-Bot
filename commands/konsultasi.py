import discord
from discord.ext import commands

import sqlite3

class Konsultasi(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def get_cto_member(self):
		member1 = await self.bot.fetch_user(394083155994214411)
		member2 = await self.bot.fetch_user(455713207458201602)
		member3 = await self.bot.fetch_user(833640260910317610)
		member4 = await self.bot.fetch_user(360798464952500226)
		member5 = await self.bot.fetch_user(632402909983932416)
		member6 = await self.bot.fetch_user(631836244921548810)

		member_list = [member1, member2, member3, member4, member5, member6]

		return member_list

	def get_settings(self, guild_id):
		conn = sqlite3.connect('Konsultasi.db')
		cursor = conn.cursor()

		try:
			selection = f"""
			SELECT *
			FROM settings
			WHERE guild_id = {guild_id}
			"""
			settings = cursor.execute(selection).fetchall()
		except sqlite3.OperationalError:
			await ctx.send('Settings haven\'t been set up on this server!\nSetup for the first time with `!setup [category ID] [message ID]`')
			return
		finally:
			conn.commit()
			conn.close()

		if settings:
			return settings

	async def get_cat(self, guildID):
		conn = sqlite3.connect('Konsultasi.db')
		cursor = conn.cursor()

		try:
			selection = f"""
			SELECT *
			FROM settings
			WHERE guild_id = {guildID}
			"""
			exist = cursor.execute(selection).fetchall()
		except sqlite3.OperationalError:
			await ctx.send('Settings haven\'t been set up on this server!\nSetup for the first time with `!setup [category ID] [message ID]`')
			return
		finally:
			conn.commit()
			conn.close()

		if exist:
			return exist[0][1]

	def get_id_konsul(self, nama_konsul):
		conn = sqlite3.connect('Konsultasi.db')
		cursor = conn.cursor()

		try:
			selection = """
			SELECT id_konsul
			FROM konsultasi
			"""
			id_konsul = cursor.execute(selection).fetchall()
		except sqlite3.OperationalError:
			await ctx.send('Table `konsultasi` doesn\'t exist!')
			conn.commit()
			conn.close()
			return

		if id_konsul:
			return id_konsul[-1][0]+1
		else:
			insertion = f"""
			INSERT INTO konsultasi
			VALUES (1, '{nama_konsul}')
			"""
			cursor.execute(insertion)

			return 1

		conn.commit()
		conn.close()

	@commands.command(brief='Setup bot settings for a first time on a server', description='Setup bot settings for a first time on a server')
	@commands.is_owner()
	async def setup(self, ctx, categoryID:int=None, messageID:int=None):
		if messageID is not None and categoryID is not None:
			# msg = await ctx.channel.fetch_message(messageID)
			# cat = await self.bot.fetch_channel(categoryID)

			conn = sqlite3.connect('Konsultasi.db')
			cursor = conn.cursor()

			try:
				selection = f"""
				SELECT *
				FROM settings
				WHERE guild_id = {ctx.guild.id}
				"""
				exist = cursor.execute(selection).fetchall()
			except sqlite3.OperationalError:
				await ctx.send('Settings haven\'t been set up on this server!\nSetup for the first time with `!setup [category ID] [message ID]`')
				conn.commit()
				conn.close()
				return

			if exist:
				await ctx.send('The settings on this server has been set up', delete_after=5)

			else:
				insertion = f"""
				INSERT INTO settings
				VALUES ({ctx.guild.id}, {categoryID}, {messageID})
				"""
				cursor.execute(insertion)

				await ctx.send('Setup successful!', delete_after=5)

			conn.commit()
			conn.close()
		else:
			await ctx.send('Correct usage : `!setup [category ID] [message ID]`', delete_after=8)

	@commands.command(brief='Make a main message', description='Make a main message')
	@commands.is_owner()
	async def public_message(self, ctx):
		embed = discord.Embed(title='Konsultasi dengan CTO HMIF ITB!', color=discord.Colour.gold())
		embed.set_footer(text='React dengan emoji 🙋 untuk membuka channel konsultasi!')

		await ctx.message.delete()

		msg = await ctx.send(embed=embed)
		await msg.add_reaction('🙋')

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		user = await self.bot.fetch_user(payload.user_id)
		guild = await self.bot.fetch_guild(payload.guild_id)
		channel = await self.bot.fetch_channel(payload.channel_id)
		message = await channel.fetch_message(payload.message_id)

		if any([payload.message_id in tup for tup in self.get_settings(payload.guild_id)]) and str(payload.emoji) == '🙋':
			category = await self.bot.fetch_channel(await self.get_cat(payload.guild_id))

			overwrites = {
				guild.default_role: discord.PermissionOverwrite(view_channel=False),
				guild.me: discord.PermissionOverwrite(view_channel=True)
			}

			ch = await category.create_text_channel(f'konsultasi-{self.get_id_konsul(payload.member.name)}')

			embed = discord.Embed(title=f'Halo {payload.member.name}!', description='Selamat datang di channel konsultasi CTO HMIF ITB!', color=discord.Colour.gold())
			embed.set_footer(text='React dengan emoji 🔒 untuk menutup channel ini')

			msg = await ch.send(embed=embed)
			await msg.add_reaction('🔒')

			await message.remove_reaction('🙋', user)

			conn = sqlite3.connect('Konsultasi.db')
			cursor = conn.cursor()

			if self.get_id_konsul(payload.member.name) == 1:
				insertion = f"""
				INSERT INTO konsultasi
				VALUES (1, '{payload.member.name}')
				"""
				cursor.execute(insertion)
			else:
				insertion = f"""
				INSERT INTO konsultasi (nama_konsul)
				VALUES ('{payload.member.name}')
				"""
				cursor.execute(insertion)

			conn.commit()
			conn.close()

		if channel.name.startswith('konsultasi-'):
			def check_message(msg):
				return (msg.author.bot and 
					msg.embeds[0] and
					msg.embeds[0].title == f'Halo {payload.member.name}!')

			if str(payload.emoji) == '🔒' and not(payload.member.bot) and check_message(message):
				await channel.delete()
				
def setup(bot):
	bot.add_cog(Konsultasi(bot))
