import discord
from types import SimpleNamespace
import traceback
import toml
import re
import tracklist as tl
import sys

CONFIG = SimpleNamespace(**toml.load(open('config.toml')))
NowPlaying = {}
CurrentSet = {}

def is_admin(user):
    return True if user in CONFIG.admins else False

class CommandHandler:
    @staticmethod
    async def prefix(args, message):
        if not is_admin(str(message.author)):
            return
        CONFIG.prefix = args[0]
        await message.channel.send(f'Changed command prefix to: {CONFIG.prefix}')

    @staticmethod
    async def quit(args, message):
        if not is_admin(str(message.author)):
            return
        await message.channel.send('Quitting')
        await client.logout()
        sys.exit(0)

    @staticmethod
    async def hello(args, message):
        await message.channel.send(f'Hello {message.author.mention}!')

    @staticmethod
    async def help(args, message):
        await message.channel.send('''
-np to show currently playing set on groovy
then use !track to check tracklist for track
        ''')

    @staticmethod
    async def track(args, message):
        global CurrentSet
        global NowPlaying
        if not NowPlaying:
            return

        async with message.channel.typing():
            await message.channel.send(f'At {NowPlaying["time"]} of {NowPlaying["title"]}')

            if NowPlaying['changed']:
                CurrentSet = tl.parse_tracklist(
                    tl.search_sets(NowPlaying['title'])[0]
                )

            await message.channel.send(f'Found {CurrentSet["name"]} {CurrentSet["duration"]}')
            current_track = tl.find_track_at(NowPlaying['time'], CurrentSet)
            await message.channel.send(f'Now Playing: {current_track["name"]}')

class TracklistBot(discord.Client):
    async def on_ready(self):
        print(f'{self.user} Online.')

    async def on_message(self, message):
        print(f'Message | {message.author}: {message.content}')

        if (str(message.author) in CONFIG.watch
        and message.channel.name in CONFIG.channels):
            parse_bot(message)

        if not (message.content.startswith(CONFIG.prefix)
            and not message.author.bot
            and message.channel.name in CONFIG.channels):
            return

        command = message.content.strip()[1:].split()

        await getattr(CommandHandler, command[0].lower())(command[1:], message)
        # try:
        #     await getattr(CommandHandler, command[0].lower())(command[1:], message)
        # except AttributeError as e:
        #     traceback.print_stack()
        #     print(e)


def parse_bot(message):
    global NowPlaying
    title = re.findall(r'\[(.+?)\]', message.embeds[0].description)[0]
    time = re.findall(r'\s(\d.+?)\s\/', message.embeds[0].footer.text)[0]
    time = re.findall(r'(\d+?)[A-Za-z]{1,3}', time)
    time = tl.to_time_delta(':'.join(time))
    changed = True
    if NowPlaying:
        changed = True if NowPlaying['title'] != title else False

    NowPlaying = {
        'title': title,
        'time': time,
        'changed': changed
    }

client = TracklistBot()
client.run(CONFIG.token)