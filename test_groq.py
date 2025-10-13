# test_groq.py
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ GROQ_API_KEY not found in .env file!")
    exit()

print(f"✅ API Key loaded: {api_key[:20]}...")

# Test connection
try:
    client = Groq(api_key=api_key)
    
    # Simple test
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": "Say 'Hello from Groq!' in one sentence."}
        ],
        max_tokens=50
    )
    
    print("✅ Groq API working!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ Error connecting to Groq: {e}")