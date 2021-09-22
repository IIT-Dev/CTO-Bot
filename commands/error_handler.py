from discord.ext import commands

import asyncio
import math

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            err_msg = await ctx.send("Error When Invoking Command!")
            await asyncio.sleep(5)
            await err_msg.delete()
        
        if isinstance(error, commands.RoleNotFound):
            err_msg = await ctx.send("Role Not Found!")
            await asyncio.sleep(5)
            await err_msg.delete()

        if isinstance(error, commands.MissingPermissions):
            err_msg = await ctx.send('You don\' have the permission to do this!')
            await asyncio.sleep(5)
            await err_msg.delete()
        
        error_ch = await self.bot.fetch_channel(849749416171536395)
        
        await error_ch.send(error)

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
