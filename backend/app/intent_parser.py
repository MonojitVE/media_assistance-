import json
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Literal
from app.config import settings

class IntentSchema(BaseModel):
    action: Literal["play", "slideshow", "explore", "unknown"]
    type: Literal["video", "audio", "image", "unknown"]
    mode: Literal["mixed", "ordered"] = "ordered"
    subtype: Optional[Literal["short", "long", "photo", "screenshot"]] = None
    order: Optional[Literal["shortest_first", "longest_first"]] = None
    raw_text: str

def parse_command(text: str) -> dict:
    """
    Uses Groq LLM to convert a natural language command into a structured JSON intent.
    Falls back to a basic unknown intent if API fails or key is missing.
    """
    if not settings.groq_api_key:
        print("[WARNING] No GROQ_API_KEY set. Cannot parse intent intelligently.")
        return {"action": "unknown", "raw_text": text}
        
    client = OpenAI(
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    system_prompt = f"""You are a Smart Media Assistant AI. Your job is to convert natural language commands into structured JSON.
Schema:
{json.dumps(IntentSchema.model_json_schema(), indent=2)}

Rules:
- action: "play" for video/audio, "slideshow" for images, "explore" for showing folders or categories. If intent is unclear, use "unknown".
- type: "video", "audio", or "image".
- mode: "mixed" if they want a mix, otherwise "ordered".
- subtype: "short" (<2min), "long", "photo", "screenshot". Can be null if not specified.
- order: "shortest_first" (default for ordered) or "longest_first". Can be null.
- raw_text: exactly what the user said.

Always return a valid JSON object matching this schema. Do not include markdown formatting or extra text.
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        intent_data = json.loads(content)
        
        # Validate through Pydantic
        intent = IntentSchema(**intent_data)
        
        # Add fallback default overrides if the LLM hallucinated
        return intent.model_dump()
        
    except ValidationError as ve:
        print(f"[ERROR] LLM returned invalid schema: {ve}")
        return {"action": "unknown", "raw_text": text}
    except Exception as e:
        print(f"[ERROR] Groq API error: {e}")
        return {"action": "unknown", "raw_text": text}
