from redbot.core.bot import Red
from .nameSubmission import nameSubmission


def setup(bot: Red):
    bot.add_cog(nameSubmission(bot))
