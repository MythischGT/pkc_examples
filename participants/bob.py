import asyncio
import websockets

from core.dhke import DHKE
from core.party import Party
from core.utils import xor_encrypt, xor_decrypt

dh = DHKE()

Bob = Party("Bob", dh)

async def handler(websocket):
    print("[Bob] Connected")
    print("[Bob] Public key of Bob:", Bob.public)
    print("[Bob] Public key of other party will be received shortly.")

    # ---- DH handshake ----
    alice_public = int(await websocket.recv())
    await websocket.send(str(Bob.public))

    Bob.compute_shared_key(alice_public)
    print("[Bob] Session key established")
    print("[Bob] You can now send and receive messages. Type 'exit' to quit.")
    print("[Bob] Public key of other party:", alice_public)

    # ---- receive loop ----
    async def receive():
        while True:
            data = await websocket.recv()
            plaintext = xor_decrypt(
                Bob.session_key,
                bytes.fromhex(data)
            )
            print(f"\n[Bob] Received:", plaintext.decode())

    # ---- send loop ----
    async def send():
        while True:
            msg = await asyncio.to_thread(input, "Bob > ")
            msg = msg.strip()

            if msg.lower() == "exit":
                break

            ciphertext = xor_encrypt(
                Bob.session_key,
                msg.encode()
            )
            print("[Bob] Sent encrypted text:", ciphertext)
            await websocket.send(ciphertext.hex())

    await asyncio.gather(receive(), send())

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("[Bob] Listening on ws://localhost:8765")
        await asyncio.Future()

asyncio.run(main())
