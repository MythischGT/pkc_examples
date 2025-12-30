import asyncio
import websockets

from core.dhke import DHKE
from core.party import Party
from core.utils import xor_encrypt, xor_decrypt

# ---- DH parameters ----
p = 467
q = (p - 1) // 2

def find_generator(p, q):
    for g in range(2, p - 1):
        if pow(g, q, p) == 1 and pow(g, 2, p) != 1:
            return g
    raise ValueError("No generator found")

g = find_generator(p, q)
dh = DHKE(p, g, q)

Obo = Party("Obo", dh)

async def handler(websocket):
    print("[Obo] Connected")

    # ---- DH handshake ----
    alice_public = int(await websocket.recv())
    await websocket.send(str(Obo.public))

    Obo.compute_shared_key(alice_public)
    print("[Obo] Session key established")

    # ---- receive loop ----
    async def receive():
        while True:
            data = await websocket.recv()
            plaintext = xor_decrypt(
                Obo.session_key,
                bytes.fromhex(data)
            )
            print(f"\n[Obo] Received:", plaintext.decode())

    # ---- send loop ----
    async def send():
        while True:
            msg = await asyncio.to_thread(input, "Obo > ")
            msg = msg.strip()

            if msg.lower() == "exit":
                break

            ciphertext = xor_encrypt(
                Obo.session_key,
                msg.encode()
            )
            await websocket.send(ciphertext.hex())

    await asyncio.gather(receive(), send())

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("[Obo] Listening on ws://localhost:8765")
        await asyncio.Future()

asyncio.run(main())
