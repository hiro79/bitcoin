#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test multiwallet.

Verify that a bitcoind node can load multiple wallet files
"""
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, assert_raises_jsonrpc

class MultiWalletTest(BitcoinTestFramework):

    def __init__(self):
        super().__init__()
        self.setup_clean_chain = True
        self.num_nodes = 1
        self.extra_args = [['-wallet=w1', '-wallet=w2', '-wallet=w3']]

    def run_test(self):
        w1 = self.nodes[0] / "wallet/w1"
        w1.generate(1)

        # accessing wallet RPC without using wallet endpoint fails
        assert_raises_jsonrpc(-32601, "Method not found", self.nodes[0].getwalletinfo)

        # check w1 wallet balance
        w1_info = w1.getwalletinfo()
        assert_equal(w1_info['immature_balance'], 50)
        w1_name = w1_info['walletname']
        assert_equal(w1_name, "w1")

        # check w1 wallet balance
        w2 = self.nodes[0] / "wallet/w2"
        w2_info = w2.getwalletinfo()
        assert_equal(w2_info['immature_balance'], 0)
        w2_name = w2_info['walletname']
        assert_equal(w2_name, "w2")

        w3 = self.nodes[0] / "wallet/w3"
        w3_name = w3.getwalletinfo()['walletname']
        assert_equal(w3_name, "w3")

        assert_equal({"w1", "w2", "w3"}, {w1_name, w2_name, w3_name})

        w1.generate(101)
        assert_equal(w1.getbalance(), 100)
        assert_equal(w2.getbalance(), 0)
        assert_equal(w3.getbalance(), 0)

        w1.sendtoaddress(w2.getnewaddress(), 1)
        w1.sendtoaddress(w3.getnewaddress(), 2)
        w1.generate(1)
        assert_equal(w2.getbalance(), 1)
        assert_equal(w3.getbalance(), 2)

if __name__ == '__main__':
    MultiWalletTest().main()
