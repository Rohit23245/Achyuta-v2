import asyncio, websockets, json, wave, io, base64, time

with open(r"C:\Users\pc\Desktop\Achyuta_v2.0\gemini_api_key.json") as f:
    key = json.load(f)["gemini_api_key"]

MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"

async def generate_step_voice(customer_input, step_target, agent_instructions):
    uri = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={key}"
    async with websockets.connect(uri) as ws:
        system_instruction = f"""You are a polite female Indian telephone calling executive named Priya.
Rules:
1. Speak in natural conversational Hindi directly to the customer in 1-2 short sentences.
2. Directly acknowledge or answer what the customer asked (e.g. if they say Hello or Kaun, answer politely).
3. Smoothly progress towards your conversation goal: "{step_target}".
4. Additional instructions: "{agent_instructions}".
5. NEVER explain your thoughts or mention AI. Only speak directly to the caller."""

        setup = {
            "setup": {
                "model": f"models/{MODEL}",
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {
                        "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Aoede"}}
                    }
                },
                "systemInstruction": {
                    "parts": [{"text": system_instruction}]
                }
            }
        }
        await ws.send(json.dumps(setup))
        await ws.recv()

        t0 = time.time()
        await ws.send(json.dumps({
            "clientContent": {
                "turns": [{
                    "role": "user",
                    "parts": [{"text": f"The customer on the phone said: \"{customer_input}\". Respond directly to them now:"}]
                }],
                "turnComplete": True
            }
        }))

        pcm_bytes = bytearray()
        first_t = None
        while True:
            raw = await ws.recv()
            d = json.loads(raw)
            sc = d.get("serverContent", {})
            turn = sc.get("modelTurn", {})
            for p in turn.get("parts", []):
                if "inlineData" in p:
                    if first_t is None:
                        first_t = time.time() - t0
                    pcm_bytes.extend(base64.b64decode(p["inlineData"]["data"]))
            if sc.get("turnComplete"):
                break
        print(f"Done! First audio at {first_t:.2f}s, total audio: {len(pcm_bytes)} bytes in {time.time()-t0:.2f}s")

if __name__ == "__main__":
    asyncio.run(generate_step_voice("Hello kaun bol raha hai", "Humare paas festive discounts hain", "Priya from KV Traders"))
