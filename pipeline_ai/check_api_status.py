import anthropic
import os
import sys
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_file)
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key or "your_" in api_key:
    print("API Key missing from .env!")
    sys.exit(1)

client = anthropic.Anthropic(api_key=api_key)

print("--------------------------------------------------")
print(f"Testing connection with Anthropic API...")
print(f"Key Prefix: {api_key[:12]}...")
print("--------------------------------------------------")

try:
    msg = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=10,
        messages=[{"role": "user", "content": "Just reply 'Hello'"}]
    )
    print("✅ [SUCCESS] The API key is fully active!")
    print("✅ [SUCCESS] You have sufficient credits!")
    print(f"✅ [SUCCESS] Model 'claude-sonnet-4-6' responded: {msg.content[0].text}")

except anthropic.RateLimitError as e:
    print("❌ [FAILED] Rate Limit Exceeded (Error 429).")
    print("CAUSE: You made too many requests in a short time. Please wait 1-2 minutes.")
    print(f"RAW ERROR: {str(e)}")

except anthropic.AuthenticationError as e:
    print("❌ [FAILED] Authentication Error (Invalid Key).")
    print("CAUSE: The API key is incorrect or revoked.")
    print(f"RAW ERROR: {str(e)}")

except anthropic.NotFoundError as e:
    print("❌ [FAILED] Model Not Found (Error 404).")
    print("CAUSE: Your account tier does not have access to the 'claude-sonnet-4-6' model.")
    print(f"RAW ERROR: {str(e)}")

except anthropic.APIStatusError as e:
    # 400 is common for exhausted free credits or disabled endpoints
    print(f"❌ [FAILED] API Connection Error (Status Code: {e.status_code}).")
    print(f"RAW ERROR: {str(e)}")

except Exception as e:
    print(f"❌ [FAILED] Unknown exception.")
    print(f"RAW ERROR: {str(e)}")
print("--------------------------------------------------")
