'''
Author: dong.zhili
Date: 2020-11-03 14:21:56
LastEditTime: 2020-11-10 16:49:30
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /BlockChain/src/transaction.py
'''

import hashlib
import pickle


def newTxInput(TXid, Vout, Signature, PubKey=None):
    """
    返回一个字典Txin
    TXid: 输入的交易编号
    Vout: 输入的交易的第几项
    Signature: 交易创造者的签名，暂时用地址代替
    PubKey: 交易创造者的地址，暂时为None
    """
    Txin = {}
    Txin['TXid'] = TXid
    Txin['Vout'] = Vout
    Txin['Signature'] = Signature
    Txin['PubKey'] = PubKey
    return Txin


def newTxOutput(Value, PubKeyHash):
    """
    返回一个字典Txout
    Value: 交易多少金额
    PubKeyHash: 支出对象的地址，若后面的某笔交易的Signature与这个值匹配则可以使用这个输出
    """
    Txout = {}
    Txout['Value'] = Value
    Txout['PubKeyHash'] = PubKeyHash
    return Txout


def newCoinbaseTX(_to, amount=10):
    TXins = []
    TXouts = []
    # Coinbase交易没有输入，TxInput采用默认值
    TXin = newTxInput(bytes(0), -1, bytes(0))
    TXout = newTxOutput(amount, _to)
    TXins.append(TXin)
    TXouts.append(TXout)
    return transaction(TXins, TXouts)


def newNormalTX(_from, _to, amount, bc):
    TXins = []
    TXouts = []
    accumulated = 0.0
    unspentTXs = bc.findUnspendableTXs(_from)

    # 创建TXinput列表
    # 采集足额的收入用于创建交易
    for tx in unspentTXs:
        if accumulated >= amount:
            break
        for i, txout in enumerate(tx.TXOutputs):
            if accumulated >= amount:
                break
            if isToAddress(txout, _from) and accumulated < amount:
                accumulated += txout['Value']
                ntxin = newTxInput(tx.ID, i, _from)
                TXins.append(ntxin)

    if accumulated < amount:
        print("ERROR: Not enough funds")
        return None
    # 创建TXoutput列表
    ntxout = newTxOutput(amount, _to)
    TXouts.append(ntxout)
    if accumulated > amount:
        ntxout = newTxOutput(accumulated-amount, _from)
        TXouts.append(ntxout)

    return transaction(TXins, TXouts)


def isToAddress(TXout, address):
    return TXout['PubKeyHash'] == address


def isFromAddress(TXin, address):
    return TXin['Signature'] == address


class transaction(object):
    """
    交易类，实例化就是一个UTXO交易，有id，Vin，Vout
    """

    def __init__(self, TXInputs, TXOutputs):
        self.TXInputs = TXInputs
        self.TXOutputs = TXOutputs
        self.ID = hashlib.sha256(pickle.dumps(
            self)).hexdigest().encode("utf-8")

    def isCoinbase(self):
        """
        判断本交易是否是一个coinbase交易
        """
        return len(self.TXInputs) == 1 and bytes(0) == self.TXInputs[0]['TXid'] and -1 == self.TXInputs[0]['Vout']

# Txid输入来源的交易编号
# Vout输入来源的交易的输出索引
# Signature交易创造者签名
# Pubkey交易创造者的公钥
# TXInput = {
#     'Txid': bytes(0),
#     'Vout': 0,
#     'Signature': bytes(0),
#     'PubKey': bytes(0),
# }

# Value输出多少币
# PubKeyHash输出地址
# TXOutput = {
#     'Value': 0,
#     'PubKeyHash': bytes(0),
# }
