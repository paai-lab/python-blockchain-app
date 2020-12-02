# Purpose of this project

**To test performance of transaction validation function in simple blockchain environment**  
With modifying below code<sup>[1](#footnote_1)</sup> 

### _What changes_

1. Implement transaction validation method
2. Modify web application
3. Write dockerfile and docker-compose configure file to simply generate multiple node in virtual network 
   for test case
4. Generate random network with given number of nodes and connection probability for bootstrp
5. Make event generator to request assigned node to perform as intended in scenario
6. Use Mongodb to record transactions and activity and export the database in json format

## Update history
2020.06.08

- Quality control function file is uploaded which is python class for convenience in checking validation
- Event generator is changed. Now 'sender','receiver','amount' are deleted. CI and d1,or d2 will be generated
- Now transaction is transferred to other node immediately when it is created. Each nodes will validate transactions
- New events 'Opening quality control','Filling quality control', and 'Closing qualtiy control' will be recorded in mongodb
- 'repeat_request_transaction' function is created in random_valide.py file, which to replicate previously generated transaction 
in 'request_transaction'only to check performance by reading event_list.json file.


2020.06.01

- Now mongodb will record, 'Transaction initiated', 'Transaction validated', 'Validated transaction received', and 'Mining new block'.
- Shell script network.sh is uploaded, it is for control network in simple way
- To start random transaction generation, execute random_tx.py in bootstrap.
- random_tx.py will generate and request node with random transaction in multiple processes.
- Assigned miner node will keep mining until transaction generation ends with given condition ex)if length of pending_tx is over 20

2020.05.25

- Upload how to use mongodb and connect blockchain node with mongodb
- The generated transactions which pass the validation process will be recorded in mongodb
- The database is 'blockchaindb' and collection is 'transactions'.
- After recording transaction in given amount of time, export collection in json formation 'output.json'
- Since container mongodb has volume in ./mongodb/data, exported file 'output.json' is also there

2020.04.23

- Upload 'networkgenerate.py' file which makes connected random network with given n nodes and probability 2* ln(n)/n and also saves graph as 'networkstructure.png' file.
- After generating random network, it makes shell script 'testscript.sh' for connecting nodes that follow generated random network edges. Send post request with curl
- Upload 'eventgenerator.py' file which generates random transaction with given array of correlation identifier.
  
2020.04.21

- All node/containers have own fixed ip. The information is in the containerip.txt file
- Even indirectly connected nodes share validated transactions in unconfirmed_transaction proprety.
- New blockchian class property, unvalidated_transaction stores transactions that don't pass the validation check.
- After mined in unspecified node, transactions in mined block will be removed in unconfirmed_transaction property in all nodes.
- New method, **tx_validation**, transaction validation function will validate transaction.
ex) Transaction has three items, 'sender', 'receiver', 'amount'.
validation condition : If the amount sum of transactions in unvalidated_transaction is over 100, transactions will be validated and transferred to unconfirmed_transaction. This function return hash list of validated transactions. 

```python
def tx_validation(self):
  summation = 0
  validated_tx_list =[]
  for tx_key,tx_value in list(self.unvalidated_transactions.items()):
      validated_tx_list.append(tx_key)
      summation += float(tx_value[u'amount'])
      if summation >100:
          return True, validated_tx_list

  return False, None
```

- In webapp transaction page, Chain list, pending transaction(Transaction waiting to be mined), unvalidated transaction(Transaction to be validated) are presented

2020.04.18

- Change node connecting system from host and clinet to peer to peer.
- Implement function to connect two node in web app

- Modify add_transaction function with announce new transaction to peers

## Need to be

- Attach comment and explanation in all API and method in code.
- Think about the name of activities when each nodes is invoked in different process
- Need to make shell script to control launching and testing environment

## Brief description

```
📦pythonblockchainapp
 ┣ 📂backup
 ┃ ┗ 📜docker-compose.yml
 ┣ 📂bootstrap
 ┃ ┣ 📂__pycache__
 ┃ ┃ ┗ 📜eventgenerator.cpython-36.pyc
 ┃ ┣ 📜eventgenerator.py
 ┃ ┣ 📜eventgenerator.pyc
 ┃ ┣ 📜evnet_list.json
 ┃ ┣ 📜random_tx.py
 ┃ ┣ 📜random_valide.py
 ┃ ┗ 📜readjson.py
 ┣ 📂mongodb
 ┃ ┣ 📂data
 ┃ ┃ ┗ 📜output.json
 ┃ ┣ 📜dockerfile
 ┃ ┣ 📜howtouse.md
 ┃ ┣ 📜output_withoutqc.json
 ┃ ┗ 📜output_withqc.json
 ┣ 📂python_blockchainapp
 ┃ ┣ 📂compose
 ┃ ┃ ┗ 📂webapp
 ┃ ┃ ┃ ┗ 📜Dockerfile-node
 ┃ ┣ 📂screenshots
 ┃ ┃ ┣ 📜1.png
 ┃ ┃ ┣ 📜2.png
 ┃ ┃ ┗ 📜3.png
 ┃ ┣ 📂webapp
 ┃ ┃ ┣ 📂app
 ┃ ┃ ┃ ┣ 📂templates
 ┃ ┃ ┃ ┃ ┣ 📜base.html
 ┃ ┃ ┃ ┃ ┣ 📜index.html
 ┃ ┃ ┃ ┃ ┗ 📜transaction.html
 ┃ ┃ ┃ ┣ 📜__init__.py
 ┃ ┃ ┃ ┣ 📜requirements.txt
 ┃ ┃ ┃ ┗ 📜views.py
 ┃ ┃ ┣ 📜Dockerfile
 ┃ ┃ ┣ 📜flaskapp.sh
 ┃ ┃ ┣ 📜requirements.txt
 ┃ ┃ ┗ 📜run_app.py
 ┃ ┣ 📜Dockerfile
 ┃ ┣ 📜bootstrap.sh
 ┃ ┣ 📜eventgenerator.py
 ┃ ┣ 📜flaskapp.sh
 ┃ ┣ 📜networkgenerate.py
 ┃ ┣ 📜networkstructure.png
 ┃ ┣ 📜node_server.py
 ┃ ┣ 📜quality_control.py
 ┃ ┗ 📜requirements.txt
 ┣ 📜.env
 ┣ 📜README.md
 ┣ 📜docker-compose.yml
 ┗ 📜network.sh
```
'app' directory : Webapp flask template directory consists of html files and views&#46;py   
'compose' directory : Containes docker configuration file to build node image and webapp image

