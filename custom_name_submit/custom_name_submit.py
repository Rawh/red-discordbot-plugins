from redbot.core import commands, Config
import discord
from .config import custom_user_roles, custom_admin_roles, whitelisted_channels
import asyncio
import random


class GameNotFound(Exception):
    pass


class GameAlreadyExists(Exception):
    pass


# ==== CHECKS ====

def is_whitelisted():
    def predicate(ctx):
        if isinstance(ctx.channel, discord.DMChannel) or isinstance(ctx.channel, discord.GroupChannel):
            return True
        if ctx.channel.name in whitelisted_channels:
            return True
        return False
    return commands.check(predicate)


class CustomNameSubmit(commands.Cog):
    """Let's users submit names for games."""
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=420982359871324)
        config_scheme = {
            "games": {}
        }
        self.config.register_guild(**config_scheme)

    # ==== STORAGE ====

    async def get_all_games(self, ctx):
        games_dict = await self.get_games_data(ctx)
        return list(games_dict.keys())

    async def create_game(self, ctx, game_name):
        sanitized_game_name = self.sanitize_user_input(game_name)
        if sanitized_game_name not in await self.get_all_games(ctx):
            games_data = await self.get_games_data(ctx)
            games_data[sanitized_game_name] = {"isLocked": 0, "data": {}}
            await self.set_games_data(ctx, games_data)
        else:
            raise GameAlreadyExists

    async def delete_game(self, ctx, game_name):
        sanitized_game_name = self.sanitize_user_input(game_name)
        if sanitized_game_name in await self.get_all_games(ctx):
            games_data = await self.get_games_data(ctx)
            games_data.pop(sanitized_game_name)
            await self.set_games_data(ctx, games_data)
        else:
            raise GameNotFound

    async def clear_game_names(self, ctx, game_name):
        sanitized_game_name = self.sanitize_user_input(game_name)
        if sanitized_game_name in await self.get_all_games(ctx):
            games_data = await self.get_games_data(ctx)
            games_data[sanitized_game_name]["data"] = {}
            await self.set_games_data(ctx, games_data)
        else:
            raise GameNotFound

    async def get_random_name(self, ctx, game_name):
        sanitized_game_name = self.sanitize_user_input(game_name)
        if sanitized_game_name in await self.get_all_games(ctx):
            games_data = await self.get_games_data(ctx)
            for i in range(len(list(games_data[sanitized_game_name]["data"].keys()))):
                name_choice = random.choice(list(games_data[sanitized_game_name]["data"].keys()))
                if games_data[sanitized_game_name]["data"][name_choice]["available"] == 1:
                    await self.make_name_unavailable(ctx, sanitized_game_name, name_choice)
                    return [name_choice, games_data[sanitized_game_name]["data"][name_choice]["user_id"]]
            return None
        else:
            raise GameNotFound

    async def get_all_entries(self, ctx, game_name):
        sanitized_game_name = self.sanitize_user_input(game_name)
        if sanitized_game_name in await self.get_all_games(ctx):
            games_data = await self.get_games_data(ctx)
            return games_data[sanitized_game_name]["data"]
        else:
            raise GameNotFound

    async def user_can_submit(self, ctx, game_name, user_id):
        sanitized_game_name = self.sanitize_user_input(game_name)
        if sanitized_game_name in await self.get_all_games(ctx):
            games_data = await self.get_games_data(ctx)
            for data in games_data[sanitized_game_name]["data"].values():
                if data["user_id"] == user_id:
                    return False
            return True
        else:
            raise GameNotFound

    async def name_exists(self, ctx, game_name, submitted_name):
        sanitized_submitted_name = self.sanitize_user_input(submitted_name)
        sanitized_game_name = self.sanitize_user_input(game_name)
        if sanitized_game_name in await self.get_all_games(ctx):
            games_data = await self.get_games_data(ctx)
            if sanitized_submitted_name in list(games_data[sanitized_game_name]["data"].keys()):
                return True
            else:
                return False
        else:
            raise GameNotFound

    async def submit_name(self, ctx, game_name, user_id, username, submitted_name):
        sanitized_submitted_name = self.sanitize_user_input(submitted_name)
        sanitized_game_name = self.sanitize_user_input(game_name)
        games_data = await self.get_games_data(ctx)
        games_data[sanitized_game_name]["data"][sanitized_submitted_name] = {
            "user_id": user_id,
            "username": username,
            "available": 1
        }
        await self.set_games_data(ctx, games_data)

    async def change_name(self, ctx, game_name, user_id, submitted_name):
        sanitized_submitted_name = self.sanitize_user_input(submitted_name)
        sanitized_game_name = self.sanitize_user_input(game_name)
        games_data = await self.get_games_data(ctx)
        old_data = await self.get_data_from_user_id(ctx, game_name, user_id)
        games_data[sanitized_game_name]["data"][sanitized_submitted_name] = games_data[sanitized_game_name]["data"].pop(old_data[0])
        await self.set_games_data(ctx, games_data)

    async def delete_name(self, ctx, game_name, user_id, submitted_name):
        sanitized_submitted_name = self.sanitize_user_input(submitted_name)
        sanitized_game_name = self.sanitize_user_input(game_name)
        games_data = await self.get_games_data(ctx)
        games_data[sanitized_game_name]["data"].pop(sanitized_submitted_name)
        await self.set_games_data(ctx, games_data)

    async def get_data_from_user_id(self, ctx, game_name, user_id):
        sanitized_game_name = self.sanitize_user_input(game_name)
        games_data = await self.get_games_data(ctx)
        for game, data in games_data[sanitized_game_name]["data"].items():
            if data["user_id"] == user_id:
                return [game, data]
        return None

    async def make_name_available(self, ctx, game_name, submitted_name):
        sanitized_submitted_name = self.sanitize_user_input(submitted_name)
        sanitized_game_name = self.sanitize_user_input(game_name)
        games_data = await self.get_games_data(ctx)
        games_data[sanitized_game_name]["data"][sanitized_submitted_name]["available"] = 1
        await self.set_games_data(ctx, games_data)

    async def make_name_unavailable(self, ctx, game_name, submitted_name):
        sanitized_submitted_name = self.sanitize_user_input(submitted_name)
        sanitized_game_name = self.sanitize_user_input(game_name)
        games_data = await self.get_games_data(ctx)
        games_data[sanitized_game_name]["data"][sanitized_submitted_name]["available"] = 0
        await self.set_games_data(ctx, games_data)

    async def is_game_locked(self, ctx, game_name):
        sanitized_game_name = self.sanitize_user_input(game_name)
        if sanitized_game_name in await self.get_all_games(ctx):
            games_data = await self.get_games_data(ctx)
            return games_data[sanitized_game_name]["isLocked"]
        else:
            raise GameNotFound

    async def lock_game(self, ctx, game_name):
        sanitized_game_name = self.sanitize_user_input(game_name)
        games_data = await self.get_games_data(ctx)
        games_data[sanitized_game_name]["isLocked"] = 1
        await self.set_games_data(ctx, games_data)

    async def unlock_game(self, ctx, game_name):
        sanitized_game_name = self.sanitize_user_input(game_name)
        games_data = await self.get_games_data(ctx)
        games_data[sanitized_game_name]["isLocked"] = 0
        await self.set_games_data(ctx, games_data)

    async def reset_entries_to_available(self, ctx, game_name):
        sanitized_game_name = self.sanitize_user_input(game_name)
        games_data = await self.get_games_data(ctx)
        for key, data in games_data[sanitized_game_name]["data"].items():
            data["available"] = 1
        await self.set_games_data(ctx, games_data)

    async def get_games_data(self, ctx):
        return await self.config.guild(ctx.guild).games()

    async def set_games_data(self, ctx, data):
        await self.config.guild(ctx.guild).games.set(data)

    def sanitize_user_input(self, input_str):
        valid_chars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "_"]
        sanitized_input = ""
        for char in input_str.lower():
            if char in valid_chars:
                sanitized_input += char
        return sanitized_input

    # ==== COMMANDS ====

    @commands.command()
    @commands.has_any_role(*custom_user_roles)
    @is_whitelisted()
    async def namesubmit(self, ctx, game, name):
        """Submit a name for a game."""
        try:
            if await self.is_game_locked(ctx, game):
                await ctx.send(f"`{game}` is currently locked. 🔒\nYou can still user `!namelist {game}` to see all submissions.")
            else:
                if await self.user_can_submit(ctx, game, ctx.author.id):
                    if not await self.name_exists(ctx, game, name):
                        await self.submit_name(ctx, game, ctx.author.id, ctx.author.name + "#" + ctx.author.discriminator, name)
                        await ctx.send("Thank you for your submission.")
                    else:
                        await ctx.send(f"The name `{name}` was already submitted.")
                else:
                    await ctx.send(f"Seems like you already submitted a name. Change your submission with `{ctx.prefix}namechange <game> <new_name>`")
        except GameNotFound:
            await ctx.send(f"`{game}` is not available for submission.")
        except Exception as e:
            raise e

    @namesubmit.error
    async def namesubmit_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("You don't have permission to use this command.")
        if isinstance(error, commands.CheckFailure):
            await self.not_whitelisted_message(ctx)

    @commands.command()
    @commands.has_any_role(*custom_user_roles)
    @is_whitelisted()
    async def namechange(self, ctx, game, name):
        """Change you submitted name for a given game."""
        try:
            if await self.is_game_locked(ctx, game):
                await ctx.send(f"`{game}` is currently locked. 🔒\nYou can still user `!namelist {game}` to see all submissions.")
            else:
                if not await self.user_can_submit(ctx, game, ctx.author.id):
                    await self.change_name(ctx, game, ctx.author.id, name)
                    await ctx.send(f"Changed the submitted name to {name}")
                else:
                    await ctx.send(f"Seems like you haven't submitted a name yet. Submit a name with `{ctx.prefix}namesubmit <game> <name>`")
        except GameNotFound:
            await ctx.send(f"`{game}` seems to not be available.")
        except Exception as e:
            raise e

    @namechange.error
    async def namechange_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("You don't have permission to use this command.")
        if isinstance(error, commands.CheckFailure):
            await self.not_whitelisted_message(ctx)

    @commands.command()
    @commands.has_any_role(*custom_admin_roles)
    @is_whitelisted()
    async def namedraw(self, ctx, game):
        """Draw a available name from the submission list."""
        try:
            random_name = await self.get_random_name(ctx, game)
            if random_name is not None:
                await ctx.send(f"Name: `{random_name[0]}` submitted by <@{random_name[1]}>")
            else:
                await ctx.send("There are no available names.")
        except GameNotFound:
            await ctx.send(f"`{game}` seems to not be available.")
        except Exception as e:
            raise e

    @namedraw.error
    async def namedraw_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await self.not_whitelisted_message(ctx)

    @commands.command()
    @commands.has_any_role(*custom_admin_roles)
    @is_whitelisted()
    async def nameclear(self, ctx, game):
        """Clear(delete) all submitted names."""
        try:
            bot_msg = await ctx.send(f"{len(await self.get_all_entries(ctx, game))} entries will be deleted.\nAre you sure?")
            await bot_msg.add_reaction("✅")
            await bot_msg.add_reaction("❌")
            reaction, user = await self.bot.wait_for('reaction_add', check=lambda r, u: u.id == ctx.author.id)
            if reaction.emoji == "✅":
                await self.clear_game_names(ctx, game)
                await ctx.send(f"Cleared all entries for `{game}`.")
            elif reaction.emoji == "❌":
                await ctx.send("Canceled nameclear")
        except GameNotFound:
            await ctx.send(f"`{game}` seems to not be available.")
        except Exception as e:
            raise e

    @nameclear.error
    async def nameclear_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await self.not_whitelisted_message(ctx)

    @commands.command()
    @commands.has_any_role(*custom_admin_roles)
    @commands.cooldown(1, 30, commands.BucketType.guild)
    @is_whitelisted()
    async def namelist(self, ctx, game):
        """List all submitted names for a game."""
        list_data = await self.get_all_entries(ctx, game)
        messages = generate_namelist_messages(list_data)
        for message in messages:
            await ctx.send(message)

    @namelist.error
    async def namelist_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Command on cooldown. Retry in {int(error.retry_after)} seconds.")
        if isinstance(error, commands.CheckFailure):
            await self.not_whitelisted_message(ctx)

    @commands.command()
    @commands.has_any_role(*custom_admin_roles)
    @is_whitelisted()
    async def namereset(self, ctx, game, name):
        """Reset a name back to available."""
        try:
            if await self.name_exists(ctx, game, name):
                await self.make_name_available(ctx, game, name)
                await ctx.send(f"Name: `{name}` for `{game}` is available again.")
            else:
                await ctx.send(f"Name: `{name}` does not exist.")
        except GameNotFound:
            await ctx.send(f"`{game}` seems to not be available.")
        except Exception as e:
            raise e

    @namereset.error
    async def namereset_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await self.not_whitelisted_message(ctx)

    @commands.command()
    @commands.has_any_role(*custom_admin_roles)
    @is_whitelisted()
    async def namelockgame(self, ctx, game):
        """Locks a game. Submission will be denied."""
        try:
            await self.lock_game(ctx, game)
            await ctx.send(f"`{game}` has been locked. 🔒")
        except GameNotFound:
            await ctx.send(f"`{game}` seems to not be available.")
        except Exception as e:
            raise e

    @namelockgame.error
    async def namelockgame_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await self.not_whitelisted_message(ctx)

    @commands.command()
    @commands.has_any_role(*custom_admin_roles)
    @is_whitelisted()
    async def nameunlockgame(self, ctx, game):
        """Unlocks a game. Submissions will be possible again."""
        try:
            await self.unlock_game(ctx, game)
            await ctx.send(f"`{game}` has been unlocked. 🔓")
        except GameNotFound:
            await ctx.send(f"`{game}` seems to not be available.")
        except Exception as e:
            raise e

    @nameunlockgame.error
    async def nameunlockgame_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await self.not_whitelisted_message(ctx)

    @commands.command()
    @commands.has_any_role(*custom_admin_roles)
    @is_whitelisted()
    async def namecreate(self, ctx, game):
        """Create a new game for users to submit their names to."""
        all_games = await self.get_all_games(ctx)
        if self.sanitize_user_input(game) in all_games:
            await ctx.send(f"`{game}` already exists.")
        else:
            try:
                await self.create_game(ctx, game)
                await ctx.send(f"Created new game: `{game}`")
            except Exception as e:
                raise e

    @namecreate.error
    async def namecreate_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await self.not_whitelisted_message(ctx)

    @commands.command()
    @commands.has_any_role(*custom_admin_roles)
    @is_whitelisted()
    async def namedeletegame(self, ctx, game):
        """Delete a game."""
        try:
            entry_count = len(await self.get_all_entries(ctx, game))
            bot_msg = await ctx.send(f"{game} and {entry_count} entries will be deleted.\nAre you sure?")
            await bot_msg.add_reaction("✅")
            await bot_msg.add_reaction("❌")
            reaction, user = await self.bot.wait_for('reaction_add', check=lambda r, u: u.id == ctx.author.id)
            if reaction.emoji == "✅":
                await self.delete_game(ctx, game)
                await ctx.send(f"`{game}` has been deleted.")
            elif reaction.emoji == "❌":
                await ctx.send("Canceled")
        except GameNotFound:
            await ctx.send(f"`{game}` seems to not be available.")
        except Exception as e:
            raise e

    @namedeletegame.error
    async def namedeletegame_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await self.not_whitelisted_message(ctx)

    @commands.command()
    @commands.has_any_role(*custom_user_roles)
    @is_whitelisted()
    async def namelistgames(self, ctx):
        """Lists all games"""
        msg = "```\n"
        for game in await self.get_all_games(ctx):
            msg += f"{game} | {len(await self.get_all_entries(ctx, game))} names submitted\n"
        msg += "```"
        await ctx.send(msg)

    @namelistgames.error
    async def namelistgames_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await self.not_whitelisted_message(ctx)

    @commands.command()
    @commands.has_any_role(*custom_admin_roles)
    @is_whitelisted()
    async def nameresetlist(self, ctx, game):
        """Resets all entries for the given game back to available."""
        try:
            entry_count = len(await self.get_all_entries(ctx, game))
            bot_msg = await ctx.send(f"{entry_count} entries for {game} will be reset to available.\nAre you sure?")
            await bot_msg.add_reaction("✅")
            await bot_msg.add_reaction("❌")
            reaction, user = await self.bot.wait_for('reaction_add', check=lambda r, u: u.id == ctx.author.id)
            if reaction.emoji == "✅":
                await self.reset_entries_to_available(ctx, game)
                await ctx.send(f"{entry_count} entries reset to available.")
            elif reaction.emoji == "❌":
                await ctx.send("Canceled")
        except GameNotFound:
            await ctx.send(f"`{game}` seems to not be available.")
        except Exception as e:
            raise e

    @nameresetlist.error
    async def nameresetlist_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await self.not_whitelisted_message(ctx)

    async def not_whitelisted_message(self, ctx):
        msg = await ctx.send("You can't use this command here.")
        await asyncio.sleep(2)
        await msg.delete()


def generate_namelist_messages(list_data):
    messages = []
    msg = "```\n"
    msg += "Name | Available | Submitted by\n"
    for name, data in list_data.items():
        username = data["username"]
        available = data["available"]
        new_line = f"{name} | {True if available == 1 else False} | {username}\n"
        if (len(msg) + 3) + len(new_line) < 1999:
            msg += new_line
        else:
            msg += "```"
            messages.append(msg)
            msg = "```\n"
            msg += "Name | Available | Submitted by\n"
            msg += new_line
    msg += "```"
    messages.append(msg)
    return messages
