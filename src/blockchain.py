'''
Author: dong.zhili
Date: 2020-11-03 14:21:56
LastEditTime: 2020-11-10 16:49:22
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /BlockChain/src/blockchain.py
'''
import os
import pickle

from block import block
from transaction import *


class blockchain(object):
    """
    区块链类
    """

    DbFile = "blockchain.pickle"

    def __init__(self):
        """
        构造函数
        从数据库文件中读取self.BlockChainDB字典；若不存在则在空的self.BlockChainDB中添加一个创世区块
        """
        # BlockChain是一个字典结构，键是block的hash，值是block对象
        self.BlockChainDB = {}
        self.tip = None
        
        if os.path.exists(self.DbFile) and os.path.getsize(self.DbFile) > 0:
            with open(self.DbFile, "rb+") as f:
            # 两个字典，一个blocks，一个chainstate
                self.BlockChainDB = pickle.load(f)
        else:
            # 如果读不到数据库文件
            print("no existing blockchain found. You need creating a new one...")
            return
            # 造创世区块
            # self.addGenesisBlock()
        
        # tip保存最后一个块的哈希值
        self.tip = list(self.BlockChainDB.keys())[-1]
    
    def addGenesisBlock(self, TXs):
        """
        在空的区块链中添加一个创世区块
        """
        b = block("".encode("utf-8"), TXs)
        self.BlockChainDB[b.Hash] = b
        with open(blockchain.DbFile, "wb+") as f:
            # 将创世区块写入到数据库文件
            f.seek(0, 0)
            f.truncate()
            pickle.dump(self.BlockChainDB, f)
        self.tip = b.Hash

    def addBlock(self, TXs):
        """
        在区块链的最后添加一个普通区块
        参数：交易
        """
        with open(blockchain.DbFile, "rb+") as f:
            self.BlockChainDB = pickle.load(f)
            prevblock = self.BlockChainDB[self.tip]
            b = block(prevblock.Hash, TXs)
            self.BlockChainDB[b.Hash] = b
            # print(self.BlockChainDB)
            # 调整文件指针到文件头，并清空文件
            f.seek(0, 0)
            f.truncate()
            pickle.dump(self.BlockChainDB, f)
        self.tip = b.Hash
    
    def verifyBlockChain(self):
        """
        从尾到头验证区块的hash是否成链
        """
        # prevblockhash = self.BlockChainDB[self.tip]['PrevBlockHash']
        key = self.tip

        while self.BlockChainDB[key].Transaction != "Genesis Block":
            if self.BlockChainDB[key].PrevBlockHash != self.BlockChainDB[self.BlockChainDB[key].PrevBlockHash].Hash:
                print("there is a error block")
                return False
            # 记录当前轮次的prevblockhash给下一轮使用
            key = self.BlockChainDB[key].PrevBlockHash
        return True

    def findUnspendableTXs(self, address):
        """
        在区块链上查找携带有未花费的收入的交易，并整理成列表返回
        """
        # 字典记录链上未花费的收入的交易，键值对为（交易ID，交易对象）
        unspentTXs = {}
        for h, b in self.BlockChainDB.items():
            for tx in b.Transactions:
                # 遍历交易的输出，找到所有收入，这个交易我可能在后面花掉，需要过滤
                for i, TXout in enumerate(tx.TXOutputs):
                    if isToAddress(TXout, address):
                        unspentTXs[tx.ID] = tx
                # 过滤时直接跳过Coinbase交易
                if tx.isCoinbase():
                    break
                # 遍历tx.TXInputs找已经花费的收入
                for TXin in tx.TXInputs:
                    if isFromAddress(TXin, address):
                        # 如果这个交易的支付者是address，则该交易的输入的txid指向的收入已经被花费
                        del unspentTXs[TXin['TXid']]
        return unspentTXs.values()
    
    def findUnspendableTXOs(self, address):
        """
        返回未被花费的收入列表
        """
        UTXOs = []
        unspendTXs = self.findUnspendableTXs(address)

        for tx in unspendTXs:
            for TXout in tx.TXOutputs:
                if isToAddress(TXout, address):
                    UTXOs.append(TXout)
        return UTXOs

    def getAvailableBalance(self, address):
        """
        返回可用余额
        """
        balance = 0.0
        unspendTXs = self.findUnspendableTXs(address)

        for tx in unspendTXs:
            for TXout in tx.TXOutputs:
                if isToAddress(TXout, address):
                    balance += TXout['Value']
        return balance
