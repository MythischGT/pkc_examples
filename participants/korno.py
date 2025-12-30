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

# ---- MITM identities ----
korno_as_jacob = Party("Korno→Jacob", dh)
korno_as_obo = Party("Korno→Obo", dh)

obo_ws = None

# ---- bidirectional proxy ----
async def proxy(jacob_ws):
    async def jacob_to_obo():
        while True:
            data = await jacob_ws.recv()
            plaintext = xor_decrypt(
                korno_as_jacob.session_key,
                bytes.fromhex(data)
            )
            print(f"\n[MITM] Jacob → Obo:", plaintext.decode())

            ciphertext = xor_encrypt(
                korno_as_obo.session_key,
                plaintext
            )
            await obo_ws.send(ciphertext.hex())

    async def obo_to_jacob():
        while True:
            data = await obo_ws.recv()
            plaintext = xor_decrypt(
                korno_as_obo.session_key,
                bytes.fromhex(data)
            )
            print(f"\n[MITM] Obo → Jacob:", plaintext.decode())

            ciphertext = xor_encrypt(
                korno_as_jacob.session_key,
                plaintext
            )
            await jacob_ws.send(ciphertext.hex())

    await asyncio.gather(jacob_to_obo(), obo_to_jacob())

# ---- Jacob connects here ----
async def handle_jacob(jacob_ws):
    print("[MITM] Jacob connected")

    # ---- DH with Jacob ----
    jacob_public = int(await jacob_ws.recv())
    await jacob_ws.send(str(korno_as_jacob.public))
    korno_as_jacob.compute_shared_key(jacob_public)
    print("[MITM] Key with Jacob established")

    await proxy(jacob_ws)

# ---- Connect to Obo first ----
async def connect_to_obo():
    global obo_ws
    obo_ws = await websockets.connect("ws://localhost:8765")

    await obo_ws.send(str(korno_as_obo.public))
    obo_public = int(await obo_ws.recv())
    korno_as_obo.compute_shared_key(obo_public)
    print("[MITM] Key with Obo established")

# ---- main ----
async def main():
    await connect_to_obo()

    async with websockets.serve(handle_jacob, "localhost", 9999):
        print("[MITM] Listening on ws://localhost:9999")
        await asyncio.Future()

asyncio.run(main())
