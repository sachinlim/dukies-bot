import discord
from discord.ext import commands
import datetime
import math
import passives
import actives
import in_game_scraper
import ebay_scraper

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print("Bot is online!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please enter the search term!')


# Shortens website links from eBay and Amazon before deleting the long link
@bot.listen("on_message")
async def on_message(message):
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


# op.gg profile for summoner name entered after command
@bot.command()
async def op(ctx, *, summoner_name):
    formatted = passives.op_format(summoner_name)
    await ctx.send("https://www.op.gg/summoners/euw/" + formatted)


# Link to live game for summoner name entered after command
@bot.command()
async def ig(ctx, *, summoner_name):
    formatted = passives.op_format(summoner_name)

    embed = discord.Embed(
        title="Live Game Match-Up",
        description=f"From {summoner_name}'s op.gg \n https://www.op.gg/summoners/euw/{formatted}/ingame",
        colour=0xbc8125,
    )

    blue_champs = blue_ranks = blue_wr = ""
    red_champs = red_ranks = red_wr = ""

    data = in_game_scraper.get_data(formatted)

    for summoner_name in data[0:5]:
        blue_champs += summoner_name[0] + '\n'
        blue_ranks += summoner_name[1] + '\n'
        blue_wr += summoner_name[2] + '\n'

    embed.add_field(name="Blue Team", value=blue_champs, inline=True)
    embed.add_field(name="Rank", value=blue_ranks, inline=True)
    embed.add_field(name="Win Rate", value=blue_wr, inline=True)

    for summoner_name in data[5:10]:
        red_champs += summoner_name[0] + '\n'
        red_ranks += summoner_name[1] + '\n'
        red_wr += summoner_name[2] + '\n'

    embed.add_field(name="Red Team", value=red_champs, inline=True)
    embed.add_field(name="Rank", value=red_ranks, inline=True)
    embed.add_field(name="Win Rate", value=red_wr, inline=True)

    embed.set_thumbnail(url='https://static.wikia.nocookie.net/leagueoflegends/images/0/02/Season_2022_-_Challenger'
                            '.png')
    embed.timestamp = datetime.datetime.utcnow()
    embed.set_footer(text='\u200b',
                     icon_url='https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/LoL_icon.svg/1200px'
                              '-LoL_icon.svg.png')

    await ctx.send(embed=embed)


@bot.command()
async def ig2(ctx, *, summoner_name):
    if " " in summoner_name:
        formatted = summoner_name.replace(" ", "%20")
        await ctx.send("https://www.op.gg/summoners/euw/" + formatted + "/ingame")
    else:
        await ctx.send("https://www.op.gg/summoners/euw/" + summoner_name + "/ingame")


# Pro Builds for specified Champion
@bot.command()
async def pb(ctx, *, champion_name):
    formatted = passives.ugg_format(champion_name)
    await ctx.send("https://probuildstats.com/champion/" + formatted)


# u.gg build guide for specified Champion
@bot.command()
async def ug(ctx, *, champion_name):
    formatted = passives.ugg_format(champion_name)
    await ctx.send("https://u.gg/lol/champions/" + formatted + "/build")


# patch notes
@bot.command()
async def patch(ctx, *, game):
    match game:
        case 'lol':
            await ctx.send('https://www.leagueoflegends.com/en-us/news/tags/patch-notes/')
        case 'tft':
            await ctx.send('https://teamfighttactics.leagueoflegends.com/en-us/news/')
        case 'valo':
            await ctx.send('https://playvalorant.com/en-us/news/game-updates/')
        case _:
            await ctx.send('Please enter a valid game after !patch. The supported games are: lol, tft, valo')


# command to delete previous messages
@bot.command()
async def clear(ctx, amount=1):
    await ctx.channel.purge(limit=amount + 1)


# command to search for sold items on eBay to get an idea of its market value
@bot.command()
async def search(ctx, *, item):
    if 'help' in item:
        help_embed = discord.Embed(
            title=f'eBay Search Help',
            description='Here are the proper ways to search.\n '
                        'Filters being used: Exact words, Sold listings, Used, UK only',
            colour=0xc48c02,
        )

        help_embed.add_field(name='Format',
                             value=f'**DO NOT ABUSE** this command as it **may get IP blocked** by eBay!\n'
                                   f'The correct way to search is by typing: !search `[item]`\n '
                                   f'\n'
                                   f'Example: !search rtx 3070',
                             inline=False)
        help_embed.add_field(name='Specific items',
                             value=f'Items such as CPUs or RAM may get diluted in the search results because '
                                   f'they are part of a PC build. Some items may need to be formatted in a way '
                                   f'so that the search filter searches for the right items.\n'
                                   f'\n'
                                   f'Example: !search ryzen 5800x **cpu**\n'
                                   f'Example: !search ddr4 ram **2x8gb**',
                             inline=False)
        help_embed.add_field(name='0 results',
                             value='You may have entered the wrong spelling of the item you are trying to search '
                                   'for.\n'
                                   '\n'
                                   'There may be *no results* for your item on eBay. '
                                   'It might also be because there are no results with the matching search term. ',
                             inline=False)
        help_embed.add_field(name='What is the trimmed mean?',
                             value=f'The trimmed mean is the average of the results with the x% of results removed '
                                   f'from the lowest and highest values.\n'
                                   f'\n'
                                   f'For this search, the trimmed mean is set to '
                                   f'15%. 15% of the lowest and highest results are removed to remove any potential '
                                   f'outliers.',
                             inline=False)
        help_embed.add_field(name='Inflated prices',
                             value=f'If you come across higher/lower values than expected, it may be due to the search '
                                   f'filter being used is accounting for irrelevant items. Even with the trimmed mean '
                                   f'in-place, it cannot remove everything.\n '
                                   f'\n'
                                   f'Look at the prices displayed in the Range column. '
                                   f"If the range's lower value is quite low or the range's upper value is quite high, "
                                   f'accessories or other items may be included in the pool of results. ',
                             inline=False)
        help_embed.add_field(name='Low numbers of items being analysed',
                             value=f'Sometimes, there are a low number of items being analysed. This is due to there '
                                   f'not being as many items sold on eBay with the search filters being used. More '
                                   f'often, it may mean there is a lack of **used** items being sold.',
                             inline=False)
        help_embed.add_field(name='If everything fails',
                             value=f'Please use the manual [eBay Advanced search]'
                                   f'(https://www.ebay.co.uk/sch/ebayadvsearch) and go from there. This bot cannot help'
                                   f' you in this case. :( ',
                             inline=False)

        await ctx.send(embed=help_embed)

    elif ' ' in item or '' in item:
        # eBay wants to use + in place of spaces in the search term
        formatted_search_term = item.replace(" ", "+")

        soup = ebay_scraper.website_data(formatted_search_term)
        my_list = ebay_scraper.get_data(soup)

        # No items found in search result found and list is empty
        if not my_list:
            no_results_embed = discord.Embed(
                title=f'eBay Sold Items Search: {item}',
                description=f'There were 0 results for your search!',
                colour=0xce2d32,
            )

            no_results_embed.add_field(name='What happened?',
                                       value=f'- Make sure you spelt the item correctly, as the search filter is looking '
                                             f'for an exact match.\n'
                                             f'\n'
                                             f'- There may be 0 results for your item that are sold as used on eBay\n'
                                             f'\n'
                                             f'`!search help` may be able to help you',
                                       inline=False)
            no_results_embed.add_field(name='Bot no longer working',
                                       value=f'If you know that there are used items in the market and your spelling '
                                             f'is correct, then the bot may have been IP Blocked by eBay.\n'
                                             f'\n'
                                             f'In this case, it might be better for you to manually use the '
                                             f'[eBay Advanced search](https://www.ebay.co.uk/sch/ebayadvsearch) and '
                                             f'see the status of the market for your item.',
                                       inline=False)

            await ctx.send(embed=no_results_embed)

        # There are sold items in the search result and the list has values
        else:
            trim_percentage, trimmed_mean, median, mode = ebay_scraper.calculate_averages(my_list)

            # Calculating the total number of results in the list after trimming for the mean
            # Trimming leads to x number of values (rounded up) being removed from both sides of the list
            list_total = len(my_list)

            trimming = list_total * trim_percentage
            trimming = math.ceil(trimming)
            trimmings_for_both_sides = trimming * 2
            trimmed_list_total = list_total - trimmings_for_both_sides

            # Calculating values for the range after trimming
            my_sorted_list = sorted(my_list)

            minimum_value = min(my_sorted_list[trimming:])
            maximum_value = max(my_sorted_list[:-trimming])

            print(my_list)
            print(my_sorted_list)

            embed = discord.Embed(
                title=f'eBay Sold Items Search: {item}',
                description='The values below may not contain all of the sold items due to the filers being used on '
                            '[eBay Advanced search](https://www.ebay.co.uk/sch/ebayadvsearch). The results are trimmed '
                            f'by {int(trim_percentage * 100)}% to remove outliers. Use `!search help` for help.',
                colour=0x6b9312,
            )

            embed.add_field(name="Average Sold Price", value=f'£{trimmed_mean:.2f}', inline=False)
            embed.add_field(name="Median", value=f'£{median:.2f}', inline=True)
            embed.add_field(name="Mode", value=f'£{mode:.2f}', inline=True)
            embed.add_field(name="Range", value=f'£{minimum_value:.2f} to £{maximum_value:.2f}', inline=True)

            embed.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/EBay_logo.svg/2560px-'
                                    'EBay_logo.svg.png')
            embed.set_footer(text=f'There were a total of {list_total} search results. After trimming '
                                  f'{trimmings_for_both_sides}, there were {trimmed_list_total} left.',
                             icon_url='https://img.icons8.com/fluency/512/paid.png')

            await ctx.send(embed=embed)


bot.run(actives.token)
