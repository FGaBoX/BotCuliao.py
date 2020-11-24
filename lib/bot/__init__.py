import discord
from asyncio import sleep
from datetime import datetime
from glob import glob

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Embed, File, DMChannel
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import (
    CommandNotFound,
    BadArgument,
    MissingRequiredArgument,
    CommandOnCooldown,
)
from discord.ext.commands import when_mentioned_or, command, has_permissions
from discord import Intents


from ..db import db

PREFIX = "+"
OWNER_IDS = [472788394410246144]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXEPTIONS = (CommandNotFound, BadArgument)


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"{cog} cog listo")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)
        super().__init__(
            command_prefix=PREFIX,
            owner_ids=OWNER_IDS,
            intents=Intents.all(),
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog cargado.")

        print("Inicio Completado.")

    def run(self, version):
        self.VERSION = version
        print("Ejecutando inicio.")
        self.setup()

        with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("Ejecutando Bot...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send(
                    "No estoy preparado para usar comandos aun. Por favor espera."
                )

    async def rules_reminder(self):
        channel = self.get_channel(779791532290342932)
        await channel.send("Soy una notificación programada.")

    async def on_connect(self):
        print("Bot Conectado")

    async def on_disconnect(self):
        print("Bot Desconectado")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Algo salió mal.")
            await self.stdout.send("Ha ocurrido un error.")
            raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXEPTIONS]):
            pass

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("Faltan uno o más argumentos requeridos.")

        elif isinstance(exc.original, HTTPException):
            await ctx.send("No se ha podido enviar el mensaje.")

        elif isinstance(exc.original, Forbidden):
            await ctx.send("No tengo permisos para hacer eso")

        else:
            raise exc.original

    async def on_ready(self):
        if not self.ready:
            self.scheduler.start()
            self.scheduler.add_job(self.rules_reminder, CronTrigger(second="0"))
            self.stdout = self.get_channel(777178109103439873)
            channel = self.get_channel(777178109103439873)
            # embed = Embed(
            #     title="Bot Online :)",
            #     description="El Bot está funcionando correctamente",
            #     color=0x2BB319,
            # )
            # embed.set_author(
            #     name="FGaBoX Trolleos",
            #     url="https://cdn.discordapp.com/avatars/472788394410246144/17f2b7a36321e81dcb91667327f56a47.png?size=4096",
            # )
            # embed.set_thumbnail(
            #     url="https://cdn.discordapp.com/avatars/472788394410246144/17f2b7a36321e81dcb91667327f56a47.png?size=4096"
            # )
            # embed.add_field(name="Campo alineado", value="Algún valor", inline=True)
            # embed.add_field(
            #     name="Otro campo alineado", value="Algún otro valor", inline=True
            # )
            # embed.add_field(
            #     name="Un campo normal",
            #     value="Este campo aparecerá en su propia linea",
            #     inline=False,
            # )
            # embed.set_footer(text="FGaBoX Trolleos")
            # await channel.send(embed=embed)
            await bot.change_presence(
                activity=discord.Game(name="Desarrollado En Python 🐍")
            )

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            print("Bot Listo")
        else:
            print("Bot Reconectado")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()