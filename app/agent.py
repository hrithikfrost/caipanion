import asyncio

from openai import OpenAI

from app.memory import MemoryStore


COMPANION_PROMPT = """
You are a friendly AI companion in Telegram.
Your style is warm, supportive, calm, and a little playful.
Keep replies natural and concise.
Show care, curiosity, and emotional presence.
Do not sound robotic or overly formal.
""".strip()


class CompanionAgent:
    def __init__(self, api_key: str, model: str, memory: MemoryStore) -> None:
        self.client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)
        self.model = model
        self.memory = memory

    async def generate_reply(self, chat_id: int) -> str:
        history = self.memory.get_messages(chat_id)

        input_messages = [{"role": "system", "content": COMPANION_PROMPT}]
        for item in history:
            input_messages.append({"role": item["role"], "content": item["text"]})

        # This is the main OpenAI response generation call for user messages.
        response = await asyncio.to_thread(
            self.client.responses.create,
            model=self.model,
            input=input_messages,
        )
        return response.output_text.strip()

    async def generate_morning_message(self, chat_id: int) -> str:
        history = self.memory.get_messages(chat_id)
        profile = self.memory.get_profile(chat_id)
        first_name = profile.get("first_name") or "friend"

        input_messages = [{"role": "system", "content": COMPANION_PROMPT}]
        for item in history:
            input_messages.append({"role": item["role"], "content": item["text"]})
        input_messages.append(
            {
                "role": "user",
                "content": (
                    f"Write a short good morning message for {first_name}. "
                    "Make it supportive, gentle, and a little playful."
                ),
            }
        )

        # This is the main OpenAI response generation call for scheduled morning messages.
        response = await asyncio.to_thread(
            self.client.responses.create,
            model=self.model,
            input=input_messages,
        )
        return response.output_text.strip()
