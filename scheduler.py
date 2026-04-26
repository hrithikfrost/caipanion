import asyncio
import logging
from datetime import datetime, timedelta

from telegram import Bot

from app.agent import CompanionAgent
from app.memory import MemoryStore


logger = logging.getLogger(__name__)


class MorningScheduler:
    """Sends one AI-generated morning message per day to every known chat."""

    def __init__(
        self,
        bot: Bot,
        agent: CompanionAgent,
        memory: MemoryStore,
        morning_hour: int,
        morning_minute: int,
    ) -> None:
        self.bot = bot
        self.agent = agent
        self.memory = memory
        self.morning_hour = morning_hour
        self.morning_minute = morning_minute
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is None:
            return

        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None

    async def _run(self) -> None:
        while True:
            await asyncio.sleep(self._seconds_until_next_run())
            await self._send_morning_messages()

    def _seconds_until_next_run(self) -> float:
        now = datetime.now()
        next_run = now.replace(
            hour=self.morning_hour,
            minute=self.morning_minute,
            second=0,
            microsecond=0,
        )
        if next_run <= now:
            next_run += timedelta(days=1)
        return (next_run - now).total_seconds()

    async def _send_morning_messages(self) -> None:
        for chat_id in self.memory.get_known_chat_ids():
            try:
                text = await self.agent.generate_morning_message(chat_id)
                self.memory.add_message(chat_id, "assistant", text)
                await self.bot.send_message(chat_id=chat_id, text=text)
            except Exception:
                logger.exception("Failed to send morning message to chat %s", chat_id)
