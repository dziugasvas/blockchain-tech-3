import os
import socket
import sys

from bitcoin.rpc import RawProxy, JSONRPCError

LAB_DIR = os.environ.get("LAB_DIR", os.path.expanduser("~/bitcoin-regtest-mif"))
RPC_PORT = 18443


def connect():
    cookie_path = os.path.join(LAB_DIR, "regtest", ".cookie")
    try:
        with open(cookie_path) as f:
            auth = f.read().strip()
    except OSError:
        fail("nerastas %s (ar paleistas bitcoind -regtest?)" % cookie_path)
    return RawProxy(service_url="http://%s@127.0.0.1:%d/" % (auth, RPC_PORT), timeout=10)


def call(proxy, method, *args):
    try:
        return getattr(proxy, method)(*args)
    except ConnectionRefusedError:
        fail("mazgas neatsako (connection refused)")
    except socket.timeout:
        fail("RPC uzklausa %s virsijo laika" % method)
    except JSONRPCError as e:
        fail("RPC klaida %s: %s" % (method, e.error.get("message", e.error)))


def fail(msg):
    print("KLAIDA:", msg, file=sys.stderr)
    sys.exit(1)