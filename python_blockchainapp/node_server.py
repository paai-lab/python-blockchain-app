from hashlib import sha256
import json
import time
import pymongo
from pymongo import MongoClient
from flask import Flask, request,flash
import requests
import copy
import quality_control

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 1

    def __init__(self):
        self.tx_ids = set()
        self.qc_checker={}
        self.unconfirmed_transactions = {}
        self.chain = []
        self.unvalidated_transactions = {}
        self.mining_right=False

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, [], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def proof_of_work(block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_new_transaction(self, transaction):
        tx_hash = sha256(json.dumps(transaction).encode()).hexdigest()
        if tx_hash not in self.tx_ids:
            self.unvalidated_transactions[tx_hash] = transaction
            self.tx_ids.add(tx_hash)
        return transaction

    def tx_validation(self,transaction):

        checking = False
        tx_id = sha256(json.dumps(transaction).encode()).hexdigest()
        SC =10
        if checking:
            qc_id = '%s_%s'%(transaction['CI'],transaction['term'])
            if qc_id not in self.qc_checker:
                record_in_db(transaction=tx_id,activity='Opening quality control',qc_id=qc_id,mode='validation')
                self.qc_checker[qc_id] = quality_control.QualityControl(CI=transaction['CI'],term=transaction['term'])
                self.qc_checker[qc_id].tx_ids =[]

            qc_variable = list(transaction['data'].keys())[0]
            qc_value = transaction['data'][qc_variable]
            record_in_db(transaction=tx_id,activity='Filling quality control',qc_id=qc_id,mode='validation')
            self.qc_checker[qc_id].add_variable(qc_variable,qc_value)
            self.qc_checker[qc_id].tx_ids.append(tx_id)
            
            #Caution!!!
            #Quality checking part
            if len(self.qc_checker[qc_id].data)==SC:
                self.qc_checker[qc_id].update_validation()

            if self.qc_checker[qc_id].validation ==True:
                record_in_db(transaction =self.qc_checker[qc_id].tx_ids,activity='Closing quality control',qc_id=qc_id,mode='validation')
                for txs in self.qc_checker[qc_id].tx_ids:
                    self.unconfirmed_transactions[txs] = self.unvalidated_transactions[txs]
                    del self.unvalidated_transactions[txs]
                return True, self.qc_checker[qc_id].tx_ids, qc_id
        
        else:
            qc_id = '%s_%s'%(transaction['CI'],transaction['term'])
            record_in_db(transaction=tx_id,activity='Transaction validated (without qc)',qc_id=qc_id,mode='validation')
            self.unconfirmed_transactions[tx_id] = self.unvalidated_transactions[tx_id]
            del self.unvalidated_transactions[tx_id]

        return True, None

    def add_validated_transaction(self,transaction):
        """
        Add received transactions from other node which are validated
        """
        tx_hash = sha256(json.dumps(transaction).encode()).hexdigest()
        if tx_hash not in list(self.unconfirmed_transactions.keys()):
            self.unconfirmed_transactions[tx_hash] = transaction

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if self.mining_right ==True:
            if not self.unconfirmed_transactions:
                return False

            last_block = self.last_block

            new_block = Block(index=last_block.index + 1,
                            transactions=self.unconfirmed_transactions,
                            timestamp=time.time(),
                            previous_hash=last_block.hash)

            proof = self.proof_of_work(new_block)
            self.add_block(new_block, proof)

            self.unconfirmed_transactions = {}

            return True


app = Flask(__name__)

# the node's copy of blockchain
blockchain = Blockchain()
blockchain.create_genesis_block()

# the address to other participating members of the network
peers = set()

# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["CI",'term']

    for field in required_fields:
        if not tx_data.get(field):
            print('WHAT', field)
            return "Invalid transaction data", 404

    tx_data["timestamp"] = time.time()
    record_in_db(tx_data,'Transaction initiated')

    add_tx_result = blockchain.add_new_transaction(tx_data)
    record_in_db(add_tx_result,'Transaction in validated')
    announce_new_transaction(add_tx_result)
    blockchain.tx_validation(add_tx_result)
    mine_unconfirmed_transactions()


    return "Success", 201


# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})

@app.route('/peers', methods=['GET'])
def get_peers():
    return json.dumps(list(peers))


# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():

    if len(blockchain.unconfirmed_transactions) >=10:
        result = blockchain.mine()
        if not result:
            return "No transactions to mine"
        else:
            # Making sure we have the longest chain before announcing to the network
            chain_length = len(blockchain.chain)
            consensus()
            if chain_length == len(blockchain.chain):
                tx_in_last_block = blockchain.last_block.transactions
                record_in_db(tx_in_last_block,'Mining new block',mode='block')
                # announce the recently mined block to the network
                announce_new_block(blockchain.last_block)
            return "Block #{} is mined.".format(blockchain.last_block.index)


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.add(node_address)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_chain()


@app.route('/mining_right',methods=['GET'])
def permit_minig():
    if blockchain.mining_right ==True:
        pass
    else:
        blockchain.mining_right =True
    return str(blockchain.mining_right)

@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        # peers.update(response.json()['peers'])
        peers.add(node_address+'/')     #Add other node address to peers
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code

def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # skip genesis block
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain



# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)
    announce_new_block(block)
    if not added:
        return "The block was discarded by the node", 400
    
    else:
        for tx_hash in list(block.transactions.keys()):
            try:
                del blockchain.unconfirmed_transactions[tx_hash]
            except:
                pass

    
    # else:
    #     del blockchain.unconfirmed_transactions[]
    return "Block added to the chain", 201

# endpoint to add new transaction by someone else to own mining pool
@app.route('/add_received_transaction', methods=['POST'])
def add_transaction():
    tx_data = request.get_json()
    tx_data = json.dumps(tx_data,ensure_ascii=False)
    tx_data = eval(tx_data)

    tx_hash = sha256(json.dumps(tx_data).encode()).hexdigest()
    if tx_hash in blockchain.tx_ids:
        added = False
        pass
    else:
        add_tx_result = blockchain.add_new_transaction(tx_data)
        record_in_db(add_tx_result,'Transaction received')
        announce_new_transaction(add_tx_result)
        blockchain.tx_validation(add_tx_result)
        mine_unconfirmed_transactions()
        added = True

    if not added:
        return "Something wrong transaction is not added", 400
    

    return "Block added to the chain", 201

# endpoint to query unconfirmed transactions
@app.route('/pending_tx',methods=['GET'])
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)

