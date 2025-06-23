from config import API_TOKEN
import telebot
import sqlite3
import threading
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

bot = telebot.TeleBot(token=API_TOKEN)

conn = sqlite3.connect("tagit.db", check_same_thread=False)
cursor = conn.cursor()
db_lock = threading.Lock()

user_data = {}  # uid: {"tags": [], "state": "idle", "link": ""}
user_states = {}  # uid: {"state": ..., "old_tag": ...}

@bot.message_handler(commands=['help'])
def help_message(message):
    help_text = (
        "🤖 *Welcome to TagIt Bot!* Here's how to use the bot:\n\n"
        "🆕 /start\n"
        "Start using the bot and register your info.\n\n"
        "➕ *Add Tags*\n"
        "Click the button to start adding tags (used to organize your links).\n\n"
        "/add\n"
        "Send a link with a title like this:\n"
        "Then choose the tag you want to save it under.\n\n"
        "/show\n"
        "View all your tags and browse saved links.\n\n"
        "/update\n"
        "Update your saved data:\n"
        "📝 Rename a tag\n"
        "❌ Delete a tag\n"
        "🗑️ Delete a specific link\n\n"
        "/done\n"
        "Use this after adding tags to finish.\n\n"
        "/help\n"
        "Show this guide again.\n"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def welcome(message):
    cid = message.chat.id
    with db_lock:
        cursor.execute("INSERT OR IGNORE INTO users (id, username, first_name) VALUES (?, ?, ?)",
                       (cid, message.from_user.username, message.from_user.first_name))
        conn.commit()
        cursor.execute("SELECT tag FROM tags WHERE user_id = ?", (cid,))
        tags = [row[0] for row in cursor.fetchall()]

    user_data[cid] = {"state": "idle", "tags": tags, "link": ""}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("➕ Add Tags"))
    bot.send_message(cid, f"Hi {message.from_user.first_name}, welcome to TagIt! 👋\nPlease add your tags 👇", reply_markup=markup)

@bot.message_handler(commands=['update'])
def update_options(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📝 Rename Tag", callback_data="rename_tag"),
        InlineKeyboardButton("❌ Delete Tag", callback_data="delete_tag"),
        InlineKeyboardButton("🗑️ Delete Link", callback_data="delete_link")
    )
    bot.send_message(message.chat.id, "Choose what you want to update:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "rename_tag")
def rename_tag_start(call):
    uid = call.from_user.id
    with db_lock:
        cursor.execute("SELECT tag FROM tags WHERE user_id = ?", (uid,))
        tags = [row[0] for row in cursor.fetchall()]
    if not tags:
        bot.send_message(call.message.chat.id, "⚠️ You have no tags to rename.")
        return
    markup = InlineKeyboardMarkup(row_width=2)
    for tag in tags:
        markup.add(InlineKeyboardButton(text=tag, callback_data=f"rename_tag_select_{tag}"))
    bot.send_message(call.message.chat.id, "Select a tag to rename:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("rename_tag_select_"))
def ask_new_tag_name(call):
    uid = call.from_user.id
    old_tag = call.data.replace("rename_tag_select_", "")
    user_states[uid] = {"state": "awaiting_new_tag_name", "old_tag": old_tag}
    bot.send_message(call.message.chat.id, f"Type the new name for tag '{old_tag}':")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("state") == "awaiting_new_tag_name")
def do_rename_tag(message):
    uid = message.from_user.id
    cid = message.chat.id
    old_tag = user_states[uid]["old_tag"]
    new_tag = message.text.strip()
    with db_lock:
        cursor.execute("UPDATE tags SET tag = ? WHERE user_id = ? AND tag = ?", (new_tag, uid, old_tag))
        cursor.execute("UPDATE links SET tag = ? WHERE user_id = ? AND tag = ?", (new_tag, uid, old_tag))
        conn.commit()
    if old_tag in user_data.get(uid, {}).get("tags", []):
        user_data[uid]["tags"].remove(old_tag)
        user_data[uid]["tags"].append(new_tag)
    user_states[uid] = {"state": "idle"}
    bot.send_message(cid, f"✅ Tag '{old_tag}' renamed to '{new_tag}'.")

@bot.message_handler(func=lambda m: m.text == "➕ Add Tags")
def ask_for_tag(message):
    cid = message.chat.id
    user_data.setdefault(cid, {"tags": [], "state": "idle", "link": ""})
    user_data[cid]["state"] = "adding_tag"
    bot.send_message(cid, "✏️ Please type the name of the tag you want to add:")

@bot.message_handler(commands=['done'])
def finish_adding_tags(message):
    cid = message.chat.id
    if cid in user_data:
        user_data[cid]["state"] = "idle"
        tags = user_data[cid]["tags"]
        if tags:
            tag_list = ', '.join(tags)
            bot.send_message(cid, f"Done! These are your tags: {tag_list} 🎉")
        else:
            bot.send_message(cid, "You haven't added any tags yet. ⚠️")
    else:
        bot.send_message(cid, "Please use /start first. ❗")

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("state") == "adding_tag")
def save_tag(message):
    cid = message.chat.id
    tag = message.text.strip()
    with db_lock:
        cursor.execute("INSERT OR IGNORE INTO tags (user_id, tag) VALUES (?, ?)", (cid, tag))
        conn.commit()
    if tag not in user_data[cid]["tags"]:
        user_data[cid]["tags"].append(tag)
        bot.send_message(cid, f"Tag '{tag}' added. ✅")
    else:
        bot.send_message(cid, f"Tag '{tag}' already exists. ⚠️")
    bot.send_message(cid, "Type another tag or send /done if you're finished.")

