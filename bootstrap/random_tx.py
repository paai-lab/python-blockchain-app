import pymongo
from pymongo import MongoClient
import eventgenerator
import time
import json
import requests,os 
from bson.json_util import dumps
import multiprocessing
from functools import partial
import numpy as np

'''
1. Initiate bootstrap with generating random transaction and request randomly assigned node to make take the transactions.
2. Assigned miner will check the length of pending transaction and if the length is over 20, it will mine new block

Task 1. will be executed with multiprocessing, in below case 4 processes.
Task 2. is another processes that keep sending GET request to miner to check and mine new block in given time.
'''



conn = MongoClient('127.0.0.1:27017')
# conn.drop_database('blockchaindb')
db = conn.blockchaindb
collect = db.transactions

def request_transaction(e_time):
    count = 0
    start_time = time.time()
    while True:
        now = time.time()
        if now > start_time +e_time:
            break
        np.random.seed(int.from_bytes(os.urandom(4), byteorder='little'))
        nt,node = next(eventgenerator.newevent(3))
        port = 8000+node 
        CONNECTED_NODE_ADDRESS = 'http://127.0.0.1:'+str(port)+'/'

        sender = nt["sender"]
        receiver = nt["receiver"]
        amount = nt["amount"]
        correlational_identifier = nt['CI']

        post_object = {
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        }

        # Submit a transaction
        new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

        requests.post(new_tx_address,
                        json=post_object,
                        headers={'Content-type': 'application/json'})

def keep_mining(e_time,miner):

    miner = 8000+miner
    CONNECTED_NODE_ADDRESS = 'http://127.0.0.1:'+str(miner)+'/'
    get_pending_tx = "{}/pending_tx".format(CONNECTED_NODE_ADDRESS)
    new_mining_address = "{}/mine".format(CONNECTED_NODE_ADDRESS)

    start_time = time.time()
    while True:
        now = time.time()
        if now > start_time +e_time:
            break        
        pending_tx = requests.get(get_pending_tx).content    
        pending_tx_len = len(json.loads(pending_tx))

        if pending_tx_len >=20:
            requests.get(new_mining_address)

if __name__=='__main__':

    e_time = 3
    miner =3

    processes =4
 
    procs =[]
    for number in range(processes):
        proc = multiprocessing.Process(target=request_transaction, name ='Client{}'.format(number+1), args=(e_time,))
        procs.append(proc)
        proc.start()
    proc = multiprocessing.Process(target=keep_mining,name='Miner',args=(e_time,miner,))
    proc.start()
    procs.append(proc)

    for proc in procs:
        proc.join()