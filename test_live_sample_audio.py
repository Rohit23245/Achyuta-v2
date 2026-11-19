import os
import json
import base64
import asyncio
import websockets
import time

with open(r"C:\Users\pc\Desktop\Achyuta_v2.0\gemini_api_key.json", "r") as f:
    keys = json.load(f)
    api_key = keys.get("gemini_api_key")

MODEL_NAME = "gemini-2.5-flash-native-audio-preview-12-2025"
VOICE_NAME = "Aoede"

async def test_sample_audio_interaction():
    uri = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={api_key}"
    print(f"[Test] Connecting to Gemini Live WebSocket...")
    print(f"[Test] Model: {MODEL_NAME} | Voice: {VOICE_NAME}")

    system_instruction = (
        "You are Priya, a polite female customer executive calling from Achyuta Technologies in Hindi. "
        "Strict rules:\n"
        "1. Always respond verbally directly to the caller in natural conversational Hindi (1-2 short sentences max).\n"
        "2. If the caller asks 'kaun bol raha hai' (who is speaking/calling), immediately tell them: 'Main Achyuta Technologies se Priya baat kar rahi hoon' and ask how they are doing.\n"
        "3. Never output internal thoughts or planning, only direct spoken Hindi words."
    )

    async with websockets.connect(uri) as ws:
        setup_msg = {
            "setup": {
                "model": f"models/{MODEL_NAME}",
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {
                        "voiceConfig": {
                            "prebuiltVoiceConfig": {
                                "voiceName": VOICE_NAME
                            }
                        }
                    }
                },
                "systemInstruction": {
                    "parts": [{"text": system_instruction}]
                }
            }
        }
        await ws.send(json.dumps(setup_msg))
        setup_ack = await ws.recv()
        print(f"[Test] Setup completed: {setup_ack.strip()}")

        # Test simulated caller saying 'Kaun bol raha hai?'
        print("[Test] Sending simulated caller voice question: 'Kaun bol raha hai?'...")
        caller_turn = {
            "clientContent": {
                "turns": [{
                    "role": "user",
                    "parts": [{"text": "Hello, kaun bol raha hai?"}]
                }],
                "turnComplete": True
            }
        }
        await ws.send(json.dumps(caller_turn))

        accumulated_pcm = bytearray()
        received_text = ""
        start_t = time.time()
        while True:
            raw_msg = await asyncio.wait_for(ws.recv(), timeout=12)
            data = json.loads(raw_msg)
            server_content = data.get("serverContent", {})
            parts = server_content.get("modelTurn", {}).get("parts", [])
            for p in parts:
                if "text" in p:
                    received_text += p["text"]
                if "inlineData" in p:
                    b64_audio = p["inlineData"].get("data", "")
                    if b64_audio:
                        accumulated_pcm.extend(base64.b64decode(b64_audio))
            if server_content.get("turnComplete"):
                elapsed = time.time() - start_t
                duration_sec = len(accumulated_pcm) / (24000 * 2)
                print(f"[Test] SUCCESS!")
                print(f"[Test] Response received in {elapsed:.2f} seconds.")
                print(f"[Test] Audio generated: {len(accumulated_pcm)} bytes PCM 24kHz (~{duration_sec:.2f} seconds of clear voice speech).")
                print(f"[Test] Transcript/Thoughts: {received_text.strip()[:180]}...")
                break

if __name__ == "__main__":
    asyncio.run(test_sample_audio_interaction())
