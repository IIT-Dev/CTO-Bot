import discord
from discord.ext import commands

import sqlite3

class Konsultasi(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.settings = self.get_settings()

	async def get_cto_member(self):
		member1 = await self.bot.fetch_user(394083155994214411)
		member2 = await self.bot.fetch_user(455713207458201602)
		member3 = await self.bot.fetch_user(833640260910317610)
		member4 = await self.bot.fetch_user(360798464952500226)
		member5 = await self.bot.fetch_user(632402909983932416)
		member6 = await self.bot.fetch_user(631836244921548810)

		member_list = [member1, member2, member3, member4, member5, member6]

		return member_list

	def get_settings(self):
		conn = sqlite3.connect('Konsultasi.db')
		cursor = conn.cursor()

		selection = """
		SELECT *
		FROM settings
		"""
		settings = cursor.execute(selection).fetchall()

		conn.commit()
		conn.close()

		if settings:
			return settings

	async def get_cat(self, guildID):
		conn = sqlite3.connect('Konsultasi.db')
		cursor = conn.cursor()

		selection = f"""
		SELECT *
		FROM settings
		WHERE guild_id = {guildID}
		"""
		exist = cursor.execute(selection).fetchall()

		conn.commit()
		conn.close()

		if exist:
			return exist[0][1]

	def get_id_konsul(self):
		conn = sqlite3.connect('Konsultasi.db')
		cursor = conn.cursor()

		selection = """
		SELECT id_konsul
		FROM konsultasi
		"""
		id_konsul = cursor.execute(selection).fetchone()

		conn.commit()
		conn.close()

		return id_konsul

	@commands.command()
	@commands.is_owner()
	async def setup(self, ctx, categoryID:int=None, messageID:int=None):
		if messageID is not None and categoryID is not None:
			# msg = await ctx.channel.fetch_message(messageID)
			# cat = await self.bot.fetch_channel(categoryID)

			conn = sqlite3.connect('Konsultasi.db')
			cursor = conn.cursor()

			insertion = f"""
			INSERT INTO settings
			VALUES ({ctx.guild.id}, {categoryID}, {messageID})
			"""
			cursor.execute(insertion)

			conn.commit()
			conn.close()

			await ctx.send('Setup successful!')
		else:
			await ctx.send('Correct usage : `!setup [category ID] [message ID]`')

	@commands.command()
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

		if any([payload.message_id in tup for tup in self.settings]):
			category = await self.bot.fetch_channel(await self.get_cat(payload.guild_id))

			overwrites = {
				guild.default_role: discord.PermissionOverwrite(view_channel=False),
				guild.me: discord.PermissionOverwrite(view_channel=True)
			}

			ch = await category.create_text_channel(f'konsultasi-{self.get_id_konsul()}')

			embed = discord.Embed(title=f'Halo {payload.member.nick}!', description='Selamat datang di channel konsultasi CTO HMIF ITB!', color=discord.Colour.gold())
			embed.set_footer(text='React dengan emoji 🔒 untuk menutup channel ini')

			msg = await ch.send(embed=embed)
			await msg.add_reaction('🔒')

			await message.remove_reaction('🙋', user)

def setup(bot):
	bot.add_cog(Konsultasi(bot))
