import asyncio
import websockets

from core.dhke import DHKE
from core.party import Party
from core.utils import xor_encrypt, xor_decrypt

dh = DHKE()
Alice = Party("Alice", dh)

async def run():
    async with websockets.connect("ws://localhost:9999") as ws:
        print("[Alice] Connected")

        # ---- DH handshake ----
        await ws.send(str(Alice.public))
        other_public = int(await ws.recv())
        Alice.compute_shared_key(other_public)
        print("[Alice] Session key established")
        print("[Alice] You can now send messages. Type 'exit' to quit.")
        print("[Alice] Public key of Alice:", Alice.public)
        print("[Alice] Public key of other party:", other_public)

            # ---- receive loop ----
        async def receive():
            while True:
                data = await ws.recv()
                plaintext = xor_decrypt(
                    Alice.session_key,
                    bytes.fromhex(data)
                )
                print(f"\n[Alice] Received:", plaintext.decode())

            # ---- send loop ----
        async def send():
            while True:
                msg = await asyncio.to_thread(input, "Alice > ")
                msg = msg.strip()

                if msg.lower() == "exit":
                    break

                ciphertext = xor_encrypt(
                    Alice.session_key,
                    msg.encode()
                )
                print("[Alice] Sent encrypted text:", ciphertext)
                await ws.send(ciphertext.hex())

        await asyncio.gather(receive(), send())

asyncio.run(run())
