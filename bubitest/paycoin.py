# __coding:utf8__

'''
@Time : 2021/3/5 14:40
@Author : Debby
@File : paycoin.py
@Software: PyCharm
'''
import time
from common import *

def oper_payCoin(inter_amount, inter_dest_address, inter_input=None):
    return oper_payCoin_source(inter_amount, inter_dest_address, None, inter_input)

def oper_payCoin_source(inter_amount, inter_dest_address, oper_source_address=None, inter_input=None):
    pay_coin = {
        "amount": inter_amount,
        "dest_address": inter_dest_address
    }
    if inter_input is not None:
        pay_coin.update({"input": json.dumps(inter_input)})
    if oper_source_address is not None:
        return {
            "pay_coin": pay_coin,
            "source_address": oper_source_address,
            "type": 7
        }
    else:
        return {
            "pay_coin": pay_coin,
            "type": 7
        }

def pay_bu_batch(addressesString, amount, source_address=genesis_source_address, private_key=genesis_private_key,
                 url=base_url):
    oper_pay_coin = []
    address_list = addressesString.split(',')
    for i in address_list:
        oper = oper_payCoin_source(amount, i)
        oper_pay_coin.append(oper)
    return transaction(source_address, private_key, fee_limit, oper_pay_coin, True, None, url)


def send_multi_to_one(accountlist, dict_nonce, tran_size, oper_size, url=base_url):
    """多对一转账
        文件里的a,b,c,d给创世账号转账  由a->g,b->g,c->g,d->g
    """
    list_a = []
    for i in accountlist:
        list_a.append(i.get_address())
        if dict_nonce[i.get_address()] is not None:
            nonce = dict_nonce[i.get_address()]
        items_list = []
        for j in range(1, tran_size + 1):
            oper_list = []
            for k in range(oper_size):
                oper_list.append(oper_payCoin(0.1, genesis_source_address))
            new_nonce = nonce + j
            trans = {
                "private_keys": [i.get_private_key()],
                "transaction_json": {
                    "fee_limit": fee_limit * oper_size,
                    "gas_price": 1000,
                    "nonce": new_nonce,
                    "operations": oper_list,
                    "source_address": i.get_address()
                }
            }
            items_list.append(trans)
        item_dic = {
            "items": items_list
        }
        results = post(url, 'submitTransaction', item_dic)
        dict_nonce[i.get_address()] = new_nonce
        for j in results['results']:
            error_code = j['error_code']
            error_desc = j['error_desc']
            hash = j['hash']
            # helper.logger.info("error_code: " + str(
            #     error_code) + " error_desc: " + error_desc + " hash: " + hash + ' source_address:' + i.get_address() + ' nonce: ' + str(
            #     nonce - tran_size + 1 + results['results'].index(j)))
            if error_code == 160:
                dict_nonce[i.get_address()] = nonce - 1
                time.sleep(3)
                size = getTransactionSize()
                while size > 30000:
                    # helper.logger.info('too much txs')
                    time.sleep(2)
                    size = getTransactionSize()
                nonce = getNonce(i.get_address())
                dict_nonce[i.get_address()] = nonce

                for k in accountlist:
                    nonce = getNonce(k.get_address())
                    dict_nonce[k.get_address()] = nonce

                break
            if error_code == 99:
                for k in accountlist:
                    nonce = getNonce(k.get_address())
                    dict_nonce[k.get_address()] = nonce
                break
            if error_code == 100:
                accountString = (',').join(list_a)
                # helper.logger.info('begin to pay coin')
                pay_bu_batch(accountString, 100000000000)
                time.sleep(0.5)

            if error_code == 103 :
                os._exit(1)



if __name__ == '__main__':
    filename = 'keypair1.txt'

    dict_nonce, a = get_nonce_dic(filename)
    flag = 0  # 计数，切换url
    tran_size = 50
    oper_size = 100
    # for i in range(2):
    i = 0
    while True:
        print(i)
        send_multi_to_one(a, dict_nonce, tran_size, oper_size)
        i += 1
    pass
