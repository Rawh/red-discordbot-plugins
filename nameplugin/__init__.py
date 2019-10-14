from .custom_name_submit import CustomNameSubmit


def setup(bot):
    bot.add_cog(CustomNameSubmit(bot))
