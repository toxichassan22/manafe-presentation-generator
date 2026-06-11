import asyncio
import os
from google import genai
from google.genai import types

async def main():
    client = genai.Client(http_options={'api_version': 'v1beta'}, api_key='AIzaSyA4-kAX7rTCfL4RXBtzP6f-zUvfZyQj7oo')
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
            )
        )
    )
    
    print("Connecting to live preview model with AUDIO modality (the glitch)...")
    async with client.aio.live.connect(model='models/gemini-3.1-flash-live-preview', config=config) as session:
        print("Connected! Sending text prompt disguised in live session...")
        await session.send(input="Respond with 'Hello, this is a glitch!' and nothing else.", end_of_turn=True)
        print("Waiting for response...")
        async for response in session.receive():
            if response.text:
                print("Glitch text output:", response.text)
                break
                
asyncio.run(main())
