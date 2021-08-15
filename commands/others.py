import discord
from discord.ext import commands
from discord.utils import get

import sqlite3
from typing import Optional

class OtherCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# async def confirmation(self, ctx):
	# 	confirmation = await ctx.send(f'Do you really want to delete data from table {tableName}?')
	# 	await confirmation.add_reaction('✅')
	# 	await confirmation.add_reaction('❌')

	# 	def check(reaction, user):
	# 		return user == ctx.author and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

	# 	try:
	# 		reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
	# 	except asyncio.TimeoutError:
	# 		await confirmation.edit(content='Timed Out!')
	# 		await confirmation.clear_reactions()
	# 		return

	# return reaction, user

	@commands.command(name='ping', aliases=['p'], description='Show bot\'s ping')
	async def ping(self, ctx):
		await ctx.send(f'Pong! 🏓\nPing : {int(self.bot.latency*1000)} ms')

	@commands.command(name='settings', description='Show settings of the current server')
	async def check_settings(self, ctx, arg1:Optional[str], arg2:Optional[str], arg3:Optional[int]):
		conn = sqlite3.connect('Konsultasi.db')
		cursor = conn.cursor()

		if arg1 == 'change' or arg1 == 'chg':
			if arg2 == 'category' or arg2 == 'cat' or arg2 == 'c':
				try:
					category = await self.bot.fetch_channel(arg3)
				except:
					await ctx.send('Category Not Found!', delete_after=5)
					return

				update = f"""
				UPDATE settings
				SET category_id = {arg3}
				WHERE guild_id = {ctx.guild.id}
				"""
				cursor.execute(update)

				await ctx.send(f'Main category has been changed to `{category.name.upper()}`!', delete_after=5)

			elif arg2 == 'message' or arg2 == 'msg' or arg2 == 'm':
				try:
					await ctx.channel.fetch_message(arg3)
				except discord.NotFound:
					await ctx.send('Message Not Found!', delete_after=5)
					return

				update = f"""
				UPDATE settings
				SET message_id = {arg3}
				WHERE guild_id = {ctx.guild.id}
				"""
				cursor.execute(update)

				await ctx.send(f'Main message has been changed to https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{arg3}', delete_after=5)

			else:
				await ctx.send('Correct usage : `!settings (change/chg) [(category/cat/c)|(message/msg/m)] [category ID|message ID]`', delete_after=8)

		else:
			selection = f"""
			SELECT *
			FROM settings
			WHERE guild_id = {ctx.guild.id}
			"""
			settings = cursor.execute(selection).fetchone()

			category = get(ctx.guild.categories, id=settings[1])

			msg = f"""
Server					: `{ctx.guild.name}`
Main Category	: `{category.name.upper()}`
Main Message	: https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{settings[2]}
"""

			await ctx.send(msg)

		conn.commit()
		conn.close()

	@commands.command(description='Make a database with `konsultasi` and `settings` tables')
	@commands.is_owner()
	async def make_db(self, ctx):
		conn = sqlite3.connect('Konsultasi.db')
		cursor = conn.cursor()

		try:
			view1 = """
			SELECT *
			FROM konsultasi
			"""

			view2 = """
			SELECT *
			FROM settings
			"""

			confirmation = await ctx.send(f'Do you really want to drop `konsultasi` and `settings` tables and create the new ones?')
			await confirmation.add_reaction('✅')
			await confirmation.add_reaction('❌')

			def check(reaction, user):
				return user == ctx.author and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
			except asyncio.TimeoutError:
				await confirmation.edit(content='Timed Out!', delete_after=5)
				await confirmation.clear_reactions()
				return

			if str(reaction.emoji) == '✅':
				drop1 = "DROP TABLE konsultasi"
				cursor.execute(drop1)

				drop2 = "DROP TABLE settings"
				cursor.execute(drop2)

				await confirmation.edit(content='Table `konsultasi` and `settings` have been remade!', delete_after=5)
				await confirmation.clear_reactions()

			elif str(reaction.emoji) == '❌':
				await confirmation.edit(content='Cancelled', delete_after=5)
				await confirmation.clear_reactions()
				return

		except sqlite3.OperationalError:
			pass

		finally:
			setup1 = """
			CREATE TABLE IF NOT EXISTS konsultasi (
				id_konsul INTEGER PRIMARY KEY AUTOINCREMENT,
				nama_konsul str NOT NULL
			);
			"""
			cursor.execute(setup1)

			setup2 = """
			CREATE TABLE IF NOT EXISTS settings (
				guild_id int NOT NULL,
				category_id int NOT NULL,
				message_id int NOT NULL
			);
			"""
			cursor.execute(setup2)

			conn.commit()
			conn.close()

			await ctx.send('Database has been set!', delete_after=5)

	@commands.command(description='See all the settings in form of list of tuples (guild ID, category ID, message ID)')
	@commands.is_owner()
	async def view_settings(self, ctx):
		conn = sqlite3.connect('Konsultasi.db')
		cursor = conn.cursor()

		selection = """
		SELECT * FROM settings
		"""
		settings = cursor.execute(selection).fetchall()

		conn.commit()
		conn.close()

		await ctx.send(settings)

	@commands.command(description='Delete the data of a table (not `DROP TABLE`)')
	@commands.is_owner()
	async def del_table(self, ctx, tableName:str=None):
		conn = sqlite3.connect('Konsultasi.db')
		cursor = conn.cursor()

		selection = f"""
		SELECT *
		FROM {tableName}
		"""
		exist = cursor.execute(selection).fetchall()

		if exist:
			confirmation = await ctx.send(f'Do you really want to delete data from table `{tableName}`?')
			await confirmation.add_reaction('✅')
			await confirmation.add_reaction('❌')

			def check(reaction, user):
				return user == ctx.author and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
			except asyncio.TimeoutError:
				await confirmation.edit(content='Timed Out!', delete_after=5)
				await confirmation.clear_reactions()
				return

			if str(reaction.emoji) == '✅':
				deletion = f"""
				DELETE FROM {tableName}
				"""
				cursor.execute(deletion)

				if tableName == 'konsultasi':
					alter = """
					UPDATE sqlite_sequence SET seq = 0 WHERE name = 'konsultasi'
					"""
					cursor.execute(alter)

				await confirmation.edit(content=f'Data from table `{tableName}` has been deleted!', delete_after=5)

			elif str(reaction.emoji) == '❌':
				await confirmation.edit(content='Cancelled', delete_after=5)

			await confirmation.clear_reactions()

		else:
			await ctx.send(f'There isn\'t any data on table {tableName}!', delete_after=5)

		conn.commit()
		conn.close()

	@commands.command(description='Shows the contents of `konsultasi` table in the database')
	@commands.is_owner()
	async def view_konsul(self, ctx):
		conn = sqlite3.connect('Konsultasi.db')
		cursor = conn.cursor()

		selection = """
		SELECT * FROM konsultasi
		"""
		result = cursor.execute(selection).fetchall()

		conn.commit()
		conn.close()

		await ctx.send(result)

	@commands.command(description='Shows "id konsultasi" attribute in the `konsultasi` table')
	@commands.is_owner()
	async def view_id_konsul(self, ctx):
		conn = sqlite3.connect('Konsultasi.db')
		cursor = conn.cursor()

		selection = """
		SELECT id_konsul FROM konsultasi
		"""
		result = cursor.execute(selection).fetchall()

		conn.commit()
		conn.close()

		await ctx.send(result)

	@commands.command(description='Reload extension')
	@commands.is_owner()
	async def reload_ex(self, ctx):
		await ctx.send('Which extension do you want to reload?')
		await ctx.send(f'Available extensions:\n{self.bot.extensions}')
		msg = await self.bot.wait_for('message', check=lambda m:m.author.id == 394083155994214411)
		self.bot.reload_extension(msg)

def setup(bot):
	bot.add_cog(OtherCommands(bot))
