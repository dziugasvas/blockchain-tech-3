#include "merkle.h"
#include <iostream>

using std::cout;
using std::endl;
using std::string;
using std::vector;

int passed = 0;
int failed = 0;

void check(const string& name, bool ok) {
    cout << (ok ? "[PASS] " : "[FAIL] ") << name << endl;
    if (ok) passed++;
    else failed++;
}

bool throws(const vector<string>& txids) {
    try {
        merkle_root_rpc(txids);
    } catch (const std::invalid_argument&) {
        return true;
    }
    return false;
}

bc::hash_digest parent(const bc::hash_digest& left, const bc::hash_digest& right) {
    return bc::bitcoin_hash(bc::build_chunk({left, right}));
}

const vector<string> BLOCK_100000 = {
    "8c14f0db3df150123e6f3dbbf30f8b955a8249b62ac1d1ff16284aefa3d06d87",
    "fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4",
    "6359f0868171b1d194cbee1af2f16ea598ae8fad666d9b012c8ed2b79a236ec4",
    "e9a66845e05d5abc0ad04ec80f774a7e585c6e8db975962d069a522137b80c1d"
};
const string ROOT_100000 = "f3e94742aca4b5ef85488dc37c06c3282295ffec960994b2c0d5ac2a25a95766";

int main() {
    bc::hash_digest a = parse_txid(BLOCK_100000[0]);
    bc::hash_digest b = parse_txid(BLOCK_100000[1]);
    bc::hash_digest c = parse_txid(BLOCK_100000[2]);
    bc::hash_digest d = parse_txid(BLOCK_100000[3]);
    bc::hash_digest e = bc::bitcoin_hash(bc::to_chunk(string("penktas lapas")));

    check("Blokas 100000: saknis sutampa su RPC merkleroot", merkle_root_rpc(BLOCK_100000) == ROOT_100000);

    check("1 lapas: saknis yra pats lapas", create_merkle({a}) == a);
    check("2 lapai: SHA256d(a || b)", create_merkle({a, b}) == parent(a, b));
    check("3 lapai: c dubliuojamas", create_merkle({a, b, c}) == parent(parent(a, b), parent(c, c)));
    check("5 lapai: dubliuojama keliuose lygiuose",
          create_merkle({a, b, c, d, e}) == parent(parent(parent(a, b), parent(c, d)), parent(parent(e, e), parent(e, e))));

    bc::data_chunk joined = bc::build_chunk({a, b});
    check("Tevo ivestis tiksliai 64 baitai", joined.size() == 64);

    check("Tuscias sarasas atmetamas", throws({}));
    check("Per trumpas hex (63 simboliai) atmetamas", throws({BLOCK_100000[0].substr(1)}));
    check("Per ilgas hex (66 simboliai) atmetamas", throws({BLOCK_100000[0] + "00"}));
    check("Ne hex simbolis atmetamas", throws({"zz" + BLOCK_100000[0].substr(2)}));

    vector<string> changed = BLOCK_100000;
    changed[2][0] = '7';
    check("Pakeistas lapas -> kita saknis", merkle_root_rpc(changed) != ROOT_100000);

    vector<string> swapped = BLOCK_100000;
    std::swap(swapped[1], swapped[2]);
    check("Sukeisti lapai -> kita saknis", merkle_root_rpc(swapped) != ROOT_100000);

    bc::hash_list notReversed;
    for (const string& txid : BLOCK_100000) {
        bc::hash_digest raw;
        bc::decode_base16(raw, txid);
        notReversed.push_back(raw);
    }
    check("Neapversti baitai -> neteisinga saknis", bc::encode_hash(create_merkle(notReversed)) != ROOT_100000);

    cout << endl << "Is viso: " << passed << " PASS, " << failed << " FAIL" << endl;
    return failed == 0 ? 0 : 1;
}