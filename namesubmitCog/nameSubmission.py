import calendar
import logging
import random
from collections import defaultdict, deque
from enum import Enum
from typing import cast, Iterable

import discord

from redbot.cogs.bank import check_global_setting_guildowner, check_global_setting_admin
from redbot.core import Config, bank, commands, errors
from redbot.core.i18n import Translator, cog_i18n
from redbot.core.utils.chat_formatting import box
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS

from redbot.core.bot import Red

T_ = Translator("nameSubmission", __file__)
_ = lambda s: s
_ = T_
@cog_i18n(_)
class nameSubmission(commands.Cog):
	""""""
	
	default_guild_settings = {
		"GAMES": {}
	}
	
	default_role_settings = {}
	default_member_settings = {}
	default_global_settings = default_guild_settings

	default_user_settings = default_member_settings

	def __init__(self, bot: Red):
		
		super().__init__()
		self.bot = bot
		self.file_path = "data/nameSubmission/settings.json"
		self.config = Config.get_conf(self, 1316424116)
		self.config.register_guild(**self.default_guild_settings)
		self.config.register_global(**self.default_global_settings)
		self.config.register_member(**self.default_member_settings)
		self.config.register_user(**self.default_user_settings)
		self.config.register_role(**self.default_role_settings)
		self.slot_register = defaultdict(dict)
	
	def is_mod(ctx):
		
		if not ctx.message.guild:
			return False
		
		id = ctx.message.author.id
		guild = ctx.message.guild
		user = discord.utils.get(guild.members, id=id)
		groups = user.roles
		allowed = False
		for group in groups:
			# if group.name.lower() == "name submitter moderator":
			if group.name.lower() == "The Nemoderators":
				allowed = True
				break
			
		if allowed:
			return True
				
		return False
	
	def is_allowedToSubmit(ctx):
		
		if not ctx.message.guild:
			return False
		
		id = ctx.message.author.id
		guild = ctx.message.guild
		user = discord.utils.get(guild.members, id=id)
		groups = user.roles
		allowed = False
		for group in groups:
			# if group.name.lower() == "name submitter":
			if group.name.lower() == "Patron of the Nemo":
				allowed = True
				break
			
		if allowed:
			return True
				
		return False
	
	@commands.command(pass_context=True, brief="Submits a name", name='namesubmit')	
	@commands.check(is_allowedToSubmit)
	async def namesubmit(self, ctx: commands.Context,game:str, *name):
		"""Submits a name"""
		
		name = " ".join(name)
		name = name.lower()
		
		currentNames = await self.config.GAMES()
		
		if not game.lower() in currentNames:
			await ctx.send("This game does not exist")
		else:
			if not name in currentNames[game.lower()]:
				currentNames[game.lower()][name] = False
				await self.config.GAMES.set(currentNames)
				await ctx.send("Name submited")
			else:
				await ctx.send("This name already submitted")

	@commands.command(pass_context=True, brief="Draws a name", name='namedraw')
	@commands.check(is_mod)
	async def namedraw(self, ctx: commands.Context,game:str):
		"""Draws a name"""
		
		currentNames = await self.config.GAMES()
		
		if not game.lower() in currentNames:
			await ctx.send("This game does not exist")
		else:
			
			names = currentNames[game.lower()]
			
			keys = list(names.keys())
			random_name = ""
			for key in keys:
				if not names[key]:
					random_name = key
					break
			
			if not random_name == "":
				currentNames[game.lower()][random_name] = True
				await self.config.GAMES.set(currentNames)
				await ctx.send(random_name)
			else:
				await ctx.send("Unable to get an unused name")

	@commands.command(pass_context=True, brief="Clears all names from game", name='nameclear')		
	@commands.check(is_mod)
	async def nameclear(self, ctx: commands.Context,game:str):
		"""Clears all names from game"""
		
		currentNames = await self.config.GAMES()
		if not game.lower() in currentNames:
			await ctx.send("This game does not exist")
		else:
			currentNames[game.lower()] = {}
			await self.config.GAMES.set(currentNames)
			await ctx.send("Name cleared")

	@commands.command(pass_context=True, brief="Resets a name", name='namereset')
	@commands.check(is_mod)
	async def namereset(self, ctx: commands.Context,game:str, *name):
		"""Resets a name"""
		
		name = " ".join(name)
		name = name.lower()
		
		currentNames = await self.config.GAMES()
		
		if not game.lower() in currentNames:
			await ctx.send("This game does not exist")
		else:
			if name in currentNames[game.lower()]:
				currentNames[game.lower()][name] = False
				await self.config.GAMES.set(currentNames)
				await ctx.send("Name reset")
			else:
				await ctx.send("This name does not exist")

	@commands.command(pass_context=True, brief="Creates a game to submit names to", name='gamecreate')
	@commands.check(is_mod)
	async def gamecreate(self, ctx: commands.Context,game:str):
		"""Creates a game to submit names to"""
		
		currentNames = await self.config.GAMES()
		if game.lower() in currentNames:
			await ctx.send("This game does already exist")
		else:
			currentNames[game.lower()] = {}
			await self.config.GAMES.set(currentNames)
			await ctx.send("Game created")

	@commands.command(pass_context=True, brief="List all names", name='namelist')
	@commands.check(is_mod)
	async def namelist(self, ctx: commands.Context,game:str):
		"""List all names"""
		
		names = ""
		currentNames = await self.config.GAMES()
		if not game.lower() in currentNames:
			await ctx.send("This game does not exist")
		else:
			for name in currentNames[game.lower()]:
				names = names + name+"\n"
			
			if not names == "":
				await ctx.send(names)
			else:
				await ctx.send("No names to list")
