# __coding:utf8__

'''
@Time : 2021/3/5 13:47 
@Author : Debby
@File : common.py 
@Software: PyCharm
'''

import json, os, time, sys
import urllib2

curPath = os.path.abspath(os.path.dirname(__file__))
# rootPath = os.path.split(curPath)[0]
sys.path.append(curPath)

base_url = "http://192.168.10.100:19334/"
times = 60
fee_limit = 100000000
genesis_source_address = 'adxSp1X4V7hXDDRBKHL6U21CpbPhki7YqjuUd'
genesis_private_key = 'privbtBp152KnunKvCBgFQX96zuASSH6FBY9KVTX1bifPCLUWarq9EaN'

isExists=os.path.exists(curPath+'/test-data')


if not isExists:
    os.makedirs(curPath+'/test-data')
    print '创建成功'


def get_nonce_dic(filename):
    l, a = readFile(curPath + "/test-data/" + filename)
    dict_nonce = {}
    for i in a:
        nonce = getNonce(i.get_address())
        dict_nonce[i.get_address()] = nonce
    return dict_nonce, a

def get_test(baseurl, url):
    urlRequest = baseurl + url
    # print(urlRequest)
    # logger.debug(urlRequest)
    try:
        req = urllib2.Request(urlRequest)
        res_data = urllib2.urlopen(req).read()
        hjson = json.loads(res_data)
        return hjson
    except Exception as err:
        # logger.error('------------')
        # logger.error(err.code)
        print err
        os._exit(0)

    return None

def getkey(baseurl, url, key, value):
    url1 = url + '?' + key + '=' + value
    return get_test(baseurl, url1)


def getNonce(inter_source_address, url=base_url):
    # time.sleep(1)  # 测试增加时延
    accountInfo = getkey(url, 'getAccount', 'address', inter_source_address)
    # logger.debug('accountInfo: \n' + json.dumps(accountInfo, indent=4))
    if accountInfo['error_code'] == 0:
        result = accountInfo['result']
        if "nonce" in result:
            nonce = result['nonce']
        else:
            nonce = 0
        return nonce
    else:

        # logger.error("account ({}) doesn't exist".format(inter_source_address))
        return -1

def items(inter_source_address, inter_private_key_list, inter_fee_limit, inter_operations, inter_nonce, gas_price=1000):
    import random
    # gas_price = getFees("gas_price")
    item_dic = {
        "items": [
            {
                "private_keys": inter_private_key_list,
                "transaction_json": {
                    "fee_limit": inter_fee_limit,
                    "gas_price": gas_price,
                    "nonce": inter_nonce,
                    "operations": inter_operations,
                    "source_address": inter_source_address
                }
            }
        ]
    }
    return item_dic

def getTransactionHistory(hash, url=base_url):
    return getkey(url, "getTransactionHistory", 'hash', hash)

def getErrorCodeByHash(hash, inter_timeout, url=base_url):
    global times
    error_code = getTransactionHistory(hash, url)['error_code']
    while True:
        inter_timeout = int(inter_timeout)
        inter_timeout -= 1
        # logger.debug("inter_timeout: " + str(inter_timeout))
        if error_code == 4:
            time.sleep(0.5)
            transactionHistory = getTransactionHistory(hash, url)
            error_code = transactionHistory['error_code']
            if error_code == 0:
                error_code = transactionHistory['result']['transactions'][0]['error_code']
                error_desc = transactionHistory['result']['transactions'][0][
                    'error_desc']
                return error_code, error_desc, hash
        else:
            transactionHistory = getTransactionHistory(hash, url)
            error_code = transactionHistory['result']['transactions'][0]['error_code']
            error_desc = transactionHistory['result']['transactions'][0]['error_desc']

            return error_code, error_desc, hash
        if inter_timeout == 0:
            if error_code == 0:
                return error_code, "success", hash
            else:
                return error_code, 'failed', hash

