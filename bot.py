import discord

from discord.ext import commands

import re

from datetime import timedelta

intents = discord.Intents.default()

intents.message_content = True

intents.members = True

intents.moderation = True

bot = commands.Bot(command_prefix="?", intents=intents)

@bot.event

async def on_ready():

    print(f"Bot online como {bot.user}")

# ==================== HELP ====================

@bot.command(name="ajuda", aliases=["comandos", "cmds"])

async def help_command(ctx):

    embed = discord.Embed(

        title="Comandos de Moderação",

        description="Lista de comandos disponíveis:",

        color=discord.Color.blue()

    )

    embed.add_field(name="!clear <número>", value="Apaga mensagens (1-100)", inline=False)

    embed.add_field(name="!mute @pessoa <tempo> [motivo]", value="Mute (ex: 10m, 1h, 2d)", inline=False)

    embed.add_field(name="!unmute @pessoa", value="Remove o mute", inline=False)

    embed.add_field(name="!kick @pessoa [motivo]", value="Expulsa a pessoa", inline=False)

    embed.add_field(name="!ban @pessoa [motivo]", value="Bane a pessoa", inline=False)

    embed.add_field(name="!unban <id>", value="Desbane pelo ID da pessoa", inline=False)

    await ctx.send(embed=embed)

# ==================== CLEAR ====================

@bot.command(name="clear", aliases=["apagar", "purge"])

@commands.has_permissions(manage_messages=True)

async def clear(ctx, amount: int):

    if amount < 1 or amount > 100:

        await ctx.send("❌ Digite um número entre 1 e 100.\nExemplo: `!clear 20`")

        return

    try:

        deleted = await ctx.channel.purge(limit=amount + 1)

        msg = await ctx.send(f"✅ Apaguei **{len(deleted) - 1}** mensagens.")

        await msg.delete(delay=3)

    except Exception as e:

        print(e)

        await ctx.send("❌ Não consegui apagar as mensagens.")

@clear.error

async def clear_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.send("❌ Você não tem permissão pra apagar mensagens.")

    elif isinstance(error, commands.MissingRequiredArgument):

        await ctx.send("❌ Digite quantas mensagens quer apagar.\nExemplo: `!clear 20`")

# ==================== MUTE ====================

@bot.command(name="mute", aliases=["timeout", "silenciar"])

@commands.has_permissions(moderate_members=True)

async def mute(ctx, member: discord.Member, duration: str = "10m", *, reason: str = "Sem motivo"):

    if member.top_role >= ctx.author.top_role and ctx.guild.owner_id != ctx.author.id:

        await ctx.send("❌ Você não pode mutar alguém com cargo igual ou superior ao seu.")

        return

    if member.top_role >= ctx.guild.me.top_role:

        await ctx.send("❌ Não consigo mutar essa pessoa (cargo mais alto que o meu).")

        return

    time_delta = parse_duration(duration)

    if time_delta is None or time_delta > timedelta(days=28):

        await ctx.send("❌ Tempo inválido. Use: `10m`, `1h`, `2d` (máximo 28 dias)")

        return

    try:

        await member.timeout(time_delta, reason=reason)

        await ctx.send(f"🔇 **{member}** foi mutado por **{duration}**.\nMotivo: {reason}")

    except Exception as e:

        print(e)

        await ctx.send("❌ Erro ao mutar o membro.")

@mute.error

async def mute_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.send("❌ Você não tem permissão pra mutar.")

    elif isinstance(error, commands.MissingRequiredArgument):

        await ctx.send("❌ Mencione alguém.\nExemplo: `!mute @pessoa 10m motivo`")

    elif isinstance(error, commands.MemberNotFound):

        await ctx.send("❌ Não encontrei essa pessoa.")

# ==================== UNMUTE ====================

@bot.command(name="unmute", aliases=["desmutar"])

@commands.has_permissions(moderate_members=True)

async def unmute(ctx, member: discord.Member):

    try:

        await member.timeout(None)

        await ctx.send(f"🔊 **{member}** foi desmutado.")

    except Exception as e:

        print(e)

        await ctx.send("❌ Erro ao desmutar.")

