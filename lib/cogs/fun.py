from random import choice, randint
from typing import Optional

from aiohttp import request
from discord import Member, Embed
from discord import HTTPException
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import BadArgument
from discord.ext.commands import command, cooldown


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="test")
    async def test(self, ctx):
        await ctx.send("Comando de prueba xd")

    @command(name="dice")
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split("d"))

        if dice <= 348:
            rolls = [randint(1, value) for i in range(dice)]

            await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

        else:
            await ctx.send(
                "Resultado demasiado grande. Trata con números más pequeños."
            )

    @command(name="slap")
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str]):
        await ctx.send(
            f"{ctx.author.mention} Le ha dado una Cachetada a {member.mention} {reason}"
        )

    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("No se ha podido encontrar al usuario.")

    @command(name="say")
    async def say_message(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    @command(name="animalfact")
    async def animal_fact(self, ctx, animal: str):
        if animal.lower() in ("dog", "cat", "panda", "fox", "bird", "koala"):
            apikey = "M9N0RZKSHKCV"
            lmt = 1
            animal_url = f"https://api.tenor.com/v1/random?q={animal.lower()}&key={apikey}&limit={lmt}&media_filter=minimal&contentfilter=high&ar_range=wide"
            fact_url = f"https://some-random-api.ml/facts/{animal}"

            async with request("GET", animal_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    animal_gif = data["results"][0]["media"][0]["gif"]["url"]

                else:
                    animal_gif = None

            async with request("GET", fact_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()

                    embed = Embed(
                        title=f"{animal.title()} Fact",
                        description=data["fact"],
                        colour=ctx.author.colour,
                    )

                    if animal_gif is not None:
                        embed.set_image(url=animal_gif)
                    await ctx.send(embed=embed)

                else:
                    await ctx.send(
                        f"La API ha respondido con el status {response.status()}."
                    )

        else:
            await ctx.send("No hay información disponible para ese animal.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
