import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import json
from flask import Flask
from threading import Thread

# --- 1. Render 유지를 위한 웹 서버 ---
app = Flask('')
@app.route('/')
def home(): return "댕이가 살아있어요!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. 데이터 저장 및 로드 함수 ---
DB_FILE = "scores.json"

def load_scores():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_scores(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 점수 데이터 초기 로드
scores = load_scores()

# --- 3. 봇 설정 ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 4. 버튼 클래스 설정 ---
class ScoreView(View):
    def __init__(self):
        super().__init__(timeout=None)

    def create_embed(self):
        embed = discord.Embed(title="⚠️ 욕설 점수판 (포인트 대결)", color=0xff0000)
        if not scores:
            embed.description = "아직 등록된 멤버가 없어요. '!등록 이름'으로 시작하세요!"
        else:
            # 점수 높은 순으로 정렬
            rank = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            board = ""
            for name, score in rank:
                board += f"**{name}**: {score}점\n"
            embed.description = board
        return embed

    @discord.ui.button(label="+1", style=discord.ButtonStyle.green)
    async def plus_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_score(interaction, 1)

    @discord.ui.button(label="+5", style=discord.ButtonStyle.success)
    async def plus_five(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_score(interaction, 5)

    @discord.ui.button(label="-1", style=discord.ButtonStyle.danger)
    async def minus_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_score(interaction, -1)

    async def update_score(self, interaction, amount):
        name = interaction.user.display_name
        if name not in scores:
            scores[name] = 0
        scores[name] += amount
        
        # 데이터 저장
        save_scores(scores)
        
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

# --- 5. 봇 명령어 ---
@bot.event
async def on_ready():
    print(f'--- {bot.user.name} 연결 성공 (데이터 로드 완료) ---')

@bot.command()
async def 점수판(ctx):
    view = ScoreView()
    await ctx.send(embed=view.create_embed(), view=view)

@bot.command()
async def 등록(ctx, *, name: str):
    if name not in scores:
        scores[name] = 0
        save_scores(scores) # 등록 즉시 저장
        await ctx.send(f"✅ {name}님이 점수판에 등록되었습니다.")
    else:
        await ctx.send(f"이미 등록된 이름입니다.")

# --- 6. 실행 ---
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('BOT_TOKEN')
    if token:
        bot.run(token)
    else:
        print("토큰을 찾을 수 없습니다!")