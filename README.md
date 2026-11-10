# Bitcoin duomenų analizė: Merkle, regtest mazgas ir RPC

Blokų grandinių technologijos, 3 užduotis (papildoma). Trys dalys:

1. **Merkle medis su Libbitcoin** (`merkle/`, C++)
2. **Nuosavas Bitcoin Core mazgas regtest tinkle** (`node/`)
3. **Python RPC analizė** (`python/`)

## Aplinka

| | |
|---|---|
| OS | macOS 26.6.2 (Apple M4, arm64) |
| Kompiliatorius | Apple clang 21.0.0 |
| Libbitcoin | libbitcoin-system v3.8.0, sukompiliuota iš šaltinių į `~/libbitcoin` |
| Boost | 1.72 (su dviem pataisymais, žr. žemiau) |
| Bitcoin Core | v31.1.0, regtest |
| Python | 3.14.3, python-bitcoinlib 0.12.2 |

### Libbitcoin diegimas

Homebrew nebeturi `libbitcoin-system`, todėl biblioteka sukompiliuota iš šaltinių (v3.8.0, statinė):

- Boost 1.72 su nauju clang nesikompiliuoja (klaida *integer value -1 is outside the valid range of values for the enumeration type*). Pataisyta dviem vietomis:
  - `boost/numeric/conversion/detail/*_mixture.hpp`: `mpl::integral_c<` pakeista į `boost::integral_constant<`;
  - `boost/mpl/aux_/integral_wrapper.hpp`: sąlyga papildyta `|| __cplusplus >= 201103L`.
- secp256k1 iš libbitcoin `version7` šakos.
- libbitcoin-system v3.8.0: `./autogen.sh && ./configure --prefix=$HOME/libbitcoin --with-boost=$HOME/libbitcoin --disable-shared --enable-static --without-tests --without-examples && make && make install`.

Makefile ima kompiliavimo vėliavas per `pkg-config --static` ir bibliotekos antraštes įtraukia per `-isystem`, kad nesimatytų pačios bibliotekos įspėjimų.

## 1 dalis: Merkle medis (Libbitcoin)

```bash
make            # sukompiliuoja run_merkle
./run_merkle    # bloko 100000 pavyzdys
./run_merkle <txid1> <txid2> ...
make test       # 13 testų
```

- `merkle/merkle.cpp`: `create_merkle()` jungia hash'us poromis ir skaičiuoja `bc::bitcoin_hash` (SHA256d). Jei lygyje nelyginis kiekis, paskutinis dubliuojamas.
- RPC rodo txid apverstu baitų eiliškumu, todėl `parse_txid()` per `bc::decode_hash` juos apverčia į vidinį formatą, o rezultatas grąžinamas atgal per `bc::encode_hash`.
- Tuščias sąrašas ir blogas hex (ne 64 simboliai, ne hex) atmetami su klaida.

**Rezultatas:** mainnet bloko 100000 šaknis `f3e94742...a95766` sutampa. Regtest bloko 102 šaknis taip pat sutampa su `getblock` `merkleroot` (`node/07_merkle_regtest.txt`).

Tas pats modulis įtrauktas ir į 2 užduoties repozitoriją ([blockchain-tech-2](https://github.com/dziugasvas/blockchain-tech-2), šaka `a3`, žyma `a3-merkle`, komanda `make bitcoin`).

## 2 dalis: Bitcoin Core regtest mazgas

- Atsisiųstas Bitcoin Core 31.1. `SHA256SUMS` patikrintas (`shasum -a 256 --check`), GPG parašai patikrinti su guix.sigs builder raktais (`node/00_*`).
- Mazgas paleistas atskirame kataloge `~/bitcoin-regtest-mif` (`bitcoind -regtest -datadir=... -daemon`), komandos per `bitcoin-cli -regtest -datadir=...`.
- Sukurtos piniginės, iškasti 101 blokai: coinbase subręsta po 100 blokų, todėl liko 50 BTC prieinama ir 5000 BTC nesubrendę (`node/02_*`).
- Atliktas mokėjimas 1 BTC. Prieš bloką transakcija buvo mempool'e (0 patvirtinimų), po bloko 102 turi 1 patvirtinimą (`node/04_*`, `node/05_*`, `node/06_decoded_tx.json`).

Repozitorijoje nėra `.cookie`, slaptažodžių, privačių raktų ar piniginių failų.

## 3 dalis: Python RPC analizė

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python rpc_example.py
python rpc_transaction.py [txid] [blockhash]
python rpc_block.py [blockhash]
```

Prisijungimas (`rpc_common.py`) naudoja mazgo `.cookie` failą iš `~/bitcoin-regtest-mif/regtest/` (kitą katalogą galima nurodyti per `LAB_DIR`). Visi RPC kvietimai eina per `call()`: išjungtas mazgas, laiko viršijimas ar RPC klaida rodomi kaip `KLAIDA: ...`, o ne traceback (`outputs/04_*`, `outputs/05_*`). Sumos skaičiuojamos satošiais (`Decimal` → `int`), kad neliktų float paklaidų.

### rpc_example.py

Rodo tinklą, aukštį, antraštes, versiją ir jungčių skaičių (`outputs/01_rpc_example.txt`).

### rpc_transaction.py

| | Mazgas | Apskaičiuota |
|---|---|---|
| Mokestis | 282 sat | 5 000 000 000 − 4 999 999 718 = 282 sat |
| Fee rate | | 282 / 141 = 2.00 sat/vB |
| size | 222 | 222 |
| weight | 561 | 3 × 113 + 222 = 561 |
| vsize | 141 | ⌈561 / 4⌉ = 141 |

Mokestis = įėjimų (prevout) suma − išėjimų suma. Transakcija SegWit, todėl txid skaičiuojamas iš serializacijos be witness (113 B), o wtxid iš pilnos (222 B). Abu sutampa su mazgo reikšmėmis. Witness baitai sveria 1, o kiti 4, todėl vsize (141) mažesnis už size (222).

Palyginimui naudojama legacy transakcija iš *Mastering Bitcoin* (Alice, `data/alice_legacy.hex`): joje nėra witness, todėl txid = wtxid, base = size = vsize = 258, weight = 4 × 258 (`outputs/02_rpc_transaction.txt`).

### rpc_block.py

- Blokas 102: 2 transakcijos, visų išėjimų suma 100 BTC.
- Coinbase gavo 5 000 000 282 sat = subsidija 50 BTC + 282 sat mokestis (regtest subsidija mažėja kas 150 blokų).
- 80 baitų antraštė atkurta iš laukų: version, prev ir merkle (apversti), time, bits, nonce, visi little-endian. Ji sutampa su `getblockheader <hash> false`, o SHA256d (apverstas) = bloko hash.
- hash ≤ target (bits `207fffff`). Pakeitus nonce +1, gaunamas visai kitas hash (`outputs/03_rpc_block.txt`).

## DI naudojimas

Šiai užduočiai naudotas DI asistentas (Claude): Libbitcoin ir Boost diegimo problemoms spręsti, pagalba C++ Merkle ir Python skriptų kodui rašyti, regtest žingsniams ir šio README tobulinimui. Rezultatus paleidau ir patikrinau savo kompiuteryje.