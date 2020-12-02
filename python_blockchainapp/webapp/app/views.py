import datetime
import json

import requests
from flask import render_template, redirect, request,flash

from app import app

# The node with which our application interacts, there can be multiple
# such nodes as well.
# CONNECTED_NODE_ADDRESS = ""

posts = []
pending_txs=[]
unvalidated_txs=[]
@app.route('/')
def index():
    return render_template('index.html',
                            title='Node picker',
                            )

@app.route('/connect', methods=['POST'])
def connect_node():
    """
    Endpoint to create a new transaction via our application.
    """
    node_address = request.form["nodeadress_port"]
    # post_object = {
    #     'Node address': node_address
    # }
    global CONNECTED_NODE_ADDRESS
    CONNECTED_NODE_ADDRESS = "http://"+node_address
    print(connect_node)
    
    return redirect('/transaction')

def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for pos, block in enumerate(chain["chain"]):
            if pos ==0:
                pass
            else:
                for tx in list(block["transactions"].values()):
                    tx["index"] = block["index"]
                    tx["hash"] = block["previous_hash"]
                    content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)

def fetch_pendingtx():
    get_pending_tx = "{}/pending_tx".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_pending_tx)
    if response.status_code ==200:
        tx = json.loads(response.content)
        global pending_txs
        pending_txs = tx.values()

def fetch_unvalidatedtx():
    get_pending_tx = "{}/unvalidated_tx".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_pending_tx)
    if response.status_code ==200:
        tx = json.loads(response.content)
        print(tx)
        global unvalidated_txs
        unvalidated_txs = tx.values()


@app.route('/transaction')
def transaction():
    fetch_posts()
    fetch_pendingtx()
    fetch_unvalidatedtx()    
    return render_template('transaction.html',
                           title='YourNet: Decentralized '
                                 'content sharing',
                           posts=posts,
                           pending_txs=pending_txs,
                           unvalidated_txs = unvalidated_txs,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """   
    sender = request.form["sender"]
    receiver = request.form["receiver"]
    amount = request.form["amount"]
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

    return redirect('/transaction')


@app.route('/p2pconnect', methods=['POST'])
def  p2pconnect():
    """
    Connect two different node
    """
    
    node1_address = request.form["node1_address"]
    node2_address = request.form["node2_address"]
    node2_address = "http://"+node2_address
    url = 'http://'+node1_address +'/register_with'
    header = {'Content-Type': 'application/json'}
    data = '{"node_address": "%s"}'%(node2_address)

    response = requests.post(url,headers=header,data=data)

    print(response.status_code)
    print(response.content)
    # if response.status_code == 200:
    #     flash('Two nodes are connected')
    # else:
    #     flash('Please check node address')
    
    return redirect('/')
def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
