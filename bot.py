import random
import telebot
from telebot import apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- НАСТРОЙКИ ---
TOKEN = "1780262862:uvQPZhoNlXN-0ZoQsMcZNRQDEQzN9VTPKhg"  # замени после revoke
SERVER_URL = "http://177.3.213.27:8081"

apihelper.API_URL = f"{SERVER_URL}/bot{{0}}/{{1}}"
apihelper.FILE_URL = f"{SERVER_URL}/file/bot{{0}}/{{1}}"

bot = telebot.TeleBot(TOKEN)

user_balances = {}
mines_games = {}

def get_balance(user_id):
    if user_id not in user_balances:
        user_balances[user_id] = 1000
    return user_balances[user_id]

# ---------- МЕНЮ ----------
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(text="🎰 Слоты (100)", callback_data="play_slots"),
        InlineKeyboardButton(text="🎲 Кубик (50)", callback_data="play_dice"),
        InlineKeyboardButton(text="✊ КНБ (50)", callback_data="play_rps"),
        InlineKeyboardButton(text="💣 Сапёр (100)", callback_data="play_mines"),
        InlineKeyboardButton(text="💰 Баланс", callback_data="check_balance"),
        InlineKeyboardButton(text="🎁 Бонус", callback_data="get_bonus")
    )
    return kb

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    balance = get_balance(user_id)
    bot.send_message(
        message.chat.id,
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"🎁 Добро пожаловать в GiftBattle!\n"
        f"💵 Баланс: {balance} монет.\n\n"
        f"Выбери игру:",
        reply_markup=main_menu()
    )

