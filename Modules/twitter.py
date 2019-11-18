#TenshiBot twitter module

#ratelimiting options
#number of commands which can be ran in timeframe
rlimit_cmd = 2
#timeframe (seconds)
rlimit_time = 120

#Account age options
#How many days old the account needs to be
dayspassed = 30

import discord
import aiohttp
import praw
import lxml
import random
import asyncio
import twitter
import datetime 

from discord.ext import commands
from urlextract import URLExtract
from profanityfilter import ProfanityFilter
from datetime import datetime, timedelta

#twitter stuff
t_api = open("Tokens/twitter_consumer.txt", "r")
tw_api = t_api.read()
t_secret = open("Tokens/twitter_consumer_secret.txt", "r")
tw_secret = t_secret.read()
t_access = open("Tokens/twitter_access.txt", "r")
tw_access = t_access.read()
t_access_secret = open("Tokens/twitter_access_secret.txt", "r")
tw_access_secret = t_access_secret.read()

api = twitter.Api(consumer_key=tw_api,
consumer_secret=tw_secret,
access_token_key=tw_access,
access_token_secret=tw_access_secret)

#url extractor stuff
extractor = URLExtract()

pf = ProfanityFilter()
pf_extended = ProfanityFilter(extra_censor_list=["@"])

user_blacklist = open("txt/badactors.txt", "r")
badactors = user_blacklist.read()

acc_age = datetime.now() - timedelta(days=dayspassed)

#owner check
#19/05 U+1F382
def is_owner():
    async def predicate(ctx):
        return ctx.author.id == 166189271244472320
    return commands.check(predicate)

def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

class twitterCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.cooldown(rlimit_cmd, rlimit_time, commands.BucketType.default)
    async def sendtweet(self, ctx, *, args):
        userid = str(ctx.author.id)
        
        #convert text to ascii
        asciitext = strip_non_ascii(args)
        asciiusername = strip_non_ascii(ctx.author.name)
        if asciitext == '':
            await ctx.send('Error: Tweet contains no alphanumeric characters')
        #check username for profanity
        if pf.is_profane(asciiusername) == True:
            await ctx.send('Error: Your Discord username is unsupported')
            return
        #link check
        if extractor.has_urls(asciitext):
            await ctx.send('Error: URL is unsupported')
            return
        if "@" in asciitext:
            await ctx.send('Error: Invalid tweet')
            return
        if int(ctx.guild.id) == int("162861213309599744"):
            await ctx.send('Error: Please use 1CCBot here')
            return
        if str(ctx.author.id) in badactors:
            await ctx.send('Error: You have been blacklisted')
            return

        else:
            em = discord.Embed(title='Are you sure you want to tweet this?', description = asciitext, colour=0x6aeb7b)
            em.set_author(name='KawashiroLink Subsystem' , icon_url=self.bot.user.avatar_url)
            em.set_footer(text="Follow me @HinanawiBot")
            tweetconfirm = await ctx.send(embed=em)
            #tweetconfirm = await ctx.send('Are you sure you want to tweet this?')
            #add tick and X reactions for user to react to
            await tweetconfirm.add_reaction('\U00002705')
            await tweetconfirm.add_reaction('\U0000274e')

            def ays_tweet(reaction, user):
                return (user == ctx.author and str(reaction.emoji) == '\U00002705') or (user == ctx.author and str(reaction.emoji) == '\U0000274e')
                                   
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=ays_tweet)
            except asyncio.TimeoutError:
                await ctx.send('Error: Timed out waiting for user response')
                return
            else:
                if ((reaction.emoji) == '\U00002705') and reaction.message.id == tweetconfirm.id:
                    #Profanity check tweet and add username before sending
                    finaltweet = ('[' + ctx.author.name + '] ' + pf.censor(asciitext))
                    api.PostUpdate(finaltweet)
                    print('[tweet] "' + finaltweet + '" User ID: :' + str(ctx.author.id))
                    await ctx.send('Tweet Posted')
                    #DM me about the tweet if i need to go delete it
                    yuyuko = self.bot.get_user(166189271244472320)
                    await yuyuko.send("**--A tweet was sent--** \nContents: " + finaltweet + "\nUnfiltered contents: " + asciitext + "\nUser ID: " + userid)
                    return
                elif ((reaction.emoji) == '\U0000274e'):
                    await ctx.send('Operation canceled')
                    return


    @commands.command()
    @is_owner()
    async def posttweet(self, ctx, *, args):
        em = discord.Embed(title='Are you sure you want to tweet this?', description = args, colour=0x6aeb7b)
        em.set_author(name='KawashiroLink (Admin Mode)' , icon_url=self.bot.user.avatar_url)
        tweetconfirm = await ctx.send(embed=em)
        #tweetconfirm = await ctx.send('Are you sure you want to tweet this?')
        #add tick and X reactions for user to react to
        await tweetconfirm.add_reaction('\U00002705')
        await tweetconfirm.add_reaction('\U0000274e')

        def ays_tweet(reaction, user):
            return (user == ctx.author and str(reaction.emoji) == '\U00002705') or (user == ctx.author and str(reaction.emoji) == '\U0000274e')
                                   
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=ays_tweet)
        except asyncio.TimeoutError:
            await ctx.send('Error: Timed out waiting for user response')
            return
        else:
            if ((reaction.emoji) == '\U00002705') and reaction.message.id == tweetconfirm.id:
                #Profanity check tweet and add username before sending
                finaltweet = ('[' + ctx.author.name + '] ' + args)
                api.PostUpdate(finaltweet)
                print('[tweet] "' + finaltweet + '" User ID: :' + str(ctx.author.id))
                await ctx.send('Tweet Posted')
                return
            elif ((reaction.emoji) == '\U0000274e'):
                await ctx.send('Operation canceled')
                return

    @commands.command()
    @is_owner()
    async def dumptwitterinfo(ctx):
        await ctx.send(api.VerifyCredentials())

    @commands.command()
    @is_owner()
    async def censortest(ctx, *, args):
        await ctx.send(pf.censor(args))

    @commands.command()
    @is_owner()
    async def censortestascii(ctx, *, args):
        asciitext = strip_non_ascii(args)
        await ctx.send(pf.censor(asciitext))    

    @commands.command()
    @is_owner()
    async def extendedcensortest(ctx, *, args):
        await ctx.send(pf_extended.censor(args))    


    @commands.command()
    @commands.cooldown(2, 60, commands.BucketType.default)
    @is_owner()
    async def asciitest(ctx, *, args):
        asciitext = strip_non_ascii(args)
        if asciitext == '':
            await ctx.send('invalid char')
        else:
            await ctx.send(asciitext)					                    

def setup(bot):
    bot.add_cog(twitterCog(bot))
