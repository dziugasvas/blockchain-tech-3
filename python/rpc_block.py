import struct
import sys
from decimal import Decimal

from bitcoin.core import Hash, b2lx

from rpc_common import connect, call, fail

SAT = Decimal(100000000)


def sats(btc):
    return int(btc * SAT)


def header_bytes(b, nonce=None):
    prev = b.get("previousblockhash", "00" * 32)
    return (struct.pack("<i", b["version"])
            + bytes.fromhex(prev)[::-1]
            + bytes.fromhex(b["merkleroot"])[::-1]
            + struct.pack("<I", b["time"])
            + struct.pack("<I", int(b["bits"], 16))
            + struct.pack("<I", b["nonce"] if nonce is None else nonce))


def target(bits):
    n = int(bits, 16)
    return (n & 0xffffff) << (8 * ((n >> 24) - 3))


p = connect()
blockhash = sys.argv[1] if len(sys.argv) > 1 else call(p, "getbestblockhash")
b = call(p, "getblock", blockhash, 2)

print("Blokas:    ", b["hash"])
print("Aukstis:   ", b["height"])
print("Tx kiekis: ", b["nTx"])
print()

total_out = 0
fees = 0
coinbase_out = 0
for i, tx in enumerate(b["tx"]):
    out = sum(sats(v["value"]) for v in tx["vout"])
    total_out += out
    if i == 0:
        coinbase_out = out
    else:
        if "fee" not in tx:
            fail("mazgas negrazino fee laukelio")
        fees += sats(tx["fee"])
    print("  %s  %d isejimai  %d sat" % (tx["txid"], len(tx["vout"]), out))

subsidy = 5000000000 >> (b["height"] // 150)
print()
print("Visu isejimu suma: ", total_out, "sat (%s BTC)" % (Decimal(total_out) / SAT))
print("Coinbase isejimai: ", coinbase_out, "sat")
print("Subsidija + fee:   ", subsidy, "+", fees, "=", subsidy + fees, "sat",
      "SUTAMPA" if coinbase_out == subsidy + fees else "NESUTAMPA")
print()

h = header_bytes(b)
calc = b2lx(Hash(h))
node_hex = call(p, "getblockheader", blockhash, False)
print("Antraste (%d baitu):" % len(h))
print(" ", h.hex())
print("Antraste kaip mazge:", "SUTAMPA" if h.hex() == node_hex else "NESUTAMPA")
print("SHA256d(antraste):  ", calc)
print("Bloko hash:         ", b["hash"], "SUTAMPA" if calc == b["hash"] else "NESUTAMPA")
print("hash <= target:     ", int(calc, 16) <= target(b["bits"]), "(bits %s)" % b["bits"])
print()

changed = b2lx(Hash(header_bytes(b, b["nonce"] + 1)))
print("nonce + 1 ->        ", changed)
print("Hash pasikeite:     ", changed != calc)