import asyncio
import websockets

from core.dhke import DHKE
from core.party import Party
from core.utils import xor_encrypt

p = 467
q = (p - 1) // 2
def find_generator(p, q):
    for g in range(2, p-1):
        if pow(g, q, p) == 1 and pow(g, 2, p) != 1:
            return g
    raise ValueError("No generator found")

g = find_generator(p, q)


dh = DHKE(p, g, q)
Jacob = Party("Jacob", dh)

async def run():
    async with websockets.connect("ws://localhost:9999") as ws:
        print("[Jacob] Connected")

        # ---- DH handshake ----
        await ws.send(str(Jacob.public))
        other_public = int(await ws.recv())
        Jacob.compute_shared_key(other_public)
        print("[Jacob] Session key established")

        # ---- Interactive loop ----
        while True:
            msg = await asyncio.to_thread(input, "Jacob > ")
            msg = msg.strip()

            if msg.lower() == "exit":
                break

            ciphertext = xor_encrypt(
                Jacob.session_key,
                msg.encode()
            )
            await ws.send(ciphertext.hex())
            print("[Jacob] Sent encrypted")

asyncio.run(run())
