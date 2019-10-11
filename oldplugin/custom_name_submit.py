from redbot.core import commands
from .database import Database
from .config import custom_user_role, custom_admin_role
import sqlite3

database = Database("/data/cogs/CogManager/cogs/nameplugin/old_custom_name_submit.db")


class CustomNameSubmit(commands.Cog):
    """Let's users submit names for games."""

    @commands.command()
    @commands.has_any_role(custom_user_role, custom_admin_role)
    async def namesubmit(self, ctx, game, name):
        """Submit a name for a game."""
        try:
            if database.user_can_submit(game, ctx.author.id):
                if not database.name_exists(game, name):
                    database.submit_name(game, ctx.author.id, ctx.author.name + "#" + ctx.author.discriminator, name)
                    await ctx.send("Thank you for your submission.")
                else:
                    await ctx.send(f"The name `{name}` was already submitted.")
            else:
                await ctx.send(f"Seems like you already submitted a name. Change your submission with `{ctx.prefix}namechange <game> <new_name>`")
        except sqlite3.OperationalError:
            await ctx.send(f"`{game}` is not available for submission.")
        except Exception as e:
            raise e

    @namesubmit.error
    async def namesubmit_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send(f"You need the role \"{custom_user_role}\" to use this command.")

    @commands.command()
    @commands.has_any_role(custom_user_role, custom_admin_role)
    async def namechange(self, ctx, game, name):
        """Change you submitted name for a given game."""
        try:
            if not database.user_can_submit(game, ctx.author.id):
                database.change_name(game, ctx.author.id, name)
                await ctx.send(f"Changed the submitted name to {name}")
            else:
                await ctx.send(f"Seems like you haven't submitted a name yet. Submit a name with `{ctx.prefix}namesubmit <game> <name>`")
        except sqlite3.OperationalError:
            await ctx.send(f"`{game}` seems to not be available.")
        except Exception as e:
            raise e

    @namechange.error
    async def namechange_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send(f"You need the role \"{custom_user_role}\" to use this command.")

    @commands.command()
    @commands.has_role(custom_admin_role)
    async def namedraw(self, ctx, game):
        """Draw a available name from the submission list."""
        try:
            random_game = database.get_random_name(game)
            if random_game is not None:
                await ctx.send(f"Name: `{random_game}`")
            else:
                await ctx.send("There are no available names.")
        except sqlite3.OperationalError:
            await ctx.send(f"`{game}` seems to not be available.")
        except Exception as e:
            raise e

    @commands.command()
    @commands.has_role(custom_admin_role)
    async def nameclear(self, ctx, game):
        """Clear(delete) all submitted games."""
        try:
            database.clear_game_names(game)
            await ctx.send(f"Cleared all entries for {game}.")
        except sqlite3.OperationalError:
            await ctx.send(f"`{game}` seems to not be available.")
        except Exception as e:
            raise e

    @commands.command()
    @commands.has_role(custom_admin_role)
    async def namelist(self, ctx, game):
        """List all submitted names for a game."""
        list_data = database.get_all_entries(game)
        messages = generate_namelist_messages(list_data)
        for message in messages:
            await ctx.send(message)

    @commands.command()
    @commands.has_role(custom_admin_role)
    async def namereset(self, ctx, game, name):
        """Reset a name back to available."""
        try:
            if database.name_exists(game, name):
                database.make_name_available(game, name)
                await ctx.send(f"Name: `{name}` for `{game}` is available again.")
            else:
                await ctx.send(f"Name: `{name}` does not exist.")
        except sqlite3.OperationalError:
            await ctx.send(f"`{game}` seems to not be available.")
        except Exception as e:
            raise e

    @commands.command()
    @commands.has_role(custom_admin_role)
    async def namecreate(self, ctx, game):
        """Create a new game for users to submit their names to."""
        try:
            database.create_game(game)
            await ctx.send(f"Created new game: `{game}`")
        except sqlite3.OperationalError:
            await ctx.send(f"`{game}` is not a valid name.")
        except Exception as e:
            raise e


def generate_namelist_messages(list_data):
    messages = []
    msg = "```\n"
    msg += "Name | Available | Submitted by\n"
    for entry in list_data:
        new_line = f"{entry[2]} | {True if entry[3] == 1 else False} | {entry[1]}\n"
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