@bot.message_handler(commands=['show'])
def show_tags(message):
    uid = message.from_user.id
    with db_lock:
        cursor.execute("SELECT tag FROM tags WHERE user_id = ?", (uid,))
        tags = [row[0] for row in cursor.fetchall()]
    if not tags:
        bot.send_message(message.chat.id, "⚠️ You don't have any tags yet.")
        return
    markup = InlineKeyboardMarkup(row_width=2)
    for tag in tags:
        markup.add(InlineKeyboardButton(text=tag, callback_data=f"show_links_{tag}"))
    bot.send_message(message.chat.id, "📂 Choose a tag to view its links:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("show_links_"))
def show_links(call):
    uid = call.from_user.id
    tag = call.data.replace("show_links_", "")
    with db_lock:
        cursor.execute("SELECT link FROM links WHERE user_id = ? AND tag = ?", (uid, tag))
        links = [row[0] for row in cursor.fetchall()]
    if not links:
        bot.send_message(call.message.chat.id, f"⚠️ No links found under the tag '{tag}'.")
        return
    response = f"🔗 Links under tag '{tag}':\n\n" + "\n".join(links)
    bot.send_message(call.message.chat.id, response)

@bot.message_handler(commands=['add'])
def add_link(message):
    uid = message.from_user.id
    user_states[uid] = {"state": "waiting_for_link"}
    bot.send_message(message.chat.id, "Please send the link you want to save.")

@bot.message_handler(func=lambda m: m.text and not m.text.startswith('/') and m.content_type == 'text')
def handle_text(message):
    uid = message.from_user.id
    if user_states.get(uid, {}).get("state") == 'waiting_for_link':
        link = message.text.strip()
        if link.startswith("http://") or link.startswith("https://"):
            user_data.setdefault(uid, {"tags": [], "state": "idle", "link": ""})
            user_data[uid]["link"] = link
            with db_lock:
                cursor.execute("SELECT tag FROM tags WHERE user_id = ?", (uid,))
                tags = [row[0] for row in cursor.fetchall()]
            markup = InlineKeyboardMarkup(row_width=2)
            for tag in tags:
                markup.add(InlineKeyboardButton(text=tag, callback_data=f"tag_{tag}"))
            markup.add(InlineKeyboardButton(text="➕ Add New Tag", callback_data="add_new_tag"))
            bot.send_message(message.chat.id, "The link has been successfully received ✅, Now choose a tag for it:", reply_markup=markup)
            user_states[uid] = {"state": "waiting_for_tag"}
        else:
            bot.send_message(message.chat.id, "Invalid link ❌\nClick /add to try again.")
            user_states[uid] = {"state": "idle"}
    else:
        bot.send_message(message.chat.id, "I didn’t understand that. Use /add to add a link ❗")

@bot.callback_query_handler(func=lambda call: call.data.startswith("tag_") or call.data == "add_new_tag")
def handle_tag_choice(call):
    cid = call.message.chat.id
    uid = call.from_user.id
    if call.data == "add_new_tag":
        user_states[uid] = {"state": "waiting_for_new_tag"}
        bot.send_message(cid, "✏️ Type your new tag:")
    else:
        tag = call.data.replace("tag_", "")
        link = user_data.get(uid, {}).get("link")
        if link:
            with db_lock:
                cursor.execute("INSERT INTO links (user_id, link, tag) VALUES (?, ?, ?)", (uid, link, tag))
                conn.commit()
        bot.send_message(cid, f"✅ Link tagged with '{tag}'!")
        bot.send_message(cid, "Want to add another link? Click /add !")
        user_states[uid] = {"state": "idle"}

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get("state") == "waiting_for_new_tag")
def handle_new_tag(message):
    uid = message.from_user.id
    cid = message.chat.id
    new_tag = message.text.strip()
    with db_lock:
        cursor.execute("INSERT OR IGNORE INTO tags (user_id, tag) VALUES (?, ?)", (uid, new_tag))
        conn.commit()
    user_data.setdefault(uid, {"tags": [], "state": "idle", "link": ""})
    if new_tag not in user_data[uid]["tags"]:
        user_data[uid]["tags"].append(new_tag)
        bot.send_message(cid, f"✅ Tag '{new_tag}' added and linked!")
    else:
        bot.send_message(cid, f"⚠️ Tag '{new_tag}' already exists. Linking it now.")
    link = user_data[uid].get("link")
    if link:
        with db_lock:
            cursor.execute("INSERT INTO links (user_id, link, tag) VALUES (?, ?, ?)", (uid, link, new_tag))
            conn.commit()
    bot.send_message(cid, "Want to add another link? Click /add !")
    user_states[uid] = {"state": "idle"}

bot.polling()