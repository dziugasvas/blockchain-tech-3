#include "merkle.h"
#include <stdexcept>

bc::hash_digest parse_txid(const std::string& hex) {
    if (hex.size() != 2 * bc::hash_size) {
        throw std::invalid_argument("txid turi buti 64 hex simboliai, gauta " + std::to_string(hex.size()));
    }

    bc::hash_digest out;
    if (!bc::decode_hash(out, hex)) {
        throw std::invalid_argument("txid turi ne hex simboliu: " + hex);
    }
    return out;
}

bc::hash_digest create_merkle(bc::hash_list merkle) {
    if (merkle.empty()) {
        throw std::invalid_argument("tuscias txid sarasas (tikras blokas visada turi coinbase)");
    }

    while (merkle.size() > 1) {
        if (merkle.size() % 2 != 0) {
            merkle.push_back(merkle.back());
        }

        bc::hash_list next;
        for (size_t i = 0; i < merkle.size(); i += 2) {
            bc::data_chunk concat(2 * bc::hash_size);
            auto writer = bc::make_unsafe_serializer(concat.begin());
            writer.write_hash(merkle[i]);
            writer.write_hash(merkle[i + 1]);
            next.push_back(bc::bitcoin_hash(concat));
        }
        merkle = next;
    }
    return merkle[0];
}

std::string merkle_root_rpc(const std::vector<std::string>& txids) {
    bc::hash_list leaves;
    for (const std::string& txid : txids) {
        leaves.push_back(parse_txid(txid));
    }
    return bc::encode_hash(create_merkle(leaves));
}