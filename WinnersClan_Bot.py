import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= НАСТРОЙКИ =================
import os

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в переменных окружения")


ADMINS = [
    6016434146,
    6124956908
]

MODERS = [
    8315178490
]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ================= ХРАНЕНИЕ =================
applications = {}   # user_id: data
complaints = []     # список жалоб

# ================= ТЕКСТЫ =================
RULES_TEXT = """📜 ПРАВИЛА КЛАНА WINNERS (HypeMC)

🎤 A. Общение:
A1. Оскорбление участников клана (смотреть пункт 2.3 правил сервера).
Наказание: 2.3 + П → 3 П = К.

A2. Оскорбление главы/персонала клана (смотреть пункт 2.3 правил сервера).
Наказание: 2.3 + Б.

A3. Необоснованная критика персонала.
Наказание: П.

A4. Необоснованная критика клана.
Наказание: П.

A5. Политические обсуждения (смотреть пункт 2.4 правил сервера).
Наказание: 2.4 + П.

A6. Телепортация без согласия (смотреть пункт 4.5 правил сервера).
Наказание: 4.5 + П.


🎮 B. Игровые нарушения:

B1. Гриферство кланового дома (смотреть пункт 4.1 и 4.4 правил сервера).
Наказание:
├─ Если игрок был в регионе: 4.1 + Б.
└─ Если не был: 4.4 + Б.

B2. Реклама сторонних кланов.
Наказание: П.
• Запрещена любая реклама кланов (кроме союзных)
• Запрещено склонять игроков к уходу из клана.

B3. Злоупотребление правами рангов.
Наказание: Б.

B4. Использование нечестного ПО (смотреть пункт 3.1 правил сервера).
Наказание: Б.

B5. Автоматическое соглашение.
▸ Игрок, заходя на сервер HypeMC, автоматически соглашается с правилами сервера.
▸ Игрок, вступая в клан Winners, автоматически соглашается с правилами клана.
▸ Незнание правил не освобождает от ответственности!.

B6. Переход в другой клан.
Наказание: Бан в клановой группе (если был).

📌 C. Дополнения:

• Администрация вправе выдать Б/К без объяснений.
•Администрация вправе помиловать на своё усмотрение за то, или иное 
нарушение.
•При добавлении игрока в регион клана, Администратор клана обязан проверять /alts (ник игрока).

Сокращения:
П — предупреждение (3 П = К)
К — кик из клана
Б — бан в клане (кик + ЧС)
"""

CLAN_TEXT = """👑 АДМИНИСТРАЦИЯ КЛАНА WINNERS

👑 Leader | DreamKing345
@FiliMonkiTY

🛡 ViceLeader | Recriver
@Danverion

⚔ GlAdmin | RenCh2k
@RenCh2k

👥 Moder:
• nuntus999
• KlayPlay
"""

# ================= КЛАВИАТУРЫ =================
def main_menu(user_id: int):
    keyboard = [
        [
            types.KeyboardButton(text="📜 Правила"),
            types.KeyboardButton(text="📝 Набор в модерацию")
        ],
        [
            types.KeyboardButton(text="👑 Состав клана"),
            types.KeyboardButton(text="🚨 Подать жалобу")
        ]
    ]
    if user_id in ADMINS or user_id in MODERS:
        keyboard.append([types.KeyboardButton(text="⚙ Админ-панель")])

    return types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def admin_panel_menu(user_id: int):
    keyboard = []

    if user_id in ADMINS:
        keyboard.append([types.KeyboardButton(text="📋 Заявки в модерацию")])

    keyboard.append([types.KeyboardButton(text="🚨 Жалобы")])
    keyboard.append([types.KeyboardButton(text="🔙 Назад")])

    return types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)

# ================= INLINE =================
def decision_buttons(prefix: str, user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Принять", callback_data=f"{prefix}_accept:{user_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"{prefix}_reject:{user_id}")
    ]])

# ================= FSM =================
class Application(StatesGroup):
    nick = State()
    tg = State()
    name = State()
    age = State()
    about = State()
    exp = State()
    time = State()

class Complaint(StatesGroup):
    nick = State()
    reason = State()
    proof = State()

# ================= START =================
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎮 Добро пожаловать в бот клана WINNERS",
        reply_markup=main_menu(message.from_user.id)
    )

# ================= ОСНОВНЫЕ =================
@dp.message(lambda m: m.text == "📜 Правила")
async def rules(message: types.Message):
    await message.answer(RULES_TEXT)

@dp.message(lambda m: m.text == "👑 Состав клана")
async def clan(message: types.Message):
    await message.answer(CLAN_TEXT)

