import io
import sys
from decimal import Decimal

from bitcoin.core import CTransaction, x, b2lx, Hash

from rpc_common import connect, call, fail

TXID = "76c754e5d6a8a2236212d2220d71ef670a8bc0f1804092694015ce63d72e7213"
BLOCKHASH = "45e98ab37d6dc7d91b8bc5408c448784df6a084d3549c27dc3b6af03c59a619b"
SAT = Decimal(100000000)


def sats(btc):
    return int(btc * SAT)


def sizes(raw_hex):
    tx = CTransaction.deserialize(x(raw_hex))
    f = io.BytesIO()
    tx.stream_serialize(f, include_witness=False)
    base_bytes = f.getvalue()
    base = len(base_bytes)
    total = len(x(raw_hex))
    weight = 3 * base + total
    vsize = (weight + 3) // 4
    return base_bytes, base, total, weight, vsize


txid = sys.argv[1] if len(sys.argv) > 1 else TXID
blockhash = sys.argv[2] if len(sys.argv) > 2 else BLOCKHASH

p = connect()
tx = call(p, "getrawtransaction", txid, 2, blockhash)

print("txid:  ", tx["txid"])
print("wtxid: ", tx["hash"])
print("blokas:", tx.get("blockhash", "dar ne bloke"))
print()

total_in = 0
print("Iejimai:")
for vin in tx["vin"]:
    if "coinbase" in vin:
        fail("coinbase transakcija neturi iejimu, mokescio skaiciuoti nereikia")
    prev = vin.get("prevout")
    if prev is None:
        fail("mazgas negrazino prevout duomenu")
    addr = prev["scriptPubKey"].get("address", "(nera adreso)")
    total_in += sats(prev["value"])
    print("  %s:%d  %s  %d sat" % (vin["txid"], vin["vout"], addr, sats(prev["value"])))

total_out = 0
print("Isejimai:")
for vout in tx["vout"]:
    addr = vout["scriptPubKey"].get("address", "(nera adreso)")
    total_out += sats(vout["value"])
    print("  n=%d  %s  %d sat" % (vout["n"], addr, sats(vout["value"])))

fee = total_in - total_out
print()
print("Iejimu suma:  ", total_in, "sat")
print("Isejimu suma: ", total_out, "sat")
print("Mokestis:     ", fee, "sat")
if "fee" in tx:
    print("Mazgo fee:    ", sats(tx["fee"]), "sat", "SUTAMPA" if sats(tx["fee"]) == fee else "NESUTAMPA")
print("Fee rate:      %.2f sat/vB" % (fee / tx["vsize"]))
print()

base_bytes, base, total, weight, vsize = sizes(tx["hex"])
txid_calc = b2lx(Hash(base_bytes))
wtxid_calc = b2lx(Hash(x(tx["hex"])))
print("txid  is hex be witness:", "SUTAMPA" if txid_calc == tx["txid"] else "NESUTAMPA")
print("wtxid is pilno hex:     ", "SUTAMPA" if wtxid_calc == tx["hash"] else "NESUTAMPA")
segwit = any("txinwitness" in vin for vin in tx["vin"])
print("SegWit:", "taip" if segwit else "ne")
print("            mazgas  apskaiciuota")
print("size        %6d  %6d" % (tx["size"], total))
print("weight      %6d  %6d" % (tx["weight"], weight))
print("vsize       %6d  %6d" % (tx["vsize"], vsize))
print("base_size           %6d" % base)
print("Dydziai", "SUTAMPA" if (tx["size"], tx["weight"], tx["vsize"]) == (total, weight, vsize) else "NESUTAMPA")
print()

with open("data/alice_legacy.hex") as f:
    alice_hex = f.read().strip()
_, abase, atotal, aweight, avsize = sizes(alice_hex)
alice_txid = b2lx(Hash(x(alice_hex)))
print("Legacy palyginimas (Mastering Bitcoin, Alice tx):")
print("  txid:   ", alice_txid)
print("  wtxid:  ", alice_txid, "(be witness txid == wtxid)")
print("  size %d, base %d, weight %d, vsize %d" % (atotal, abase, aweight, avsize))
print()
print("Musu SegWit tx: txid != wtxid:", tx["txid"] != tx["hash"])
print("Musu SegWit tx: vsize < size:", vsize < total, "(witness baitai sveria 1, ne 4)")