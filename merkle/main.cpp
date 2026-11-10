#include "merkle.h"
#include <iostream>

using std::cout;
using std::endl;
using std::string;
using std::vector;

int main(int argc, char* argv[]) {
    vector<string> txids;
    string expected;

    if (argc > 1) {
        for (int i = 1; i < argc; i++) {
            txids.push_back(argv[i]);
        }
        cout << "Txid is komandines eilutes: " << txids.size() << endl;
    } else {
        txids = {
            "8c14f0db3df150123e6f3dbbf30f8b955a8249b62ac1d1ff16284aefa3d06d87",
            "fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4",
            "6359f0868171b1d194cbee1af2f16ea598ae8fad666d9b012c8ed2b79a236ec4",
            "e9a66845e05d5abc0ad04ec80f774a7e585c6e8db975962d069a522137b80c1d"
        };
        expected = "f3e94742aca4b5ef85488dc37c06c3282295ffec960994b2c0d5ac2a25a95766";
        cout << "Mainnet blokas 100000 (" << txids.size() << " transakcijos)" << endl;
    }

    try {
        bc::hash_list leaves;
        cout << endl << "Lapai (RPC tvarka -> vidine tvarka):" << endl;
        for (const string& txid : txids) {
            bc::hash_digest leaf = parse_txid(txid);
            leaves.push_back(leaf);
            cout << "  " << txid << endl << "  -> " << bc::encode_base16(leaf) << endl;
        }

        bc::hash_digest root = create_merkle(leaves);
        string rootRpc = bc::encode_hash(root);
        cout << endl << "Saknis vidine tvarka: " << bc::encode_base16(root) << endl;
        cout << "Saknis RPC tvarka:    " << rootRpc << endl;

        if (!expected.empty()) {
            cout << "Laukiama (RPC):       " << expected << endl;
            cout << (rootRpc == expected ? "SUTAMPA" : "NESUTAMPA") << endl;
            return rootRpc == expected ? 0 : 1;
        }
    } catch (const std::exception& e) {
        std::cerr << "Klaida: " << e.what() << endl;
        return 1;
    }
    return 0;
}