import logging
import os
import asyncio
from datetime import datetime, timedelta
from flask import Flask, request
import telegram
from telegram import Update
from telegram.constants import ParseMode  # Updated import
from telegram.ext import CommandHandler, MessageHandler, filters

TOKEN = os.getenv('TOKEN')
CHAT_RULES = """
*Добро пожаловать в чат!* Пожалуйста, ознакомься с нашими правилами📜
*Всё серьёзно и очень строго!*

1. ❌ *Запрещены политические срачи и сопутствующий нацизм*. Вы вольны заниматься этим друг с другом в личных сообщениях, но в нашем чате это будет караться баном.

2. 📢 *Запрещена реклама*. При желании что-то пропиарить пишите - @JosieLoops.

3. 🔞 *Исторически в чате сложился весьма грубый уровень общения между участниками, но мы призываем уважать чувства друг друга*. Вы можете кидаться друг в друга говном, посылать нахер, другие оскорбления, но до тех пор, пока это несёт в себе шуточный подтекст и никого не задевает. Но если вам прямо говорят, что вы перегибаете палку - прекратите.
   В противном случае будет мут или бан, на усмотрение администрации и модерации.

4. 📸 *Можно выкладывать порнографию и другой 18+ NSFW контент самостоятельно в чат, но только под спойлером и желательно предупреждением*. Это касается контента по тематике канала и чата (Серия игр Fear and Hunger кто не понял). Треш контент иного характера запрещён.

5. 🍆 *Запрещено обсуждение половой жизни*, если другим участникам чата это неприятно. Карается мутом (общайтесь в ЛС на эту тему).
---

*Welcome to the chat!* Please read our rules📜
*Everything is serious and very strict!*

1. ❌ *Political arguments and accompanying Nazism are prohibited*. You are free to engage in this with each other in private messages, but in our chat, it will be punished by a ban.

2. 📢 *Advertising is forbidden*. If you want to promote something, write to @JosieLoops.

3. 🔞 *Historically, the chat has developed a rather rough level of communication between participants, but we urge you to respect each other's feelings*. You can throw shit at each other, send each other to hell, and use other insults, but only as long as it carries a joking connotation and doesn't offend anyone. But if you are directly told that you are crossing the line - stop.
   Otherwise, there will be a mute or ban at the discretion of the administration and moderation.

4. 📸 *You can post pornography and other 18+ NSFW content in the chat, but only under a spoiler and preferably with a warning*. This applies to content related to the theme of the channel and chat (the Fear and Hunger game series, for those who don't know). Trash content of other nature is prohibited.

5. 🍆 *Discussion of sexual life is prohibited* if other chat participants find it unpleasant. Punishable by mute (communicate in PM on this topic).
...
"""

welcome_times = {}
WELCOME_INTERVAL = timedelta(hours=12)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Create Flask app
app = Flask(__name__)
bot = telegram.Bot(token=TOKEN)

# Command to start the bot
async def start(update: Update, context) -> None:
    logging.info('Handled /start command from %s', update.message.from_user.username)
    await update.message.reply_text('Bee-bee. (I was created to help manage a telegram channel, devoted to the game F&H)')

# Function to send welcome messages to new chat members
async def send_welcome(update: Update, context) -> None:
    if update.message and update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if member.id != context.bot.id:
                now = datetime.now()
                if member.id in welcome_times:
                    last_welcome_time = welcome_times[member.id]
                    if now - last_welcome_time < WELCOME_INTERVAL:
                        continue
                welcome_times[member.id] = now
                mention_name = f"@{member.username}" if member.username else member.full_name
                await context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=f"Bee, {mention_name}!\n{CHAT_RULES}",
                    parse_mode=ParseMode.MARKDOWN  # Ensure the correct parse mode is used
                )

# Webhook route for Telegram to send updates
@app.route('/' + TOKEN, methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    if update.message:
        if update.message.new_chat_members:
            asyncio.run(send_welcome(update, None))
        elif update.message.text == "/start":
            asyncio.run(start(update, None))
    return 'ok'

# Basic route to check if the bot is running
@app.route('/')
def index():
    return 'Bot is running.'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
