'''
Author: dong.zhili
Date: 2020-11-03 14:21:56
LastEditTime: 2020-11-10 16:49:56
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /BlockChain/src/block.py
'''
import hashlib
import pickle
import sys
import time

from transaction import transaction


class block(object):
    """
    区块结构
    Timestamp:当前时间戳，也就是区块创建的时间
    PrevBlockHash:前一个块的哈希，即父哈希
    Hash:当前块的哈希
    Transaction:区块存储交易列表
    Nonce:存储一个递增的数字，用于工作量证明
    """

    def __init__(self, prevblockhash, transactions):
        self.Timestamp = int(time.time())
        self.PrevBlockHash = prevblockhash
        self.Transactions = transactions
        self.Nonce, self.Hash = self.proofOfWork()

    def proofOfWork(self):
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
            data = self.PrevBlockHash + pickle.dumps(self.Transactions) + self.Timestamp.to_bytes(10, 'little') \
                + targetBits.to_bytes(10, 'little') + \
                nonce.to_bytes(10, 'little')
            hashStr = hashlib.sha256(data).hexdigest()
            hashInt = int(hashStr, 16)
            hash = hashStr.encode("utf-8")

            if hashInt < target:
                break
            else:
                nonce = nonce + 1
        return nonce, hash
