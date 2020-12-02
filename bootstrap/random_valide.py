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
import ast

'''
1. Initiate bootstrap with generating random transaction and request randomly assigned node to make take the transactions.
2. Assigned miner will check the length of pending transaction and if the length is over 20, it will mine new block

Task 1. will be executed with multiprocessing, in below case 4 processes.
Task 2. is another processes that keep sending GET request to miner to check and mine new block in given time.
'''
eventlist=[]
def request_transaction(e_time,node_number):
    count = 0
    start_time = time.time()
    generator = eventgenerator.create_event()
    while True:
        now = time.time()
        if now > start_time +e_time:
            break
        np.random.seed(int.from_bytes(os.urandom(4), byteorder='little'))
        nt = generator.invoke_event(e_time=e_time,node_number=node_number)
        node = nt[2]
        port = 8000+node
        CONNECTED_NODE_ADDRESS = 'http://127.0.0.1:'+str(port)#+'/'

        term = nt[1]
        correlational_identifier = nt[0]['ci']
        data = nt[0]['data']       

        post_object = {
            'CI': correlational_identifier,
            'term': term,
            'data': data
        }

        # Submit a transaction
        new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)
        print(new_tx_address)
        requests.post(new_tx_address,
                        json=post_object,
                        headers={'Content-type': 'application/json'})

        eventlist.append((nt[0],nt[1],nt[2]))

    eventlistname = './time'+str(e_time)+'_Nodes_'+str(node_number)+'_evnet_list.json'
    with open(eventlistname,'w') as f:
        for line in eventlist:
            f.write(str(line))
            f.write('\n')

def repeat_request_transaction(): 
    # Replicate random transaction with event_list.json file.
    # Just read json file and request transaction in line by line

    count = 0
    start_time = time.time()
    
    with open('./N20_NC10_SC10/time60_Nodes_20_evnet_list.json','r') as f:
        lines = f.readlines()
        now = time.time()

        for line in lines:
            nt = ast.literal_eval(line)
            node = int(nt[2])
            port = 8000+node
            

            CONNECTED_NODE_ADDRESS = 'http://127.0.0.1:'+str(port)+'/'

            term = nt[1]
            correlational_identifier = nt[0]['ci']
            data = nt[0]['data']       

            post_object = {
                'CI': correlational_identifier,
                'term': term,
                'data': data
            }
            

            # Submit a transaction
            new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

            requests.post(new_tx_address,
                            json=post_object,
                            headers={'Content-type': 'application/json'})    
                    
def whois_mining(miner):
    miner = 8000+miner
    
    CONNECTED_NODE_ADDRESS = 'http://127.0.0.1:'+str(miner)+'/'
    print(CONNECTED_NODE_ADDRESS)
    permit_minig = "{}/mining_right".format(CONNECTED_NODE_ADDRESS)
    requests.get(permit_minig)

if __name__=='__main__':

    e_time = 60
    node_number = 20
    miner =3

    processes =1

    whois_mining(miner)
    # request_transaction(e_time,node_number)
    
    repeat_request_transaction()
