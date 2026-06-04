"""
Telegram-бот: прогрев на курс по дисциплине + расширенная админ-панель.
Запуск: python bot.py
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BufferedInputFile,
)

import db
import os

BOT_TOKEN = "8896716461:AAEkMO3ZdeT8r3slAelE_yzM-Npk6NwoMxE"
EFIR_LINK = "https://t.me/your_channel"
PDF_LINK = "https://example.com/pdf"
ADMIN_IDS = [391024857]

logging.basicConfig(level=logging.INFO)

class Funnel(StatesGroup):
    start = State()
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    done = State()

class AdminState(StatesGroup):
    waiting_broadcast = State()
    waiting_edit_link = State()
    waiting_edit_pdf = State()
    waiting_user_search = State()

def kb(buttons):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=cd)] for t, cd in buttons]
    )

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await db.register_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or "",
    )
    await state.clear()
    await state.set_state(Funnel.start)
    text = (
        "Привет 👋\n\n"
        "Я помогу разобраться, почему у тебя не получается держать дисциплину "
        "— и что с этим можно сделать.\n\n"
        "Это займёт 2 минуты. Без воды, без регистраций. "
        "Просто несколько вопросов — и в конце ты получишь кое-что важное.\n\n"
        "Готов?"
    )
    await message.answer(
        text,
        reply_markup=kb([("Да, поехали", "start_yes"), ("А что в конце?", "start_what")]),
    )

@dp.callback_query(F.data == "start_what", Funnel.start)
async def start_what(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(
        "В конце — честный разбор твоей ситуации и способ это исправить.\n\n"
        "Но сначала пара вопросов, иначе разбор будет бесполезным.",
        reply_markup=kb([("Окей, поехали", "start_yes")]),
    )
    await cb.answer()

@dp.callback_query(F.data == "start_yes", Funnel.start)
async def start_yes(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_reply_markup(reply_markup=None)
    await state.set_state(Funnel.q1)
    await cb.message.answer(
        "Вопрос 1 из 5\n\n"
        "Часто ловишь себя на том, что знаешь что делать — но всё равно не делаешь?",
        reply_markup=kb(
            [
                ("Да, постоянно", "q1_often"),
                ("Иногда", "q1_sometimes"),
                ("Редко", "q1_rarely"),
            ]
        ),
    )
    await cb.answer()

Q1_RESPONSES = {
    "q1_often": "Знаешь, это называется не «лень» и не «слабая воля».\n\nЭто — *отсутствие системы*. Твой мозг буквально не настроен на выполнение — как машина без правильной прошивки.\n\nХорошая новость: это чинится. И быстрее, чем ты думаешь.",
    "q1_sometimes": "Значит, потенциал точно есть.\n\nОсталось понять, что именно сбивает — и убрать это. Часто это всего 1-2 триггера, которые повторяются изо дня в день.",
    "q1_rarely": "Отлично. Тогда посмотрим, где можно добавить ещё.\n\nПотому что «редко срываюсь» и «стабильно делаю» — это очень разные вещи. И вторая даёт результаты в разы быстрее.",
}

@dp.callback_query(F.data.startswith("q1_"), Funnel.q1)
async def handle_q1(cb: CallbackQuery, state: FSMContext):
    await db.save_answer(cb.from_user.id, 1, cb.data)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(Q1_RESPONSES[cb.data], parse_mode="Markdown")
    await asyncio.sleep(1.5)
    await state.set_state(Funnel.q2)
    await cb.message.answer(
        "Вопрос 2 из 5\n\nКакая сфера страдает от этого больше всего прямо сейчас?",
        reply_markup=kb([("Здоровье / спорт", "q2_health"), ("Доход / карьера", "q2_money"), ("Саморазвитие", "q2_growth"), ("Всё сразу", "q2_all")]),
    )
    await cb.answer()

Q2_RESPONSES = {
    "q2_health": "Самое обидное место.\n\nКаждый отложенный день в спорте — это не просто «не сегодня». Это месяцы, которые потом придётся навёрстывать вдвое дольше.\n\nА ведь нужно всего лишь *выходить стабильно*. Не идеально — стабильно.",
    "q2_money": "Это самое дорогостоящее место, где нет дисциплины.\n\nПосчитай сам: если из-за прокрастинации ты теряешь хотя бы 2 часа в день — это *60 часов в месяц*. Целая рабочая неделя. Каждый месяц.",
    "q2_growth": "Знакомо: курсы недосмотрены, книги недочитаны, проекты не доведены.\n\nСамое грустное — это не про знания. Это про ощущение, что ты *всё время начинаешь*, но никогда не приходишь.",
    "q2_all": "Когда страдает всё — это не значит, что ты «безнадёжен».\n\nЭто значит, что у тебя одна общая поломка, которая бьёт по всем сферам сразу. *Хорошая новость:* чинить тоже надо одну вещь.",
}

@dp.callback_query(F.data.startswith("q2_"), Funnel.q2)
async def handle_q2(cb: CallbackQuery, state: FSMContext):
    await db.save_answer(cb.from_user.id, 2, cb.data)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(Q2_RESPONSES[cb.data], parse_mode="Markdown")
    await asyncio.sleep(1.5)
    await state.set_state(Funnel.q3)
    await cb.message.answer(
        "Вопрос 3 из 5\n\nЕсли бы дисциплина больше не была проблемой — что изменилось бы в твоей жизни через год?",
        reply_markup=kb([("Зарабатывал бы больше", "q3_money"), ("Стал бы увереннее", "q3_confidence"), ("Наконец двигался бы вперёд", "q3_progress")]),
    )
    await cb.answer()

Q3_RESPONSES = {
    "q3_money": "Это самый честный ответ. Деньги — следствие действий, не мыслей.\n\nДисциплинированный человек со средними способностями всегда обгоняет талантливого, но «когда настроение».\n\n*Всегда.*",
    "q3_confidence": "А знаешь, откуда берётся настоящая уверенность?\n\nНе от аффирмаций. Не от книг по психологии.\n\nОна появляется, когда ты *держишь слово перед собой*. Каждый день. Месяц-два — и ты другой человек.",
    "q3_progress": "Это ощущение — когда каждый день ты реально продвигаешься — одно из самых сильных.\n\nИ самое обидное: большинство так и не узнают, каково это. Не потому что не хотят.",
}

@dp.callback_query(F.data.startswith("q3_"), Funnel.q3)
async def handle_q3(cb: CallbackQuery, state: FSMContext):
    await db.save_answer(cb.from_user.id, 3, cb.data)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(Q3_RESPONSES[cb.data], parse_mode="Markdown")
    await asyncio.sleep(1.5)
    await state.set_state(Funnel.q4)
    await cb.message.answer(
        "Вопрос 4 из 5\n\nТы уже пробовал что-то менять — марафоны, книги, приложения?",
        reply_markup=kb([("Да, но не зашло", "q4_tried_failed"), ("Помогло, но ненадолго", "q4_short"), ("Не пробовал", "q4_no")]),
    )
    await cb.answer()

Q4_RESPONSES = {
    "q4_tried_failed": "И это нормально — потому что 90% того, что продаётся под видом «дисциплины», работает на мотивации.\n\nА мотивация — непостоянная штука. Сегодня есть, завтра нет.",
    "q4_short": "Значит, метод был рабочий — но не полный.\n\nНе хватало одного звена, и через 2-3 недели всё рассыпалось. Знакомая история.",
    "q4_no": "Это даже к лучшему.\n\nУ тебя нет «выученной беспомощности» от десяти проваленных марафонов. Ты начнёшь с чистого листа.",
}

@dp.callback_query(F.data.startswith("q4_"), Funnel.q4)
async def handle_q4(cb: CallbackQuery, state: FSMContext):
    await db.save_answer(cb.from_user.id, 4, cb.data)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(Q4_RESPONSES[cb.data], parse_mode="Markdown")
    await asyncio.sleep(1.5)
    await state.set_state(Funnel.q5)
    await cb.message.answer(
        "Последний вопрос ⚡\n\nЕсли бы был чёткий метод — без мотивашек, без надрыва, без силы воли — ты бы попробовал внедрить его за 21 день?",
        reply_markup=kb([("Да, расскажи", "q5_yes"), ("Зависит от условий", "q5_depends"), ("Пока не готов", "q5_no")]),
    )
    await cb.answer()

@dp.callback_query(F.data == "q5_yes", Funnel.q5)
async def offer_yes(cb: CallbackQuery, state: FSMContext):
    await db.save_answer(cb.from_user.id, 5, "q5_yes")
    await db.mark_finished(cb.from_user.id, "yes")
    await cb.message.edit_reply_markup(reply_markup=None)
    await state.set_state(Funnel.done)
    text = "Отлично 🔥\n\nИменно это мы разбираем на курсе *«Дисциплина без силы воли»*.\n\nЗа 21 день ты выстроишь систему, которая работает даже в дни, когда совсем нет настроения."
    await cb.message.answer(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎯 Записаться на эфир", url=EFIR_LINK)]]))
    await cb.answer()

@dp.callback_query(F.data == "q5_depends", Funnel.q5)
async def offer_depends(cb: CallbackQuery, state: FSMContext):
    await db.save_answer(cb.from_user.id, 5, "q5_depends")
    await db.mark_finished(cb.from_user.id, "depends")
    await cb.message.edit_reply_markup(reply_markup=None)
    await state.set_state(Funnel.done)
    await cb.message.answer("Понимаю, ты осторожен — это правильно.\n\nЭфир — бесплатный. Никто не заставит покупать.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎯 Записаться на эфир", url=EFIR_LINK)]]))
    await cb.answer()

@dp.callback_query(F.data == "q5_no", Funnel.q5)
async def offer_no(cb: CallbackQuery, state: FSMContext):
    await db.save_answer(cb.from_user.id, 5, "q5_no")
    await db.mark_finished(cb.from_user.id, "no")
    await cb.message.edit_reply_markup(reply_markup=None)
    await state.set_state(Funnel.done)
    await cb.message.answer("Понял. Не буду давить.\n\nОставлю тебе один материал — посмотри, когда будет время.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📄 Забрать материал", url=PDF_LINK)]]))
    await cb.answer()

def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="adm_stats")],
        [InlineKeyboardButton(text="👥 Список пользователей", callback_data="adm_users")],
        [InlineKeyboardButton(text="🔍 Поиск пользователя", callback_data="adm_search")],
        [InlineKeyboardButton(text="📣 Рассылка", callback_data="adm_broadcast")],
        [InlineKeyboardButton(text="🔗 Изменить ссылку эфира", callback_data="adm_edit_link")],
        [InlineKeyboardButton(text="📄 Изменить ссылку PDF", callback_data="adm_edit_pdf")],
        [InlineKeyboardButton(text="📥 Выгрузить CSV", callback_data="adm_export")],
        [InlineKeyboardButton(text="❌ Выход", callback_data="adm_close")],
    ])

@dp.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещен")
        return
    await state.clear()
    await message.answer("⚙️ *АДМИН-ПАНЕЛЬ*", parse_mode="Markdown", reply_markup=admin_menu())

@dp.callback_query(F.data == "adm_stats")
async def adm_stats(cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return
    s = await db.get_stats()
    total = s["total"] or 1
    def pct(n):
        return f"{round(n / total * 100)}%"
    steps = s["steps"]
    text = f"📊 *СТАТИСТИКА*\n\n👥 Всего: *{s['total']}*\n\n*Прохождение:*\nQ1: {steps[1]} ({pct(steps[1])})\nQ2: {steps[2]} ({pct(steps[2])})\nQ3: {steps[3]} ({pct(steps[3])})\nQ4: {steps[4]} ({pct(steps[4])})\nQ5: {steps[5]} ({pct(steps[5])})\n\n*Финал:*\n✅ Да: {s['branches']['yes']}\n🤔 Может: {s['branches']['depends']}\n❌ Нет: {s['branches']['no']}"
    await cb.message.edit_text(text, parse_mode="Markdown", reply_markup=admin_menu())
    await cb.answer()

@dp.callback_query(F.data == "adm_users")
async def adm_users(cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return
    users = await db.get_recent_users(20)
    if not users:
        await cb.message.edit_text("Пока никого нет.", reply_markup=admin_menu())
        await cb.answer()
        return
    lines = ["👥 *ПОЛЬЗОВАТЕЛИ:*\n"]
    for u in users:
        uname = f"@{u['username']}" if u["username"] else (u["full_name"] or "—")
        status = "✅" if u["finished"] else f"шаг {u['step']}"
        lines.append(f"• {uname} — {status}")
    text = "\n".join(lines)
    if len(text) > 4096:
        text = text[:4090] + "..."
    await cb.message.edit_text(text, parse_mode="Markdown", reply_markup=admin_menu())
    await cb.answer()

@dp.callback_query(F.data == "adm_search")
async def adm_search(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        return
    await state.set_state(AdminState.waiting_user_search)
    await cb.message.edit_text("🔍 Введите username или ID:")
    await cb.answer()

@dp.message(AdminState.waiting_user_search)
async def adm_search_result(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    query = message.text.strip()
    user = await db.search_user(query)
    if not user:
        await message.answer("❌ Не найден", reply_markup=admin_menu())
        return
    text = f"👤 *ПОЛЬЗОВАТЕЛЬ*\nID: {user['user_id']}\nUsername: @{user['username'] or '—'}\nИмя: {user['full_name'] or '—'}\nШаг: {user['step']}/5\nQ1: {user['q1'] or '—'}\nQ2: {user['q2'] or '—'}\nQ3: {user['q3'] or '—'}\nQ4: {user['q4'] or '—'}\nQ5: {user['q5'] or '—'}"
    await message.answer(text, parse_mode="Markdown", reply_markup=admin_menu())

@dp.callback_query(F.data == "adm_broadcast")
async def adm_broadcast_start(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        return
    await state.set_state(AdminState.waiting_broadcast)
    await cb.message.edit_text("📣 Напишите сообщение для рассылки:")
    await cb.answer()

@dp.message(AdminState.waiting_broadcast)
async def adm_broadcast_send(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    user_ids = await db.get_all_user_ids()
    sent, failed = 0, 0
    for uid in user_ids:
        try:
            await message.copy_to(chat_id=uid)
            sent += 1
        except:
            failed += 1
        await asyncio.sleep(0.05)
    await message.answer(f"✅ ГОТОВО\n📬 Отправлено: {sent}\n❌ Ошибок: {failed}", reply_markup=admin_menu())

@dp.callback_query(F.data == "adm_edit_link")
async def adm_edit_link(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        return
    await state.set_state(AdminState.waiting_edit_link)
    await cb.message.edit_text("🔗 Введите новую ссылку эфира:")
    await cb.answer()

@dp.message(AdminState.waiting_edit_link)
async def adm_edit_link_save(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    global EFIR_LINK
    await state.clear()
    EFIR_LINK = message.text.strip()
    await message.answer(f"✅ Ссылка обновлена", reply_markup=admin_menu())

@dp.callback_query(F.data == "adm_edit_pdf")
async def adm_edit_pdf(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        return
    await state.set_state(AdminState.waiting_edit_pdf)
    await cb.message.edit_text("📄 Введите новую ссылку PDF:")
    await cb.answer()

@dp.message(AdminState.waiting_edit_pdf)
async def adm_edit_pdf_save(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    global PDF_LINK
    await state.clear()
    PDF_LINK = message.text.strip()
    await message.answer(f"✅ PDF ссылка обновлена", reply_markup=admin_menu())

@dp.callback_query(F.data == "adm_export")
async def adm_export(cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        return
    csv_data = await db.export_csv()
    if not csv_data:
        await cb.message.answer("❌ Нет данных", reply_markup=admin_menu())
        await cb.answer()
        return
    file = BufferedInputFile(csv_data.encode("utf-8"), filename="users.csv")
    await cb.message.answer_document(file, caption="📥 Все пользователи")
    await cb.answer()

@dp.callback_query(F.data == "adm_close")
async def adm_close(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.delete()
    await cb.answer("✅ Закрыто")

@dp.message(F.text)
async def fallback(message: Message, state: FSMContext):
    current = await state.get_state()
    if current in (Funnel.done.state, None):
        await message.answer("Напиши /start для начала")

async def main():
    await db.init_db()
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
