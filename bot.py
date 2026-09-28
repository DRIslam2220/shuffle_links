import os
import random
import json
import firebase_admin
from firebase_admin import credentials, db
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

CONFIG_FILE = "firebase_config.json"
BOT_TOKEN_FILE = "bot_token.txt"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_bot_token():
    with open(BOT_TOKEN_FILE, "r", encoding="utf-8") as f:
        token = f.read().strip()
    if not token:
        raise RuntimeError("bot_token.txt is empty.")
    return token


config = load_config()
database_url = config["databaseURL"]
service_account_file = config.get("serviceAccountFile", "firebase-service-account.example.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_file)
    firebase_admin.initialize_app(cred, {"databaseURL": database_url})


def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔀 Shuffle Links", callback_data="shuffle")],
        [InlineKeyboardButton("📊 Status", callback_data="status")]
    ])


def get_root():
    value = db.reference("/").get()
    return value if isinstance(value, dict) else {}


def find_links():
    """
    Expected structure:
      key:
        link:
          link: "https://..."

    Any final value exactly equal to "link" is ignored.
    """
    root = get_root()
    result = []

    for key, value in root.items():
        if not isinstance(value, dict):
            continue

        link_object = value.get("link")
        if not isinstance(link_object, dict):
            continue

        link_value = link_object.get("link")
        if not isinstance(link_value, str):
            continue

        if link_value.strip().lower() == "link":
            continue

        result.append((key, link_value))

    return result


def shuffle_links():
    items = find_links()

    if len(items) < 2:
        return len(items), False

    keys = [x[0] for x in items]
    links = [x[1] for x in items]
    original = links[:]

    # Try to make the result different from the current arrangement.
    for _ in range(20):
        random.shuffle(links)
        if links != original:
            break

    updates = {
        f"/{key}/link/link": link
        for key, link in zip(keys, links)
    }

    db.reference("/").update(updates)
    return len(items), True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome!\n\n"
        "Use the buttons below to manage the Firebase links.\n\n"
        "🔀 Shuffle Links: randomly exchanges the existing links.\n"
        "📊 Status: shows how many links can be shuffled.",
        reply_markup=menu()
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "status":
        try:
            items = find_links()
            root = get_root()
            excluded = 0

            for key, value in root.items():
                if not isinstance(value, dict):
                    continue
                obj = value.get("link")
                if isinstance(obj, dict) and obj.get("link") == "link":
                    excluded += 1

            await query.edit_message_text(
                "📊 Firebase Status\n\n"
                f"🔗 Shuffleable links: {len(items)}\n"
                f"🚫 Excluded links: {excluded}",
                reply_markup=menu()
            )
        except Exception as e:
            print(repr(e))
            await query.edit_message_text(
                "❌ Failed to read Firebase.",
                reply_markup=menu()
            )
        return

    if query.data == "shuffle":
        await query.edit_message_text("🔄 Shuffling links...")

        try:
            count, changed = shuffle_links()

            if count < 2:
                message = (
                    "⚠️ Not enough links to shuffle.\n\n"
                    f"Found: {count}"
                )
            elif changed:
                message = (
                    "✅ Shuffle completed successfully!\n\n"
                    f"🔗 Links shuffled: {count}\n"
                    "🚫 Values equal to \"link\" were excluded."
                )
            else:
                message = "⚠️ The links could not be rearranged."

            await query.edit_message_text(message, reply_markup=menu())

        except Exception as e:
            print("Firebase error:", repr(e))
            await query.edit_message_text(
                "❌ Firebase update failed.\n\n"
                "Please check your Firebase service-account credentials "
                "and Realtime Database permissions.",
                reply_markup=menu()
            )


def main():
    token = load_bot_token()

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
