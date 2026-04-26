import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from app.agent import CompanionAgent
from app.config import get_settings
from app.memory import MemoryStore
from app.scheduler import MorningScheduler


logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None or update.effective_user is None or update.message is None:
        return

    memory: MemoryStore = context.application.bot_data["memory"]
    memory.remember_user(
        chat_id=update.effective_chat.id,
        username=update.effective_user.username,
        first_name=update.effective_user.first_name,
    )

    await update.message.reply_text(
        "Hi! I am your AI companion. Write to me anytime, and I will reply."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None or update.effective_user is None or update.message is None:
        return

    user_text = (update.message.text or "").strip()
    if not user_text:
        return

    memory: MemoryStore = context.application.bot_data["memory"]
    agent: CompanionAgent = context.application.bot_data["agent"]

    memory.remember_user(
        chat_id=update.effective_chat.id,
        username=update.effective_user.username,
        first_name=update.effective_user.first_name,
    )
    memory.add_message(update.effective_chat.id, "user", user_text)

    try:
        reply_text = await agent.generate_reply(update.effective_chat.id)
    except Exception:
        logger.exception("Failed to generate reply for chat %s", update.effective_chat.id)
        reply_text = "I hit a temporary problem while thinking. Please try again in a moment."

    memory.add_message(update.effective_chat.id, "assistant", reply_text)

    await update.message.reply_text(reply_text)


async def on_startup(application: Application) -> None:
    scheduler: MorningScheduler = application.bot_data["scheduler"]
    scheduler.start()


async def on_shutdown(application: Application) -> None:
    scheduler: MorningScheduler = application.bot_data["scheduler"]
    await scheduler.stop()


def run_bot() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    settings = get_settings()
    memory = MemoryStore(settings.memory_file)
    agent = CompanionAgent(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        memory=memory,
    )

    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )
    scheduler = MorningScheduler(
        bot=application.bot,
        agent=agent,
        memory=memory,
        morning_hour=settings.morning_hour,
        morning_minute=settings.morning_minute,
    )

    application.bot_data["memory"] = memory
    application.bot_data["agent"] = agent
    application.bot_data["scheduler"] = scheduler

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()
