# Telegram AI Companion MVP

Minimal Telegram bot in Python with:

- Telegram message handling
- OpenAI-generated replies
- Simple file-based memory
- Daily morning messages

## Project structure

- `main.py` - entry point
- `app/telegram_handler.py` - Telegram bot handlers
- `app/agent.py` - AI companion logic and OpenAI calls
- `app/memory.py` - simple JSON memory
- `app/scheduler.py` - daily morning message scheduler
- `app/config.py` - environment configuration

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in:

- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `OPENAI_MODEL` (optional)
- `MORNING_HOUR` (optional)
- `MORNING_MINUTE` (optional)

## Run

```bash
python main.py
```

## Where the reply is generated

The main reply generation happens in `app/agent.py` inside:

- `CompanionAgent.generate_reply(...)`
- `CompanionAgent.generate_morning_message(...)`

Both methods call `self.client.responses.create(...)`.

## Notes

- Memory is stored in `data/memory.json`.
- The bot sends morning messages only to chats that already wrote to the bot or used `/start`.
- This is a minimal MVP version without database, auth, admin panel, or media features.
