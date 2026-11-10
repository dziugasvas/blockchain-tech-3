#ifndef MERKLE_H
#define MERKLE_H

#include <bitcoin/system.hpp>
#include <string>
#include <vector>

bc::hash_digest parse_txid(const std::string& hex);
bc::hash_digest create_merkle(bc::hash_list merkle);
std::string merkle_root_rpc(const std::vector<std::string>& txids);

#endif