'networkgenerate&#46;py' :

- Random network generator with given parameter '-n' as number of nodes by networkx 'Erdős–Rényi'.  
- From generated network, write docker-compose.yml file to build virtual network, bootstrap.sh and flaskapp.sh shell script to command run docker and connect blockchain nodes with edges in random network.  

'eventgenerator&#46;py' : Python file that randomly generates transactions to request assigned nodes to execute.  
'docker-compose.yml' : Docker compose configuration file that generates blockchain node containers and webapp container.  
'Dockerfile' : Dockerfile is for build blockchain node image.  
'bootstrap&#46;sh' : Shell script to run docker-compose  
'flaskapp&#46;sh' : Shell script that contains post request to connect to different node containers in rest api
'networkstructure.png' : Random network graph image file genertaed from 'networkgenerate&#46;py'
'node_server&#46;py' : Blockchain code with flask rest api, used for making docker 'node' image.
'requirements.txt' : Required python packages to build node and webapp image.
'run_app&#46;py' : Webapp python file with flask and rest api  

---

# python_blockchain_app<a name="footnote_1">1</a>

A simple tutorial for developing a blockchain application from scratch in Python.

## What is blockchain? How it is implemented? And how it works?

Please read the [step-by-step implementation tutorial](https://www.ibm.com/developerworks/cloud/library/cl-develop-blockchain-app-in-python/index.html) to get your answers :)

## Instructions to run

Clone the project,

```sh
$ git clone https://github.com/satwikkansal/python_blockchain_app.git
```

Install the dependencies,

```sh
$ cd python_blockchain_app
$ pip install -r requirements.txt
```

Start a blockchain node server,

```sh
# Windows users can follow this: https://flask.palletsprojects.com/en/1.1.x/cli/#application-discovery
$ export FLASK_APP=node_server.py
$ flask run --port 8000
```

One instance of our blockchain node is now up and running at port 8000.


Run the application on a different terminal session,

```sh
$ python run_app.py
```

The application should be up and running at [http://localhost:5000](http://localhost:5000).

Here are a few screenshots

1. Posting some content

![image.png](https://github.com/satwikkansal/python_blockchain_app/raw/master/screenshots/1.png)

2. Requesting the node to mine

![image.png](https://github.com/satwikkansal/python_blockchain_app/raw/master/screenshots/2.png)

3. Resyncing with the chain for updated data

![image.png](https://github.com/satwikkansal/python_blockchain_app/raw/master/screenshots/3.png)

To play around by spinning off multiple custom nodes, use the `register_with/` endpoint to register a new node. 

Here's a sample scenario that you might wanna try,

```sh
# Make sure you set the FLASK_APP environment variable to node_server.py before running these nodes
# already running
$ flask run --port 8000 &
# spinning up new nodes
$ flask run --port 8001 &
$ flask run --port 8002 &
```

You can use the following cURL requests to register the nodes at port `8001` and `8002` with the already running `8000`.

```sh
curl -X POST \
  http://127.0.0.1:8001/register_with \
  -H 'Content-Type: application/json' \
  -d '{"node_address": "http://127.0.0.1:8000"}'
```

```sh
curl -X POST \
  http://127.0.0.1:8002/register_with \
  -H 'Content-Type: application/json' \
  -d '{"node_address": "http://127.0.0.1:8000"}'
```

This will make the node at port 8000 aware of the nodes at port 8001 and 8002, and make the newer nodes sync the chain with the node 8000, so that they are able to actively participate in the mining process post registration.

To update the node with which the frontend application syncs (default is localhost port 8000), change `CONNECTED_NODE_ADDRESS` field in the [views.py](/app/views.py) file.

Once you do all this, you can run the application, create transactions (post messages via the web inteface), and once you mine the transactions, all the nodes in the network will update the chain. The chain of the nodes can also be inspected by inovking `/chain` endpoint using cURL.

```sh
$ curl -X GET http://localhost:8001/chain
$ curl -X GET http://localhost:8002/chain
```
