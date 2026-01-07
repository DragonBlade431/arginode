import asyncio, json, random, time
import websockets

# Realistic Indian soil fertility profiles (kg/ha)
SOIL_PROFILES = [
    {"N": (60,120),  "P": (5,15),   "K": (80,120)},   # Low fertility
    {"N": (120,200), "P": (10,25),  "K": (120,220)},  # Medium fertility
    {"N": (200,350), "P": (20,40),  "K": (220,350)},  # High fertility
]

async def main():
    uri = "ws://127.0.0.1:8000/ws/esp32"
    async with websockets.connect(uri) as ws:
        for i in range(5):

            # Pick a realistic soil profile
            profile = random.choice(SOIL_PROFILES)

            N = random.randint(*profile["N"])
            P = random.randint(*profile["P"])
            K = random.randint(*profile["K"])

            payload = {
                "N": N,
                "P": P,
                "K": K,
                "pH": round(random.uniform(5.8, 7.8), 2),
                "temp": round(random.uniform(22, 36), 2),
                "humidity": round(random.uniform(40, 85), 1),
                "soil": round(random.uniform(20, 70), 1),
                "rainfall": round(random.uniform(0, 10), 2),
                "lat": 12.9716,
                "lon": 77.5946,
                "ts": int(time.time() * 1000)
            }

            await ws.send(json.dumps(payload))
            print("Sent:", payload)

            try:
                echo = await asyncio.wait_for(ws.recv(), timeout=0.5)
                print("Echo:", echo)
            except asyncio.TimeoutError:
                pass

            await asyncio.sleep(0.5)

asyncio.run(main())