import asyncio, websockets, json, base64, time, threading

with open(r"C:\Users\pc\Desktop\Achyuta_v2.0\gemini_api_key.json") as f:
    key = json.load(f)["gemini_api_key"]

MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"

class PersistentGeminiVoiceSession:
    def __init__(self, system_prompt):
        self.uri = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={key}"
        self.system_prompt = system_prompt
        self.ws = None
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        future = asyncio.run_coroutine_threadsafe(self._connect(), self.loop)
        future.result(timeout=10)

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _connect(self):
        self.ws = await websockets.connect(self.uri)
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
                    "parts": [{"text": self.system_prompt}]
                }
            }
        }
        await self.ws.send(json.dumps(setup))
        await self.ws.recv()

    def generate_reply(self, customer_words, step_target):
        future = asyncio.run_coroutine_threadsafe(self._turn(customer_words, step_target), self.loop)
        return future.result(timeout=15)

    async def _turn(self, customer_words, step_target):
        t0 = time.time()
        prompt = f'The caller just said: "{customer_words}". Reply directly to them now in Hindi, and mention: "{step_target}"'
        await self.ws.send(json.dumps({
            "clientContent": {
                "turns": [{"role": "user", "parts": [{"text": prompt}]}],
                "turnComplete": True
            }
        }))
        accumulated_pcm = bytearray()
        first_chunk_t = None
        while True:
            raw = await self.ws.recv()
            d = json.loads(raw)
            sc = d.get("serverContent", {})
            turn = sc.get("modelTurn", {})
            for p in turn.get("parts", []):
                if "inlineData" in p:
                    if first_chunk_t is None:
                        first_chunk_t = time.time() - t0
                    accumulated_pcm.extend(base64.b64decode(p["inlineData"]["data"]))
            if sc.get("turnComplete"):
                break
        print(f"Persistent Session Turn: First chunk in {first_chunk_t:.2f}s! Total audio: {len(accumulated_pcm)} bytes in {time.time()-t0:.2f}s")
        return bytes(accumulated_pcm)

    def close(self):
        try:
            future = asyncio.run_coroutine_threadsafe(self.ws.close(), self.loop)
            future.result(timeout=3)
        except Exception:
            pass

if __name__ == "__main__":
    session = PersistentGeminiVoiceSession("You are Priya from KV Traders in Hindi. Keep responses short and conversational.")
    print("Session ready! Running Turn 1...")
    pcm1 = session.generate_reply("Hello, kaun bol raha hai?", "Hum KV Traders se bol rahe hain")
    print("Running Turn 2 on same persistent session...")
    pcm2 = session.generate_reply("Aapke paas kya saman hai?", "Humare paas building material aur hardware hai")
    session.close()
    print("SUCCESS! Both turns completed on a single open WebSocket!")
