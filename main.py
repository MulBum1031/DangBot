
import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os

# 데이터 저장 파일 설정
DATA_FILE = "users.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 버튼 뷰 클래스 ---
class BadWordView(View):
    def __init__(self, target_name):
        super().__init__(timeout=None)
        self.target_name = target_name

    async def update_score(self, interaction, amount):
        data = load_data()
        if self.target_name in data:
            data[self.target_name] += amount
            if data[self.target_name] < 0: data[self.target_name] = 0
            save_data(data)
            await interaction.response.send_message(f"'{self.target_name}'님의 욕 횟수가 {amount}만큼 변경되었습니다.", ephemeral=True)
        else:
            await interaction.response.send_message("등록되지 않은 사용자입니다.", ephemeral=True)

    @discord.ui.button(label="+1", style=discord.ButtonStyle.danger)
    async def plus_one(self, interaction: discord.Interaction, button: Button):
        await self.update_score(interaction, 1)

    @discord.ui.button(label="+5", style=discord.ButtonStyle.secondary)
    async def plus_five(self, interaction: discord.Interaction, button: Button):
        await self.update_score(interaction, 5)

    @discord.ui.button(label="-1", style=discord.ButtonStyle.success)
    async def minus_one(self, interaction: discord.Interaction, button: Button):
        await self.update_score(interaction, -1)

# --- 봇 명령어 ---

@bot.event
async def on_ready():
    print(f'봇 이름: {bot.user.name} (댕이) 연결 완료!')

@bot.command(name="등록")
async def register(ctx, name: str):
    data = load_data()
    if name in data:
        await ctx.send(f"이미 '{name}'님은 등록되어 있습니다.")
    else:
        data[name] = 0
        save_data(data)
        await ctx.send(f"'{name}'님이 댕이의 명단에 등록되었습니다!")

@bot.command(name="욕")
async def show_status(ctx):
    data = load_data()
    if not data:
        await ctx.send("등록된 사용자가 없습니다. `!등록 <이름>`으로 먼저 등록해주세요.")
        return

    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    embed = discord.Embed(title="🚨 욕설 횟수 현황판 🚨", color=discord.Color.red())
    
    status_text = ""
    for name, count in sorted_data:
        status_text += f"**이름:** {name} | **횟수:** {count}회\n"
        status_text += "----------------------------------\n"
    
    embed.description = status_text
    top_user = sorted_data[0][0]
    view = BadWordView(top_user)
    
    await ctx.send(content=f"가장 점수가 높은 **{top_user}**님에 대한 조절 버튼입니다:", embed=embed, view=view)

# --- 서버장 전용 초기화 명령어 ---
@bot.command(name="초기화")
async def reset_data(ctx):
    # 명령어를 입력한 사람이 서버장(Owner)인지 확인
    if ctx.author == ctx.guild.owner:
        save_data({}) # 빈 딕셔너리를 저장하여 데이터 삭제
        await ctx.send("⚠️ 서버장에 의해 모든 욕설 데이터가 초기화되었습니다.")
    else:
        await ctx.send("❌ 이 명령어는 서버장만 사용할 수 있습니다.")

# Render 환경 변수 설정 (보안 강화)
token = os.environ.get('MTQzNzY5MzEzMTE4MDA4NTI1OQ.GnVajB.x4gQa5wC9OEVOOgPf1y7x1a1CMIAer4dN7slrM')
bot.run(token)