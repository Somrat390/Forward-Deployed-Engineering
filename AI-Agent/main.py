import os
import asyncio
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq  # type: ignore[import-not-found]
from dotenv import load_dotenv

from tools.Currency_tool import get_exchange_rate
from tools.WeatherTool import current_weather
from tools.CalculatorTool import calculate

load_dotenv()

app = FastAPI(title="AI Agent")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = os.getenv("GROQ_MODEL")

tools = [

    # Calculator Tool
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform mathematical calculations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "add",
                            "subtract",
                            "multiply",
                            "divide",
                            "mod",
                            "power"
                        ],
                        "description": "Mathematical operation to perform."
                    },
                    "a": {
                        "type": "number",
                        "description": "First number."
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number."
                    }
                },
                "required": ["operation", "a", "b"]
            }
        }
    },
    # Weather Tool
    {
        "type": "function",
        "function": {
            "name": "current_weather",
            "description": (
                "Get the current weather information "
                "for a given city."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": (
                            "Name of the city, e.g. Dhaka or London."
                        )
                    }
                },
                "required": ["city"]
            }
        }
    },

    # Currency Exchange Tool
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": (
                "Get the latest available exchange rate "
                "between two currencies. Use three-letter "
                "currency codes such as USD, BDT, EUR, GBP."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {
                        "type": "string",
                        "description": "Source currency, e.g. USD."
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "Target currency, e.g. BDT."
                    }
                },
                "required": [
                    "from_currency",
                    "to_currency"
                ]
            }
        }
    }

]


available_functions = {

    "calculator": calculate,

    "current_weather": current_weather,

    "get_exchange_rate": get_exchange_rate

}


def execute_tool(tool_call):

    function_name = tool_call.function.name

    try:
        arguments = json.loads(
            tool_call.function.arguments
        )

    except json.JSONDecodeError:
        return {"error": "Invalid tool arguments."}

    function = available_functions.get(function_name)

    if function is None:
        return {"error": f"Unknown tool: {function_name}"}

    try:
        return function(**arguments)

    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}


def run_agent(user_input: str):

    messages = [

        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant with access "
                "to three tools: calculator, weather, and "
                "currency exchange. "
                "Use the appropriate tool whenever needed. "
                "Never invent calculation results, weather "
                "information, or exchange rates. "
                "If a tool returns an error, explain it to "
                "the user clearly."
            )
        },

        {
            "role": "user",
            "content": user_input
        }

    ]

    while True:

        response = client.chat.completions.create(

            model=MODEL,

            messages=messages,

            tools=tools,

            tool_choice="auto"

        )

        assistant_message = response.choices[0].message

        # Add LLM response to conversation
        messages.append(assistant_message)

        # Check whether the LLM requested a tool
        if not assistant_message.tool_calls:

            return assistant_message.content

        # Execute all requested tools
        for tool_call in assistant_message.tool_calls:

            result = execute_tool(tool_call)

            messages.append({

                "role": "tool",

                "tool_call_id": tool_call.id,

                "content": json.dumps(result)

            })


# ==========================================
# 7. Main Application
# ==========================================

if __name__ == "__main__":

    print("AI Agent Started!")
    print("Available Tools: Calculator, Weather, Currency")
    print("Type 'exit' or 'quit' to stop.")

    while True:

        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("Agent stopped.")
            break

        if not user_input:
            continue

        try:

            answer = run_agent(user_input)

            print("\nAssistant:", answer)

        except Exception as e:

            print("\nError:", str(e))