@app.route('/unvalidated_tx',methods=['GET'])
def get_unvalidated_tx():
    return json.dumps(blockchain.unvalidated_transactions)


def consensus():
    """
    Our naive consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False

def announce_new_transaction(tx_data):
    """
    A function to announce to the network once a transaction has been transferred.
    Other nodes store the received transaction in the unmined memory
    """
    for peer in peers:
        url = "{}/add_received_transaction".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(tx_data),
                      headers=headers)

def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}/add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)

def record_in_db(transaction,activity,mode='transaction',qc_id=None):
    '''
    Record invoked activity and transaction in database
    mode : default = transaction
    1)transaction
    2)block
    '''
    pass 

    conn = MongoClient('172.28.2.1:27017')
    # conn = MongoClient('127.0.0.1:27017')

    db = conn.blockchaindb
    collect = db.transactions

    if mode =='transaction':
        dbtx = copy.deepcopy(transaction)
        dbtx['Transaction ID'] = sha256(json.dumps(transaction).encode()).hexdigest()
        
        dbtx['Time in DB'] = time.time()
        dbtx['Node'] = 'Node '+ str(port-8000)
        dbtx['activity'] = activity
        collect.insert(dbtx)

    elif mode =='block':
        dbtx={}
        tx_ids = list(transaction.keys())
        dbtx['Transaction ID'] = tx_ids
        dbtx['Time in DB'] = time.time()
        dbtx['Node'] = 'Node '+ str(port-8000)
        dbtx['activity'] = activity
        collect.insert(dbtx)

    elif mode == 'validation':
        dbtx={}
        dbtx['Transaction ID'] = transaction
        dbtx['Time in DB'] = time.time()
        dbtx['Node'] = 'Node '+ str(port-8000)
        dbtx['activity'] = activity
        dbtx['Quality Control ID'] = qc_id
        collect.insert(dbtx)

    return "Success", 201



# Uncomment this line if you want to specify the port number in the code
#app.run(debug=True, port=8000)

if __name__ =='__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0',port=port,debug=True)