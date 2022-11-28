from discord.ext import commands


class LinkShortener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Shortens website links from eBay and Amazon before deleting the long link
    @commands.listen("on_message")
    async def on_message(self, message):
        # Shortens eBay links
        if message.content.startswith('https://www.ebay.co.uk/itm/'):
            if "?" in message.content:
                new_link = message.content.split("?")[0]

                await message.channel.send(new_link)
                await message.delete()

        # Shortens Amazon links
        if message.content.startswith('https://www.amazon.co.uk/'):
            if "/dp/" in message.content:
                new_link = message.content.split("/")
                dp_pos = new_link.index("dp")
                id_pos = dp_pos + 1

                await message.channel.send("https://amazon.co.uk/" + new_link[dp_pos] + "/" + new_link[id_pos])
                await message.delete()

            if "/gp/" in message.content:
                new_link = message.content.split("/")
                gp_pos = new_link.index("gp")
                product_pos = gp_pos + 1
                id_pos = gp_pos + 2

                await message.channel.send("https://amazon.co.uk/" + new_link[gp_pos] + "/" + new_link[product_pos]
                                           + "/" + new_link[id_pos])
                await message.delete()


async def setup(bot):
    await bot.add_cog(Link(bot))