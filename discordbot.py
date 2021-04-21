import discord
from discord.ext import tasks
import pandas as pd
import random
import time

# ここにチャンネルID
gbm_channel_id = 834402896543088651

vcc = discord.VoiceChannel
vc = discord.VoiceClient
music_flag = False
music_message = discord.Message

# ここのファイルはお好みで
data = pd.read_csv(filepath_or_buffer="list.csv", encoding="utf-8", sep="\t")

class Bot :
    client = discord.Client()

bot = Bot()

async def music_start(message):
    global vc
    global music_flag

    if vc.is_playing() == False and vc.is_paused() == False:
        music_num = random.randint(0 , len(data)-1 )
        filename = data.loc[ music_num , ["場所"]].tolist()[0]
        name = data.loc[ music_num , ["名前"]].tolist()[0]
        album = data.loc[ music_num , ["アルバム"]].tolist()[0]
        artist = data.loc[ music_num , ["アーティスト"]].tolist()[0]
        #name = data.loc[ music_num , ["名前"]].tolist()[0]
        #name = data.loc[ music_num , ["名前"]].tolist()[0]

        if vc != discord.VoiceClient and vc.is_connected() == True:
            source = discord.FFmpegPCMAudio(filename , options='-application audio')
            vc.play(source)
            await message.channel.send('```\nタイトル：{}\nアーティスト：{}\nアルバム：{}\n```'.format(name , artist , album ))
        else :
            await message.channel.send('まだ再生準備が整ってないみたいだよ！')
            music_flag = False


@bot.client.event
async def on_ready():
    print("discordへの接続OK-!")

@bot.client.event
async def on_message(message):
    global vc
    global vcc
    global music_flag
    global music_message

    if message.author.bot:
        return

    # 専用チャンネル以外では、反応させない。
    if message.channel.id == gbm_channel_id :

        if message.content == ("connect"):
            if message.author.voice.channel is not None :
                if vc == discord.VoiceClient or vc.is_connected() == False:
                    await message.channel.send('ハロハロー！「接続完了であります！」がでるまで待っててね！')
                    vcc = message.author.voice.channel
                    vc = await vcc.connect()
                    await message.channel.send('接続完了であります！')
                    loop.start()
                else :
                    await message.channel.send('接続済みです。Over！')
            else :
                await message.channel.send('お主、ボイチャに入っていないのでは？')

        elif message.content == ("bgm"):
            music_flag = True
            music_message = message
            await music_start(message)  

        elif message.content == ("next"):
            if vc.is_connected() == True and vc.is_playing() == True and music_flag == True:
                vc.stop()
                music_start(message)
                await message.channel.send('次の曲へスキップしました。')
            else :
                await message.channel.send('そもそも、接続されてないよ！')

        elif message.content == ("stop"):
            if vc.is_connected() == True and vc.is_playing() == True and music_flag == True:
                vc.stop()
                music_flag = False
                music_stop_flag = False
                await message.channel.send('停止しました。')
            else :
                await message.channel.send('そもそも、接続されてないよ！')

        elif message.content == ("pause"):
            if vc.is_connected() == True and vc.is_playing() == True:
                vc.pause()
                await message.channel.send('一時停止にしました。')
            else :
                await message.channel.send('そもそも、接続されてないよ！')

        elif message.content == ("resume"):
            if vc.is_connected() == True:
                vc.resume()
                await message.channel.send('再生再開しました。')
            else :
                await message.channel.send('そもそも、接続されてないよ！')

        elif message.content == ("clone"):
            if vc.is_connected() == True:
                await message.channel.send('切断作業中....。')
                if vc.is_playing() == True :
                    vc.stop()           
                await vc.disconnect()
                loop.stop()
                await message.channel.send('切断しました。byebye！')
            else :
                await message.channel.send('そもそも、接続されてないよ！')

        elif message.content == ("exit"):
            await message.channel.send('電源落ちますー！')
            await bot.client.logout()

@tasks.loop(seconds=3)
async def loop():
    global music_message
    global music_flag
    if music_flag == True :
        await music_start(music_message)

try:
    bot.client.run("とーくん")

except RuntimeError :
    loop.cancel()
    print("強制終了したぜよ")
