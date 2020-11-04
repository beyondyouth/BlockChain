'''
Author: your name
Date: 2020-11-03 14:21:56
LastEditTime: 2020-11-04 21:42:07
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /lab2.1/src/blockchain.py
'''
import os
import sys
import time
import math
import pickle
import hashlib
from transaction import *

class blockchain(object):
    """
    区块链类
    区块结构
    Timestamp:当前时间戳，也就是区块创建的时间
    PrevBlockHash:前一个块的哈希，即父哈希
    Hash:当前块的哈希
    Data:区块存储的实际有效信息，也就是交易
    Nonce:存储一个递增的数字，用于工作量证明
    """
    def __init__(self):
        # self.temp = {}
        # BlockChain是一个字典结构，键是block的hash，值是block对象
        self.BlockChainDB = {}
        self.DbFile = "blockchain.pickle"
        # self.temp['blocks'] = self.BlockChain
        
        # 从pickle文件读取区块链
        if os.path.exists(self.DbFile) and os.path.getsize(self.DbFile) > 0:
            with open(self.DbFile, "rb+") as f:
            # 两个字典，一个blocks，一个chainstate
                self.BlockChainDB = pickle.load(f)
        else:
            # 如果读不到数据库文件
            print("no existing blockchain found. Creating a new one...")
            # 造创世区块
            self.newGenesisBlock()
            with open(self.DbFile, "wb+") as f:
                # 将创世区块写入到数据库文件
                pickle.dump(self.BlockChainDB, f)
        # tip保存最后一个块的哈希值
        self.tip = list(self.BlockChainDB.keys())[-1]
    
    def proofOfWork(self, b):
        """
        工作量证明
        参数：区块
        返回：nonce和hash
        """
        targetBits = 18
        target = 1 << (256 - targetBits)
        hashInt = None
        nonce = 0
        data = None
        # 不断递增nonce并计算哈希，直到符合条件
        for nonce in range(sys.maxsize):
            data = b['PrevBlockHash'] + b['Data'].encode("utf-8") + b['Timestamp'].to_bytes(10, 'little') \
                + targetBits.to_bytes(10, 'little') + nonce.to_bytes(10, 'little')
            hashStr = hashlib.sha256(data).hexdigest()
            hashInt = int(hashStr, 16)
            hash = hashStr.encode("utf-8")
            
            if hashInt < target:
                print(hash)
                break
            else:
                nonce = nonce + 1
        b['Nonce'] = nonce
        b['Hash'] = hash
    
    def newGenesisBlock(self):
        """
        在空的区块链中添加一个创世区块
        """
        block = {
            'Timestamp': int(time.time()),
            'PrevBlockHash': "".encode("utf-8"),
            'Hash': None,
            'Data': "Genesis Block",
            'Nonce': 0,
        }
        self.proofOfWork(block)
        self.BlockChainDB[block['Hash']] = block

    def addBlock(self, data):
        """
        在区块链的最后添加一个普通区块
        参数：交易
        """
        with open(self.DbFile, "rb+") as f:
            self.BlockChainDB = pickle.load(f)
            prevblock = self.BlockChainDB[self.tip]
            block = {
                'Timestamp': int(time.time()),
                'PrevBlockHash': prevblock['Hash'],
                'Hash': None,
                'Data': data,
                'Nonce': 0,
            }
            self.proofOfWork(block)
            self.BlockChainDB[block['Hash']] = block
            print(self.BlockChainDB)
            # 调整文件指针到文件头，并清空文件
            f.seek(0, 0)
            f.truncate()
            pickle.dump(self.BlockChainDB, f)
        self.tip = block['Hash']
    
    def verifyBlockChain(self):
        """
        从尾到头验证区块的hash是否成链
        """
        # prevblockhash = self.BlockChainDB[self.tip]['PrevBlockHash']
        key = self.tip

        while self.BlockChainDB[key]['Data'] != "Genesis Block":
            if self.BlockChainDB[key]['PrevBlockHash'] != self.BlockChainDB[self.BlockChainDB[key]['PrevBlockHash']]['Hash']:
                print("there is a error block")
                return False
            # 记录当前轮次的prevblockhash给下一轮使用
            key = self.BlockChainDB[key]['PrevBlockHash']
        return True

if __name__ == '__main__':
    # 定义一个区块链数组
    bc = blockchain()

    bc.addBlock("Send 1 BTC to Ivan")
    bc.addBlock("Send 2 more BTC to Ivan")

    for h,b in bc.BlockChainDB.items():
        print("Prev. hash: %x\n", b['PrevBlockHash'])
        print("Data: %s\n", b['Data'])
        print("Hash: %x\n", b['Hash'])
    
    bc.verifyBlockChain()
    