import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# 1. Render 무료 플랜 유지를 위한 가짜 웹 서버 설정
app = Flask('')

@app.route('/')
def home():
    return "댕이가 살아있어요!"

def run():
    # Render는 기본적으로 8080 혹은 설정된 PORT 번호를 확인합니다.
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True # 메인 프로그램 종료 시 함께 종료되도록 설정
    t.start()

# 2. 디스코드 봇 설정 (인텐트 필수 설정)
# 최근 디스코드 업데이트로 인해 Intents 설정이 없으면 봇이 켜지지 않거나 메시지를 못 읽습니다.
intents = discord.Intents.default()
intents.message_content = True  # 채팅 내용을 읽을 수 있는 권한
intents.members = True          # 서버 멤버 정보를 읽을 수 있는 권한

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'--- 연결 성공 ---')
    print(f'봇 이름: {bot.user.name}')
    print(f'ID: {bot.user.id}')
    print(f'댕이 간식줘')
    print(f'------------------')

@bot.command()
async def 등록(ctx, *, name: str):
    await ctx.send(f"✅ {name} 등록이 완료되었습니다!")

@bot.command()
async def 안녕(ctx):
    await ctx.send(f"댕! 🐶")

# 3. 실제 실행 부분
if __name__ == "__main__":
    # 웹 서버를 먼저 실행하여 Render의 포트 체크를 통과시킵니다.
    print("가짜 웹 서버를 시작합니다...")
    keep_alive()
    
    # Render의 Environment 메뉴에 등록한 'BOT_TOKEN'을 가져옵니다.
    token = os.environ.get('BOT_TOKEN')
    
    if token:
        print("토큰을 찾았습니다. 디스코드 연결을 시도합니다...")
        try:
            bot.run(token)
        except Exception as e:
            print(f"봇 실행 중 에러가 발생했습니다: {e}")
    else:
        print("❌ 에러: Render 환경 변수(Environment)에 'BOT_TOKEN'이 설정되지 않았습니다.")