# ---------- ОБРАБОТКА КНОПОК ----------
@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    user_id = call.from_user.id
    balance = get_balance(user_id)
    data = call.data

    # --- БАЛАНС ---
    if data == "check_balance":
        bot.answer_callback_query(call.id, text=f"Баланс: {balance} монет", show_alert=True)
        return

    # --- БОНУС ---
    if data == "get_bonus":
        bonus = random.randint(50, 150)
        user_balances[user_id] += bonus
        bot.answer_callback_query(call.id, text=f"🎁 +{bonus} монет!", show_alert=True)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🎁 Бонус получен!\n💵 Баланс: {user_balances[user_id]}",
            reply_markup=main_menu()
        )
        return

    # --- СЛОТЫ ---
    if data == "play_slots":
        bet = 100
        if balance < bet:
            bot.answer_callback_query(call.id, text="❌ Мало монет!", show_alert=True)
            return
        user_balances[user_id] -= bet
        symbols = ["🍒", "🍋", "7️⃣", "💎"]
        spin = [random.choice(symbols) for _ in range(3)]
        spin_result = " | ".join(spin)
        roll = random.randint(1, 100)
        if roll == 1:
            win = random.randint(5000, 10000)
            user_balances[user_id] += win
            msg = f"🎰 [ {spin_result} ]\n\n💥 МЕГА-ДЖЕКПОТ!\n🎉 +{win} монет!"
        elif roll <= 25:
            win = bet * 2
            user_balances[user_id] += win
            msg = f"🎰 [ {spin_result} ]\n\n🎉 Выигрыш! +{win} монет."
        else:
            msg = f"🎰 [ {spin_result} ]\n\n😢 Не повезло."
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"{msg}\n\n💵 Баланс: {user_balances[user_id]}",
            reply_markup=main_menu()
        )
        return

    # --- КУБИК ---
    if data == "play_dice":
        bet = 50
        if balance < bet:
            bot.answer_callback_query(call.id, text="❌ Мало монет!", show_alert=True)
            return
        user_balances[user_id] -= bet
        dice = random.randint(1, 6)
        roll = random.randint(1, 100)
        if roll == 1:
            win = random.randint(5000, 10000)
            user_balances[user_id] += win
            msg = f"🎲 Выпало: {dice}\n\n💥 МЕГА-ДЖЕКПОТ!\n🎉 +{win} монет!"
        elif roll <= 25:
            win = bet * 2
            user_balances[user_id] += win
            msg = f"🎲 Выпало: {dice}\n\n🎉 Выигрыш! +{win} монет."
        else:
            msg = f"🎲 Выпало: {dice}\n\n😢 Проигрыш."
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"{msg}\n\n💵 Баланс: {user_balances[user_id]}",
            reply_markup=main_menu()
        )
        return

    # --- КАМЕНЬ НОЖНИЦЫ БУМАГА ---
    if data == "play_rps":
        kb = InlineKeyboardMarkup(row_width=3)
        kb.add(
            InlineKeyboardButton(text="✊ Камень", callback_data="rps_rock"),
            InlineKeyboardButton(text="✌️ Ножницы", callback_data="rps_scissors"),
            InlineKeyboardButton(text="✋ Бумага", callback_data="rps_paper"),
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_menu")
        )
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="✊✌️✋ Выбери свой ход (ставка 50):",
            reply_markup=kb
        )
        return

    if data in ("rps_rock", "rps_scissors", "rps_paper"):
        bet = 50
        if balance < bet:
            bot.answer_callback_query(call.id, text="❌ Мало монет!", show_alert=True)
            return
        user_balances[user_id] -= bet
        choice_map = {"rps_rock": "✊ Камень", "rps_scissors": "✌️ Ножницы", "rps_paper": "✋ Бумага"}
        user_choice = data
        bot_choice = random.choice(["rps_rock", "rps_scissors", "rps_paper"])
        beats = {"rps_rock": "rps_scissors", "rps_scissors": "rps_paper", "rps_paper": "rps_rock"}
        if user_choice == bot_choice:
            user_balances[user_id] += bet
            result = "🤝 Ничья! Ставка возвращена."
        elif beats[user_choice] == bot_choice:
            win = bet * 2
            user_balances[user_id] += win
            result = f"🎉 Ты победил! +{win} монет."
        else:
            result = "😢 Ты проиграл."
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=(
                f"Ты: {choice_map[user_choice]}\n"
                f"Бот: {choice_map[bot_choice]}\n\n"
                f"{result}\n\n💵 Баланс: {user_balances[user_id]}"
            ),
            reply_markup=main_menu()
        )
        return

    # --- САПЁР ---
    if data == "play_mines":
        bet = 100
        if balance < bet:
            bot.answer_callback_query(call.id, text="❌ Мало монет!", show_alert=True)
            return
        user_balances[user_id] -= bet
        cells = list(range(9))
        mine = random.choice(cells)
        mines_games[user_id] = {"mine": mine, "opened": set(), "bet": bet}
        kb = InlineKeyboardMarkup(row_width=3)
        buttons = [InlineKeyboardButton(text="❓", callback_data=f"mine_{i}") for i in range(9)]
        kb.add(*buttons)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"💣 Сапёр (ставка {bet})\nНайди безопасную клетку — выигрыш ×3. Одна мина!",
            reply_markup=kb
        )
        return

    if data.startswith("mine_"):
        game = mines_games.get(user_id)
        if not game:
            bot.answer_callback_query(call.id, text="Игра уже завершена. Начни заново.", show_alert=True)
            return
        idx = int(data.split("_")[1])
        if idx in game["opened"]:
            bot.answer_callback_query(call.id, text="Эта клетка уже открыта!", show_alert=True)
            return
        if idx == game["mine"]:
            kb = InlineKeyboardMarkup(row_width=3)
            buttons = []
            for i in range(9):
                if i == game["mine"]:
                    buttons.append(InlineKeyboardButton(text="💥", callback_data="noop"))
                else:
                    buttons.append(InlineKeyboardButton(text="⬜", callback_data="noop"))
            kb.add(*buttons)
            mines_games.pop(user_id, None)
            bot.answer_callback_query(call.id, text="💥 БУМ! Ты попал на мину.", show_alert=True)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"💥 БУМ! Ты проиграл {game['bet']} монет.\n\n💵 Баланс: {user_balances[user_id]}",
                reply_markup=main_menu()
            )
        else:
            game["opened"].add(idx)
            win = game["bet"] * 3
            user_balances[user_id] += win
            mines_games.pop(user_id, None)
            bot.answer_callback_query(call.id, text=f"🎉 Безопасно! +{win} монет", show_alert=True)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"🎉 Ты открыл безопасную клетку и выиграл {win} монет!\n\n💵 Баланс: {user_balances[user_id]}",
                reply_markup=main_menu()
            )
        return

    # --- НАЗАД В МЕНЮ ---
    if data == "back_menu":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🎁 GiftBattle — выбери игру:",
            reply_markup=main_menu()
        )
        return

    if data == "noop":
        bot.answer_callback_query(call.id)
        return

# ---------- ЗАПУСК ----------
if __name__ == "__main__":
    print("🚀 GiftBattle запущен...")
    bot.infinity_polling()