def post(baseurl, url, param):
    data = json.dumps(param)
    url = baseurl + url
    try:
        headers = {'Content-Type': 'application/json'}
        request = urllib2.Request(url, data=data, headers=headers)
        response = urllib2.urlopen(request)
        res = response.read()
        # print res
        return json.loads(res)
    except Exception as err:
        print err


def transactions(inter_source_address, inter_private_key, inter_fee_limit, operations, inter_nonce, url=base_url,
                 gas_price=1000):
    if inter_nonce is not None:
        item_dic = items(inter_source_address, inter_private_key, inter_fee_limit, operations, inter_nonce, gas_price)
    else:
        inter_nonce = getNonce(inter_source_address)
        item_dic = items(inter_source_address, inter_private_key, inter_fee_limit, operations, inter_nonce + 1,
                         gas_price);
    result = post(url, 'submitTransaction', item_dic)
    # logger.debug(json.dumps(result, indent=4))
    error_code = result['results'][0]['error_code']
    error_desc = result['results'][0]['error_desc']
    hash = result['results'][0]['hash']
    error_code, error_desc, hash = getErrorCodeByHash(hash, times, base_url)
    # logger.info("error_code: " + str(
    #     error_code) + " error_desc: " + error_desc + " hash: " + hash + ' source_address:' + inter_source_address + ' nonce: ' + str(
    #     inter_nonce))

    return error_code, error_desc, hash

# 删除文件
def deleteFile(file):
    if os.path.exists(file):
        os.remove(file)
    else:
        print('no such file:%s' % file)

# 读取文件内容，转化成账户对象
def readFile(dirPath):

    l = []
    account = []
    with open(dirPath, 'r') as f:
        for line in f:
            # print(line)
            # a = Account(line[0:39], line[40:89], line[90:173])  # bif_main
            # a = Account(line[0:46], line[47:117], line[118:188])   #bubi-v4-a00
            a = Account(line[0:37], line[38:94], line[95:175]) #bubi-v4-adx
            # a = Account(line[0:41], line[42:98], line[99:175])
            # print(line[0:39])
            # print(line[40:89])
            # print(line[90:173])
            # print(line[0:46])
            # print(line[47:117])
            # print(line[118:188])
            account.append(a)
            l.append(line[0:41])

    f.close()
    return l, account

def getNewAccountWritetoFile(filename, mode):
    new_account = get_test(base_url, 'createAccount')
    f = open(curPath + "/test-data//" + filename, mode)
    # with open(rootPath+"\\test-data\\"+filename, mode) as f:
    if new_account is not None:
        address = new_account['result']['address']
        priv = new_account['result']['private_key']
        pub = new_account['result']['public_key']
        f.write(address + ',' + priv + ',' + pub + '\n')
        f.close()
        return address, priv, pub
    else:
        # logger.error('get new account error')
        return None


def getNewAccount():
    return getNewAccountWritetoFile("test_data", 'w+')

def getNewAccountOnly():
    new_account = get_test(base_url, 'createAccount')
    if new_account is not None:
        address = new_account['result']['address']
        priv = new_account['result']['private_key']
        pub = new_account['result']['public_key']
        return address, priv, pub
    else:
        # logger.error('get new account error')
        return None

def getErrorCode(results, inter_timeout, url=base_url):
    global hash
    hash = results['results'][0]['hash']
    if 'results' in results:
        postErrorCode = results['results'][0]['error_code']
        if postErrorCode != 0:
            return postErrorCode, results['results'][0]['error_desc'], hash
    return getErrorCodeByHash(hash, inter_timeout, url)

