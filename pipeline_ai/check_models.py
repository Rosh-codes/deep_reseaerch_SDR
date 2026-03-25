import anthropic
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_file)
api_key = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)

models_to_test = [
    "claude-3-5-sonnet-latest",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620"
]

print("--- Testing Model Availability ---")
for m in models_to_test:
    try:
        msg = client.messages.create(
            model=m,
            max_tokens=5,
            messages=[{"role": "user", "content": "hi"}]
        )
        print(f"[SUCCESS] You have access to: {m}")
    except Exception as e:
        print(f"[FAILED] No access to: {m} -> Error: {str(e)}")
print("---------------------------------")
