#!/usr/bin/env python3
"""
Run the notebook cells in sequence
"""
import sys
import os
from dotenv import load_dotenv

print("=" * 70)
print("RUNNING NOTEBOOK CELLS")
print("=" * 70)

# Cell 1: Hello
print("\n[Cell 1] print('hai')")
print("hai")

# Cell 2: Install packages
print("\n[Cell 2] %pip install langchain-anthropic")
print("Packages already installed")

# Cell 3: LangChain setup
print("\n[Cell 3] LangChain Setup")
print("-" * 70)

import operator
import math
import datetime
from typing import TypedDict, Annotated, Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage, ToolMessage, BaseMessage,
)
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

load_dotenv(override=True)
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    raise ValueError("ANTHROPIC_API_KEY not found. Add it to your .env file.")

base_url = os.getenv("ANTHROPIC_BASE_URL")
model_name = os.getenv("MODEL_NAME", "claude-opus-4-5-20251101-v1:0")

chat_model = ChatAnthropic(
    model=model_name,
    temperature=0.3,
    anthropic_api_key=anthropic_api_key,
    base_url=base_url,
)

from importlib.metadata import version
print("✅  Setup complete!")
print(f"   LangGraph       : {version('langgraph')}")
print(f"   langchain-anthropic : {version('langchain-anthropic')}")
print(f"   Model           : {model_name}")
print(f"   Base URL        : {base_url}")

try:
    _test = chat_model.invoke([HumanMessage(content="Say hello in one word.")])
    print(f"   Test call       : {_test.content.strip()}")
except Exception as e:
    print(f"   Test call failed: {e}")

# Cell 4: Raw API call
print("\n[Cell 4] Raw API Call")
print("-" * 70)

import requests
import json

API_KEY = os.getenv("ANTHROPIC_API_KEY")
BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
ENDPOINT = f"{BASE_URL}/v1/messages"

headers = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

payload = {
    "model": os.getenv("MODEL_NAME"),
    "max_tokens": 256,
    "temperature": 0.5,
    "system": "You are a helpful assistant.",
    "messages": [
        {
            "role": "user",
            "content": "What is the capital of Pakistan?"
        }
    ]
}

response = requests.post(ENDPOINT, headers=headers, json=payload)

print(f"Status Code : {response.status_code}")
print(f"Response    :\n{json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    reply = response.json()["content"][0]["text"]
    print(f"\nClaude says: {reply}")

print("\n" + "=" * 70)
print("NOTEBOOK EXECUTION COMPLETE")
print("=" * 70)
