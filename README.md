# Telegram Firebase Shuffle Bot

## What it does

This Telegram bot is connected to Firebase Realtime Database.

When any Telegram user presses:

**🔀 Shuffle Links**

the bot randomly exchanges the existing links between the Firebase entries.

Entries whose final value is exactly:

```text
link
```

are excluded and are not changed.

The bot is NOT restricted to a specific Telegram user. Anyone can use it with the bot.

---

## Files

Put these files in the same folder:

```text
bot.py
requirements.txt
bot_token.txt
firebase_config.json
firebase-service-account.json
```

### 1. bot_token.txt

Put your Telegram BotFather token in this file:

```text
123456789:YOUR_BOT_TOKEN
```

Do not put anything else in this file.

### 2. firebase_config.json

This file contains the Firebase connection configuration.

The included example is already configured for the supplied Firebase project.

### 3. firebase-service-account.json

Create/download a Firebase service-account JSON file and place it in the same folder.

IMPORTANT:
This is a private credential. Do not publish it on GitHub or send it to other people.

---

## Install

Install Python 3.10+.

Then open a terminal in this folder:

```bash
pip install -r requirements.txt
```

Run:

```bash
python bot.py
```

You should see:

```text
Bot is running...
```

Then open your Telegram bot and send:

```text
/start
```

---

## Firebase structure

The bot expects entries similar to:

```text
shr1
  link
    link: "https://example.com/..."

shr2
  link
    link: "https://example2.com/..."

shr22
  link
    link: "link"
```

`shr22` will be excluded because its value is exactly `link`.

---

## Security

Do NOT expose:

- bot_token.txt
- firebase-service-account.json

Anyone who gets the Telegram bot token can control the bot.
Anyone who gets the Firebase service-account credentials may be able to access your Firebase project according to the service-account permissions.
