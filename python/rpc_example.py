from datetime import datetime, timezone

from rpc_common import connect, call

p = connect()

chain = call(p, "getblockchaininfo")
net = call(p, "getnetworkinfo")

print("Laikas (UTC):       ", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
print("Tinklas:            ", chain["chain"])
print("Blokai:             ", chain["blocks"])
print("Antrastes:          ", chain["headers"])
print("Geriausias blokas:  ", chain["bestblockhash"])
print("IBD:                ", chain["initialblockdownload"])
print("Versija:            ", net["version"], net["subversion"])
print("Jungtys:            ", call(p, "getconnectioncount"))

if chain["chain"] != "regtest":
    print("DEMESIO: tai ne regtest tinklas")