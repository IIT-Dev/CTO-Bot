import discord
from discord.ext import commands
from discord.utils import get

import asyncio
from replit import db
from typing import Optional, Union

class OtherCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# async def confirmation(self, ctx):
	# 	confirmation = await ctx.send(f'Do you really want to delete data from table {table_name}?')
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

	@commands.command(name='ping', aliases=['p'], brief='Show bot\'s ping', description='Show bot\'s ping')
	async def ping(self, ctx):
		await ctx.send(f'Pong! 🏓\nPing : `{int(self.bot.latency*1000)}` ms')

	@commands.command(name='settings', aliases=['s'], brief='Show settings of the current server', description='Show settings of the current server')
	async def check_settings(self, ctx, arg1:Optional[str], arg2:Optional[str]):
		if arg1 == 'category' or arg1 == 'cat' or arg1 == 'c':
			if ctx.author.guild_permissions.administrator == True or ctx.author.id == self.bot.owner_id:
				category = ctx.guild.get_channel(arg2)

				if category is None:
					await ctx.send(f'Category with ID `{arg2}` is not found!', delete_after=5)
					return

				try:
					db['settings'][str(ctx.guild.id)][0] = arg2
				except KeyError:
					await ctx.send('Settings haven\'t been set up on this server!\nSetup for the first time with `c!setup [category ID] [message ID]`')
					return

				await ctx.send(f'Main category has been changed to `{category.name.upper()}`', delete_after=5)

			else:
				await ctx.send('You don\'t have a permission to do this!')

		elif arg1 == 'message' or arg1 == 'msg' or arg1 == 'm':
			if ctx.author.guild_permissions.administrator == True or ctx.author.id == self.bot.owner_id:
				try:
					msg = await ctx.channel.fetch_message(arg2)
				except discord.NotFound:
					await ctx.send('Message is not found!', delete_after=5)
					return
				except discord.HTTPException:
					await ctx.send('Failed to fetch message!', delete_after=5)
					return

				try:
					db['settings'][str(ctx.guild.id)][1] = arg2
				except KeyError:
					await ctx.send('Settings haven\'t been set up on this server!\nSetup for the first time with `c!setup [category ID] [message ID]`')
					return

				await ctx.send(f'Main message has been changed to {msg.jump_url}', delete_after=5)

			else:
				await ctx.send('You don\'t have a permission to do this!')

		else:
			try:
				settings = db['settings'][str(ctx.guild.id)]
			except KeyError:
				await ctx.send('Settings haven\'t been set up on this server!\nSetup for the first time with `c!setup [category ID] [message ID]`')
				return

			category = await self.bot.fetch_channel(settings[0])
			message = await ctx.guild.fetch_message(settings[1])

			msg = f"""
Server					: `{ctx.guild.name}`
Main Category	: `{category.name.upper()}`
Main Message	: {message.jump_url}
"""

			await ctx.send(msg)

	@commands.command(name='vs', brief='See all the settings in form of list of tuples (guild ID, category ID, message ID)', description='See all the settings in form of list of tuples (guild ID, category ID, message ID)')
	@commands.is_owner()
	async def view_settings(self, ctx):
		try:
			settings = db['settings']
		except KeyError:
			await ctx.send('Table `settings` doesn\'t exist!')
			return

		await ctx.send(settings)

	@commands.command(name='vt', brief='Shows the contents of a table in the database', description='Shows the contents of a table in the database')
	@commands.is_owner()
	async def view_table(self, ctx, table_name:str=None):
		try:
			table = db[table_name]
		except KeyError:
			await ctx.send('Table `konsultasi` doesn\'t exist')
			return

		await ctx.send(table)
	
	@commands.command(name='vid', brief='Shows "id konsultasi" attribute in the `konsultasi` table', description='Shows "id konsultasi" attribute in the `konsultasi` table')
	@commands.is_owner()
	async def view_id_konsul(self, ctx):
		try:
			id_konsul = list(db['konsultasi'].keys())[-1]
		except KeyError:
			await ctx.send('Table `konsultasi` doesn\'t exist!')
			return

		await ctx.send(id_konsul)
	
	@commands.command(name='delt', brief='Delete the data of a table', description='Delete the data of a table')
	@commands.is_owner()
	async def del_table(self, ctx, table_name:str=None):
		try:
			db[table_name]
		except KeyError:
			await ctx.send(f'Table `{table_name}` doesn\'t exist!')
			return

		confirmation = await ctx.send(f'Do you really want to delete data from table `{table_name}`?')
		await confirmation.add_reaction('✅')
		await confirmation.add_reaction('❌')

		def check(reaction, user):
			return user == ctx.author and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

		try:
			reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
		except asyncio.TimeoutError:
			await confirmation.edit(content='Timed Out!', delete_after=5)
			await confirmation.clear_reactions()
			return

		if str(reaction.emoji) == '✅':
			del db[table_name]

			await confirmation.edit(content=f'Data from table `{table_name}` has been deleted!', delete_after=5)

		elif str(reaction.emoji) == '❌':
			await confirmation.edit(content='Cancelled', delete_after=5)

		await confirmation.clear_reactions()

def setup(bot):
	bot.add_cog(OtherCommands(bot))
