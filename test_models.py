from google import genai
import time
client = genai.Client(api_key='AIzaSyA4-kAX7rTCfL4RXBtzP6f-zUvfZyQj7oo')
models = ['gemini-3-flash-preview', 'gemini-3.1-flash-lite', 'gemini-3.1-flash-lite-preview', 'gemini-3.5-flash', 'gemini-pro-latest']
for m in models:
    try:
        res = client.models.generate_content(model=m, contents='say ok')
        print(f'SUCCESS: {m}')
    except Exception as e:
        print(f'FAILED {m}: {str(e)[:100]}')
    time.sleep(1)