@unmute.error

async def unmute_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.send("❌ Você não tem permissão.")

    elif isinstance(error, commands.MissingRequiredArgument):

        await ctx.send("❌ Mencione alguém pra desmutar.")

# ==================== KICK ====================

@bot.command(name="kick", aliases=["expulsar"])

@commands.has_permissions(kick_members=True)

async def kick(ctx, member: discord.Member, *, reason: str = "Sem motivo"):

    if member.top_role >= ctx.author.top_role and ctx.guild.owner_id != ctx.author.id:

        await ctx.send("❌ Você não pode kickar alguém com cargo igual ou superior ao seu.")

        return

    if member.top_role >= ctx.guild.me.top_role:

        await ctx.send("❌ Não consigo kickar essa pessoa.")

        return

    try:

        await member.kick(reason=reason)

        await ctx.send(f"👢 **{member}** foi expulso.\nMotivo: {reason}")

    except Exception as e:

        print(e)

        await ctx.send("❌ Erro ao expulsar o membro.")

@kick.error

async def kick_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.send("❌ Você não tem permissão pra kickar.")

    elif isinstance(error, commands.MissingRequiredArgument):

        await ctx.send("❌ Mencione alguém.\nExemplo: `!kick @pessoa motivo`")

    elif isinstance(error, commands.MemberNotFound):

        await ctx.send("❌ Não encontrei essa pessoa.")

# ==================== BAN ====================

@bot.command(name="ban", aliases=["banir"])

@commands.has_permissions(ban_members=True)

async def ban(ctx, member: discord.Member, *, reason: str = "Sem motivo"):

    if member.top_role >= ctx.author.top_role and ctx.guild.owner_id != ctx.author.id:

        await ctx.send("❌ Você não pode banir alguém com cargo igual ou superior ao seu.")

        return

    if member.top_role >= ctx.guild.me.top_role:

        await ctx.send("❌ Não consigo banir essa pessoa.")

        return

    try:

        await member.ban(reason=reason)

        await ctx.send(f"🔨 **{member}** foi banido.\nMotivo: {reason}")

    except Exception as e:

        print(e)

        await ctx.send("❌ Erro ao banir o membro.")

@ban.error

async def ban_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.send("❌ Você não tem permissão pra banir.")

    elif isinstance(error, commands.MissingRequiredArgument):

        await ctx.send("❌ Mencione alguém.\nExemplo: `!ban @pessoa motivo`")

    elif isinstance(error, commands.MemberNotFound):

        await ctx.send("❌ Não encontrei essa pessoa.")

# ==================== UNBAN ====================

@bot.command(name="unban", aliases=["desbanir"])

@commands.has_permissions(ban_members=True)

async def unban(ctx, user_id: int):

    try:

        user = await bot.fetch_user(user_id)

        await ctx.guild.unban(user)

        await ctx.send(f"✅ **{user}** foi desbanido.")

    except Exception as e:

        print(e)

        await ctx.send("❌ Não consegui desbanir. Verifique se o ID está correto.")

@unban.error

async def unban_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.send("❌ Você não tem permissão pra desbanir.")

    elif isinstance(error, commands.MissingRequiredArgument):

        await ctx.send("❌ Digite o ID da pessoa.\nExemplo: `!unban 123456789012345678`")

    elif isinstance(error, commands.BadArgument):

        await ctx.send("❌ ID inválido. Digite só os números.")

# Função de tempo

def parse_duration(duration: str):

    match = re.match(r"^(\d+)(s|m|h|d)$", duration.lower())

    if not match:

        return None

    num = int(match.group(1))

    unit = match.group(2)

    if unit == "s":

        return timedelta(seconds=num)

    elif unit == "m":

        return timedelta(minutes=num)

    elif unit == "h":

        return timedelta(hours=num)

    elif unit == "d":

        return timedelta(days=num)

    return None

# Coloca seu token aqui

bot.run("MTU1NDMyMjUzNjQ1ODc1NjE4OA.GF-0ro.EwgvqUw3FHg4EyCmudr1l6avJfcxgtOun_UY9Y")