# ================= АДМИН-ПАНЕЛЬ =================
@dp.message(lambda m: m.text == "⚙ Админ-панель")
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMINS and message.from_user.id not in MODERS:
        return
    await message.answer(
        "⚙ АДМИН-ПАНЕЛЬ",
        reply_markup=admin_panel_menu(message.from_user.id)
    )

@dp.message(lambda m: m.text == "🔙 Назад")
async def back(message: types.Message):
    await message.answer("Главное меню", reply_markup=main_menu(message.from_user.id))

# ================= ЗАЯВКИ =================
@dp.message(lambda m: m.text == "📋 Заявки в модерацию")
async def show_apps(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    if not applications:
        await message.answer("📭 Заявок нет")
        return

    for uid, data in applications.items():
        text = (
            "📝 ЗАЯВКА В МОДЕРАЦИЮ\n\n"
            f"Ник: {data['nick']}\n"
            f"TG: {data['tg']}\n"
            f"Имя: {data['name']}\n"
            f"Возраст: {data['age']}\n"
            f"О себе: {data['about']}\n"
            f"Опыт: {data['exp']}\n"
            f"Время: {data['time']}"
        )
        await message.answer(text, reply_markup=decision_buttons("app", uid))

# ================= ЖАЛОБЫ =================
@dp.message(lambda m: m.text == "🚨 Жалобы")
async def show_complaints(message: types.Message):
    if message.from_user.id not in ADMINS and message.from_user.id not in MODERS:
        return

    if not complaints:
        await message.answer("📭 Жалоб нет")
        return

    for comp in complaints:
        await message.answer(
            "🚨 ЖАЛОБА\n\n"
            f"Нарушитель: {comp['nick']}\n"
            f"Суть: {comp['reason']}\n"
            f"Доказательства: {comp['proof']}",
            reply_markup=decision_buttons("comp", comp["from"])
        )

# ================= АНКЕТА =================
@dp.message(lambda m: m.text == "📝 Набор в модерацию")
async def app_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🎮 Ник на сервере:")
    await state.set_state(Application.nick)

@dp.message(Application.nick)
async def app_nick(message: types.Message, state: FSMContext):
    await state.update_data(nick=message.text)
    await message.answer("📱 Telegram:")
    await state.set_state(Application.tg)

@dp.message(Application.tg)
async def app_tg(message: types.Message, state: FSMContext):
    await state.update_data(tg=message.text)
    await message.answer("👤 Имя:")
    await state.set_state(Application.name)

@dp.message(Application.name)
async def app_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("🎂 Возраст:")
    await state.set_state(Application.age)

@dp.message(Application.age)
async def app_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("📄 О себе:")
    await state.set_state(Application.about)

@dp.message(Application.about)
async def app_about(message: types.Message, state: FSMContext):
    await state.update_data(about=message.text)
    await message.answer("🛡 Опыт:")
    await state.set_state(Application.exp)

@dp.message(Application.exp)
async def app_exp(message: types.Message, state: FSMContext):
    await state.update_data(exp=message.text)
    await message.answer("⏱ Время в день:")
    await state.set_state(Application.time)

@dp.message(Application.time)
async def app_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data["time"] = message.text
    applications[message.from_user.id] = data
    await message.answer("✅ Заявка отправлена")
    await state.clear()

# ================= ЖАЛОБА =================
@dp.message(lambda m: m.text == "🚨 Подать жалобу")
async def comp_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("👤 Ник нарушителя:")
    await state.set_state(Complaint.nick)

@dp.message(Complaint.nick)
async def comp_nick(message: types.Message, state: FSMContext):
    await state.update_data(nick=message.text)
    await message.answer("📄 Суть жалобы:")
    await state.set_state(Complaint.reason)

@dp.message(Complaint.reason)
async def comp_reason(message: types.Message, state: FSMContext):
    await state.update_data(reason=message.text)
    await message.answer("📎 Доказательства:")
    await state.set_state(Complaint.proof)

@dp.message(Complaint.proof)
async def comp_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data["proof"] = message.text
    data["from"] = message.from_user.id
    complaints.append(data)
    await message.answer("✅ Жалоба отправлена")
    await state.clear()

# ================= CALLBACK =================
@dp.callback_query(lambda c: c.data.startswith(("app_", "comp_")))
async def decision(callback: types.CallbackQuery):
    prefix, rest = callback.data.split("_")
    action, user_id = rest.split(":")
    user_id = int(user_id)

    if callback.from_user.id not in ADMINS and callback.from_user.id not in MODERS:
        await callback.answer("⛔ Нет прав", show_alert=True)
        return

    await bot.send_message(
        user_id,
        "✅ Обращение принято" if action == "accept" else "❌ Обращение отклонено"
    )

    await callback.message.edit_text(callback.message.text + "\n\n✔ Решение вынесено")
    await callback.answer("Готово")

# ================= ЗАПУСК =================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())
