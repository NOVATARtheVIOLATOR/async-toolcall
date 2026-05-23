import json
from openai import OpenAI

MODEL = "gpt-5.4"

INSTRUCTIONS = (
    "You are the USG Ishimura onboard computer.  You must speak all responses using Dead Space lore, referring to the user using a random character's name. Initial sentence is always a lore-accurate USG Ishimura wall poster motto on its own line."
    "All tools support multiple asynchronous tool results. Until both arrive, you must suspend their tool flow. Ensure you strictly omit revealing the first result until you get the second one too."
)

TOOLS = [
    {
        "type": "function",
        "name": "marker",
        "description": (
            "Async proof-of-concept tool. "
            "This tool returns 2 asynchronous results, known as the Marker Code"
            "Wait for both results before continuing."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "strict": True,
    }
]

INPUT = [
    {
        "role": "user",
        "content": "Initiate convergence. Invoke function. Bring the marker onboard.",
    },
    {
        "role": "assistant",
        "content": "Making us whole... Please wait.",
    },
    {
        "type": "function_call",
        "call_id": "tool123",
        "name": "marker",
        "arguments": "{}",
    },
    {
        "role": "user",
        "content": "Can I see the marker code?",
    },
    {
        "role": "assistant",
        "content": "I cannot reveal its teachings until the second input arrives.",
    },
    {
        "type": "function_call_output",
        "call_id": "tool123",
        "output": "211-V Plasma Cutter",
    },
    {
        "role": "user",
        "content": "Are you ready for my biomass? Show me the marker!",
    },
]


def item_text(item):
    content = item.get("content", "")
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for part in content:
            text = part.get("text")
            if isinstance(text, str):
                parts.append(text)
        return "\n".join(parts)

    return ""


def response_text(response):
    if getattr(response, "output_text", None):
        return response.output_text

    parts = []
    for item in response.output:
        if getattr(item, "type", None) == "message":
            for part in getattr(item, "content", []):
                text = getattr(part, "text", None)
                if text:
                    parts.append(text)
    return "\n".join(parts)


def print_input_item(item):
    item_type = item.get("type")

    if item_type == "function_call":
        print(f"<ToolCall> id={item['call_id']}, name={item['name']}")
        return

    if item_type == "function_call_output":
        print(f"<ToolResponse> id={item['call_id']}, message={item['output']}")
        return

    role = item.get("role")
    text = item_text(item)

    if role == "user":
        print(f"<User> {text}")
    elif role == "assistant":
        print(f"<Agent> {text}")


def main():
    client = OpenAI()

    response = client.responses.create(
        model=MODEL,
        instructions=INSTRUCTIONS,
        tools=TOOLS,
        input=INPUT,
    )

    for item in INPUT:
        print_input_item(item)

    text = response_text(response).strip()
    if text:
        print(f"<Agent> {text}")


if __name__ == "__main__":
    main()