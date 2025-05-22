import asyncio
from typing import Any, Dict, List, Optional, Sequence

from asgiref.sync import sync_to_async, async_to_sync

# Correct import path for BaseChatMemory
from langchain.memory.chat_memory import BaseChatMemory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from chat_app.models import ChatMessage # Ensure this import is correct

class DjangoChatMessageHistory(BaseChatMemory):
    session_id: str # <--- This line defines 'session_id' as a Pydantic field
    memory_key: str = "history" # Default memory key for agent history

    @property
    def memory_variables(self) -> List[str]:
        """Defines the input keys this memory expects, typically just the memory_key."""
        return [self.memory_key]

    @property
    def buffer(self) -> List[BaseMessage]:
        return self.load_memory_variables({})[self.memory_key]

    @property
    def buffer_as_messages(self) -> List[BaseMessage]:
        return self.buffer

    def __init__(self, session_id: str, **kwargs: Any):
        # Pass 'session_id' directly to the parent's constructor.
        # Pydantic (which BaseChatMemory uses) will now correctly validate and set it.
        super().__init__(session_id=session_id, **kwargs)
        # self.session_id is automatically set by Pydantic, no need to do it manually.

    # --- Shared Async Helper to Fetch Messages from Database ---
    async def _aget_messages_from_db(self) -> List[BaseMessage]:
        messages = []
        chat_messages = await sync_to_async(
            list,
            thread_sensitive=True # Important for Django ORM
        )(ChatMessage.objects.filter(session_id=self.session_id).order_by('timestamp'))

        for msg in chat_messages:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
        return messages

    # --- Synchronous Interface for LangChain Memory (load) ---
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, List[BaseMessage]]:
        messages = async_to_sync(self._aget_messages_from_db)()
        return {self.memory_key: messages}

    # --- Asynchronous Interface for LangChain Memory (aload) ---
    async def aload_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, List[BaseMessage]]:
        messages = await self._aget_messages_from_db()
        return {self.memory_key: messages}

    # --- Asynchronous Methods for Saving and Clearing Context ---
    async def asave_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        user_message_content = inputs.get("input")
        ai_message_content = outputs.get("output")

        if user_message_content:
            await sync_to_async(ChatMessage.objects.create)(
                session_id=self.session_id, role="user", content=user_message_content
            )
        if ai_message_content:
            await sync_to_async(ChatMessage.objects.create)(
                session_id=self.session_id, role="assistant", content=ai_message_content
            )

    async def aclear(self) -> None:
        await sync_to_async(ChatMessage.objects.filter(session_id=self.session_id).delete)()