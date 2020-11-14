import discord
from discord.ext import commands
from datetime import datetime, timedelta

class CustomHelp(commands.HelpCommand):
    def __init__(self, **options):        
        self.width = options.pop('width', 30)
        self.indent = options.pop('indent', 2)
        self.sort_commands = options.pop('sort_commands', True)
        self.dm_help = options.pop('dm_help', False)
        self.dm_help_threshold = options.pop('dm_help_threshold', 1000)
        self.commands_heading = options.pop('commands_heading', "Commands:")
        self.no_category = options.pop('no_category', 'No Category')
        self.paginator = options.pop('paginator', None)

        if self.paginator is None:
            self.paginator = 'Paginator'

        super().__init__(**options)


    def shorten_text(self, text: str) -> str:
        if len(text) > 30:
            return text[:30 - 3] + '...'
        
        return text


    def get_description(self):
        command_name = self.invoked_with

        return (
               f'Type `{self.clean_prefix}{command_name} <command>` for more info on a command.\n'
               f'You can also type `{self.clean_prefix}{command_name} <category>` for more info on a category.'
               )


    def get_destination(self):
        ctx = self.context

        if self.dm_help is True:
            return ctx.author
        elif self.dm_help is None and len(self.paginator) > self.dm_help_threshold:
            return ctx.author
        else:
            return ctx.channel


    async def send_bot_help(self, mapping: dict) -> None:
        destination = self.get_destination()

        e = discord.Embed(title = 'Help', description = self.get_description(), colour = discord.Colour.blurple())
        e.set_thumbnail(url = self.context.bot.user.avatar_url)

        for cog, commands in mapping.items():
            if cog:
                e.add_field(name = cog.qualified_name, value = cog.description, inline = False)
            else:
                e.add_field(name = 'Core', value = 'core commands', inline = False)

            e.add_field(name = 'Command', value = '\n'.join(command.name for command in commands), inline = True)
            e.add_field(name = 'Usage', value = '\n'.join(self.shorten_text(command.help) if command.help else 'No description' for command in commands), inline = True)

        e.set_footer(text = f'Sent on {datetime.now().date()}')

        await destination.send(embed = e)


    async def send_command_help(self, command: commands.Command) -> None:
        destination = self.get_destination()

        e = discord.Embed(title = f'{command.name} help', colour = discord.Colour.blurple())
        e.set_thumbnail(url = self.context.bot.user.avatar_url)

        e.add_field(name = 'Command', value = command.name, inline = True)
        e.add_field(name = 'Usage', value = command.help, inline = True)

        e.set_footer(text = f'Sent on {datetime.now().date()}')

        await destination.send(embed = e)


    async def send_group_help(self, group):
        raise NotImplementedError('not implemented yet')


    async def send_cog_help(self, cog: commands.Cog) -> None:
        destination = self.get_destination()

        e = discord.Embed(title = f'{command.name} help', colour = discord.Colour.blurple())
        e.set_thumbnail(url = self.context.bot.user.avatar_url)

        if cog:
            e.add_field(name = cog.qualified_name, value = cog.value, inline = False)
        else:
            e.add_field(name = 'Core', value = 'core commands', inline = False)

        e.add_field(name = 'Command', value = '\n'.join(command.name for command in commands), inline = True)
        e.add_field(name = 'Usage', value = '\n'.join(command.help for command in commands), inline = True)
        
        e.set_footer(text = f'Sent on {datetime.now().date()}')

        await destination.send(embed = e)