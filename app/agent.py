# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.firestore_tools import (
    search_recipes,
    get_recipe_details,
    add_recipe,
    generate_grocery_shopping_list,
)
import json
from pathlib import Path

from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.memory import VertexAiMemoryBankService


from app.online_api_tools import search_online_recipes
from app.maps_tools import geocode_address, find_nearby_places
from app.image_tools import generate_recipe_image


_metadata_path = Path(__file__).parent.parent / "deployment_metadata.json"
_agent_engine_resource_name = None
if _metadata_path.exists():
    try:
        with open(_metadata_path, "r") as _f:
            _meta = json.load(_f)
            _agent_engine_resource_name = _meta.get("remote_agent_runtime_id")
    except Exception:
        pass

if not _agent_engine_resource_name:
    _agent_engine_resource_name = "projects/911795412318/locations/us-east1/reasoningEngines/428253181948985344"







def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


def memory_bank_service_builder():
    memory_bank_id = _agent_engine_resource_name.split("/")[-1]
    return VertexAiMemoryBankService(
        project="qwiklabs-gcp-01-0f8258c0f681",
        location="us-east1",
        agent_engine_id=memory_bank_id,
    )


from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from app.a2ui_utils import a2ui_callback

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are Recipe Concierge, a helpful culinary AI assistant. "
        "Use your Firestore recipe tools to search for recipes, retrieve recipe details, or save new recipes. "
        "You can also run Python code in a safe sandbox to perform calculations, conversions, or data manipulation. "
        "IMPORTANT: Automatically remember and record all user dietary preferences, allergies, and food intolerances "
        "(e.g., peanuts, gluten, dairy, shellfish, tree nuts). Always check preloaded memory for known user allergies "
        "and NEVER suggest recipes or ingredients containing those allergens unless explicitly instructed by the user."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=AgentEngineSandboxCodeExecutor(
        agent_engine_resource_name=_agent_engine_resource_name
    ),
    instruction=a2ui_instruction,
    tools=[
        PreloadMemoryTool(),
        get_weather,
        get_current_time,
        search_recipes,
        get_recipe_details,
        add_recipe,
        generate_grocery_shopping_list,
        search_online_recipes,
        geocode_address,
        find_nearby_places,
        generate_recipe_image,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)


app = App(
    root_agent=root_agent,
    name="app",
)