def transaction(inter_source_address, inter_private_key, inter_fee_limit, operations, check, inter_nonce=None,
                url=base_url):
    if inter_nonce is not None:
        item_dic = item(inter_source_address, inter_private_key, inter_fee_limit, operations, inter_nonce, url)
    else:
        nonce = getNonce(inter_source_address, url)
        item_dic = item(inter_source_address, inter_private_key, inter_fee_limit, operations, nonce + 1, url)
    result = post(url, 'submitTransaction', item_dic)
    hash = result['results'][0]['hash']
    # logger.info('hash: ' + result['results'][0]['hash'])
    # logger.debug('sumbmitTransaction-result: \n' + json.dumps(result, indent=4))
    code = 111111
    desc = 'default'
    if check:
        code, desc, hash = getErrorCode(result, times, url)
        # if code != 0:
        #     logger.error('error_code: ' + str(code) + ', error_desc: ' + desc)
        # elif code == 0 and desc != '':
        #     logger.info('error_code: ' + str(code) + ', error_desc: ' + desc)
        # else:
        #     logger.info('error_code: ' + str(code) + ', error_desc: 交易成功！')
    return code, desc, hash

def item(inter_source_address, inter_private_key, inter_fee_limit, inter_operations, inter_nonce, url=base_url):
    gas_price = 1000
    # gas_price = getFees("gas_price", url)
    item_dic = {
        "items": [
            {
                "private_keys": [
                    inter_private_key
                ],
                "transaction_json": {
                    "fee_limit": inter_fee_limit,
                    "gas_price": gas_price,
                    "nonce": inter_nonce,
                    "operations": inter_operations,
                    "source_address": inter_source_address
                }
            }
        ]
    }
    return item_dic


def oper_create_account(inter_dest_address, inter_init_balance):
    create_account = {
        "init_balance": inter_init_balance,
        "priv": {
            "master_weight": 1,
            "thresholds": {
                "tx_threshold": 1
            }
        }
    }
    if inter_dest_address is None:
        new_address, new_priKey, new_pubKey = getNewAccount()
        import utils.helper as helper
        with open('../test-data/' + helper.getNowTime() + 'user.txt', 'a+') as f:
            f.write(new_address + '-' + new_priKey + '\n')
        f.close()
        print(new_address + '-' + new_priKey)
        create_account.update({"dest_address": new_address})
    else:
        create_account.update({"dest_address": inter_dest_address})
    return {
        "create_account": create_account,
        "type": 1
    }

def getModulesStatus(url=base_url):
    return get_test(url, "getModulesStatus")

def getTransactionSize(url=base_url):
    status = getModulesStatus(url)
    size = status['glue_manager']['transaction_size']
    return size

def create_keypair(tran_size, oper_size, init_balance, filename):
    deleteFile( curPath +"/test-data/" + filename)
    f = open(curPath + "/test-data/" + filename, "a+")
    for i in range(0, tran_size):
        nonce = getNonce(genesis_source_address)
        nonce = nonce + 1
        oper_create_list = []
        account_s = []
        for j in range(0, oper_size):
            new_address, new_priKey, new_pubKey = getNewAccountOnly()
            account_s.append(new_address + ',' + new_priKey + ',' + new_pubKey)
            oper_create_list.append(oper_create_account(new_address, init_balance))
        error_code, error_desc, hash = transactions(genesis_source_address, [genesis_private_key],
                                                    fee_limit * oper_size, oper_create_list, nonce)
        error_code, error_desc, hash = getErrorCodeByHash(hash, times, base_url)
        if error_code == 0 and error_desc == '':
            for i in account_s:
                f.write(i + '\n')
        while error_code == 160:
            time.sleep(5)
            import re
            new_gas = re.findall(r"gas_price\((.+?)\)", error_desc)[0]
            error_code, error_desc, hash = transactions(genesis_source_address, [genesis_private_key],
                                                        fee_limit * oper_size, oper_create_list, nonce)
            error_code, error_desc, hash = getErrorCodeByHash(hash, times, base_url)
            if error_code == 0 and error_desc == '':
                for i in account_s:
                    f.write(i + '\n')
            else:
                print error_code
                print error_desc

    f.close()


class Account:

    def __init__(self, address, private_key, public_key, node=None, pool=None):
        self.address = address
        self.private_key = private_key
        self.node = node
        self.pool = pool
        self.public_key = public_key

    def get_publickey(self):
        return self.public_key

    def get_address(self):
        return self.address

    def get_private_key(self):
        return self.private_key

    def get_node(self):
        return self.node

    def get_pool(self):
        return self.pool
