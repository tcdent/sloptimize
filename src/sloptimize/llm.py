from typing import Optional, TypeVar, Type
from pydantic import BaseModel
from openai import OpenAI
from xai_sdk import Client
from xai_sdk.chat import system, user, assistant
import time
import logging
from pydantic_core import ValidationError
from .environment import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    XAI_API_KEY,
    GROK_MODEL,
)

T = TypeVar("T", bound=BaseModel)

"""
LLM client configuration for OpenAI and Grok

STRUCTURED OUTPUTS COMPATIBILITY:
- OpenAI: Supports structured outputs via client.responses.create() on gpt-4o-2024-08-06 and later
- xAI Grok: Supports structured outputs on all models later than grok-2-1212 (including Grok 4)
- Both use the same OpenAI-compatible API contract with Pydantic BaseModel in response_format

API INVESTIGATION FINDINGS:
- OpenAI: responses.create() takes 'input' and 'instructions' parameters, NOT 'messages'
- xAI: Native xAI SDK provides cleaner API with chat.create() + chat.parse(Pydantic)
- xAI SDK example: chat.append(system("...")) + chat.append(user("...")) + chat.parse(Model)
- xAI parse() returns tuple: (response, parsed_pydantic_object)

IMPLEMENTATION STRATEGY:
- LLMClient: Uses OpenAI responses API for OpenAI models
- GrokClient: Uses native xAI SDK for Grok models
- Both expose same __call__ interface for consistency
- TypeVar T ensures type safety - returns the exact Pydantic model type passed in
"""


class LLMClient:
    """Wrapper for OpenAI LLM interactions.

    This class provides a convenient interface for interacting with OpenAI's language models,
    particularly for chat completions with structured outputs. It encapsulates the client and model
    configuration, allowing callable usage for generating responses.
    """

    client: OpenAI
    model: str

    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

    def __call__(
        self,
        messages: list[dict[str, str]],
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> T:
        """Complete a chat conversation with structured output using the responses API.

        This method sends the provided messages to the LLM and parses the response into the specified
        response_model structure. It is used for generating typed, structured outputs from chat interactions,
        typically in applications requiring predictable response formats like data extraction or API responses.

        Args:
            messages: List of message dictionaries for the chat conversation.
            response_model: The type to parse the response into.
            temperature: Controls randomness in generation (default: 0.7).
            max_tokens: Optional limit on output tokens.

        Returns:
            Parsed response of type T.
        """
        response = self.client.responses.parse(
            model=self.model,
            input=messages,
            text_format=response_model,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        return response.output_parsed


class GrokClient:
    """Wrapper for xAI Grok interactions using the native xAI SDK.

    This class provides a convenient interface to create and manage chat conversations
    with the Grok model, handling message appending and structured output parsing.
    It is typically used to generate responses with retries on transient errors.
    """

    client: Client
    model: str

    def __init__(self, client: Client, model: str) -> None:
        """Initialize the GrokClient with the SDK client and model name."""
        self.client = client
        self.model = model

    def __call__(
        self,
        messages: list[dict[str, str]],
        response_model: type[T],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        max_retries: int = 2,
    ) -> T:
        """Complete a chat conversation with structured output using the xAI SDK.

        This method creates a chat, appends messages, and parses the response into
        a Pydantic model. It supports retries on validation, connection, or timeout errors
        with exponential backoff.
        """
        for attempt in range(max_retries + 1):
            try:
                chat = self.client.chat.create(
                    model=self.model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                for message in messages:
                    if message["role"] == "system":
                        chat.append(system(message["content"]))
                    elif message["role"] == "user":
                        chat.append(user(message["content"]))
                    elif message["role"] == "assistant":
                        chat.append(assistant(message["content"]))
                    else:
                        raise ValueError(f"Unsupported role: {message['role']}")
                response, parsed_object = chat.parse(response_model)
                return parsed_object
            except (ValidationError, ConnectionError, TimeoutError) as e:
                if attempt == max_retries:
                    logging.error(f"Failed after {max_retries + 1} attempts: {e}")
                    raise
                wait_time = 2**attempt
                logging.warning(
                    f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)


openai_client = LLMClient(
    client=OpenAI(api_key=OPENAI_API_KEY),
    model=OPENAI_MODEL,
)

grok_client = GrokClient(
    client=Client(api_key=XAI_API_KEY),
    model=GROK_MODEL,
)
