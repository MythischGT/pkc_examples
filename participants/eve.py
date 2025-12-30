import asyncio
import websockets

from core.dhke import DHKE
from core.party import Party
from core.utils import xor_encrypt, xor_decrypt

dh = DHKE()

# ---- Eve identities ----
eve_as_alice = Party("Eve→Alice", dh)
eve_as_bob = Party("Eve→Bob", dh)

bob_ws = None

# ---- bidirectional proxy ----
async def proxy(alice_ws):
    async def alice_to_bob():
        while True:
            data = await alice_ws.recv()
            plaintext = xor_decrypt(
                eve_as_alice.session_key,
                bytes.fromhex(data)
            )
            print(f"\n[Eve] Alice → Bob: Ciphertext decrypted to plaintext:", plaintext.decode())

            ciphertext = xor_encrypt(
                eve_as_bob.session_key,
                plaintext
            )
            await bob_ws.send(ciphertext.hex())

    async def bob_to_alice():
        while True:
            data = await bob_ws.recv()
            plaintext = xor_decrypt(
                eve_as_bob.session_key,
                bytes.fromhex(data)
            )
            print(f"\n[Eve] Bob → Alice: Ciphertext decrypted to plaintext:", plaintext.decode())

            ciphertext = xor_encrypt(
                eve_as_alice.session_key,
                plaintext
            )
            await alice_ws.send(ciphertext.hex())

    await asyncio.gather(alice_to_bob(), bob_to_alice())

# ---- Alice connects here ----
async def handle_alice(alice_ws):
    print("[Eve] Alice connected")
    print("[Eve] Public key of Eve (to Alice):", eve_as_alice.public)
    print("[Eve] Public key of Eve (to Bob) will be sent shortly.")

    # ---- DH with Alice ----
    alice_public = int(await alice_ws.recv())
    await alice_ws.send(str(eve_as_alice.public))
    eve_as_alice.compute_shared_key(alice_public)
    print("[Eve] Key with Alice established")

    await proxy(alice_ws)

# ---- Connect to Bob first ----
async def connect_to_bob():
    global bob_ws
    bob_ws = await websockets.connect("ws://localhost:8765")

    await bob_ws.send(str(eve_as_bob.public))
    bob_public = int(await bob_ws.recv())
    eve_as_bob.compute_shared_key(bob_public)
    print("[Eve] Key with Bob established")
    print("[Eve] Public key of Eve (to Bob):", eve_as_bob.public)

# ---- main ----
async def main():
    await connect_to_bob()

    async with websockets.serve(handle_alice, "localhost", 9999):
        print("[Eve] Listening on ws://localhost:9999")
        await asyncio.Future()

asyncio.run(main())
