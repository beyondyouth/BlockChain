'''
Author: dong.zhili
Date: 2020-11-03 14:21:56
LastEditTime: 2020-11-10 16:49:44
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /BlockChain/src/main.py
'''
import argparse
import os

from blockchain import blockchain
from transaction import *

if __name__ == '__main__':
    # 定义一个区块链数组
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l", "--listblock", help="print all the blocks of the blockchain", action="store_true")
    parser.add_argument("-g", "--genesisblock",
                        help="create the genesis block, and reward to address")
    parser.add_argument(
        "-s", "--send", help="send xx BTC from xx to xx", type=float)
    parser.add_argument("-F", "--FROM", help="send xx BTC from xx to xx")
    parser.add_argument("-T", "--TO", help="send xx BTC from xx to xx")
    parser.add_argument("-q", "--query", help="query xx's vaild BTC")
    parser.add_argument(
        "--clean", help="remove the blockchain database file", action="store_true")

    args = parser.parse_args()
    if args.listblock:
        bc = blockchain()
        for h, b in bc.BlockChainDB.items():
            print("Prev. hash: %x\n", b.PrevBlockHash)
            print("Hash: %x\n", b.Hash)

    if args.genesisblock:
        txs = []
        bc = blockchain()
        tx = newCoinbaseTX(args.genesisblock)
        txs.append(tx)
        bc.addGenesisBlock(txs)

    if args.send:
        # 构造一次交易，并将该交易保存到新的区块中
        if args.FROM and args.TO:
            amount = args.send
            txs = []
            bc = blockchain()
            tx = newNormalTX(args.FROM, args.TO, amount, bc)
            if None is tx:
                print("new UXTO failed!")
                os._exit()
            txs.append(tx)
            bc.addBlock(txs)
            print("success")

    if args.query:
        address = args.query
        bc = blockchain()
        balance = bc.getAvailableBalance(address)
        print("Balance of '%s': %.2f" % (address, balance))

    if args.clean:
        if os.path.exists(blockchain.DbFile):
            os.remove(blockchain.DbFile)

    # bc.verifyBlockChain()
    # cli = cli()
        # cli.run()
