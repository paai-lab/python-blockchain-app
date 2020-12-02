#!/bin/sh
import networkx 
import matplotlib.pyplot as plt
import math
import oyaml as yaml
from argparse import ArgumentParser
# import subprocess

import os
'''
Erdős–Rényi model
n is number of nodes
Almost every graph in G(n, 2ln(n)/n) is connected.
As n tends to infinity, the probability that a graph on n vertices with edge probability 2ln(n)/n is connected, tends to 1.
https://en.wikipedia.org/wiki/Erd%C5%91s%E2%80%93R%C3%A9nyi_model
'''
parser = ArgumentParser()
parser.add_argument('-n',default=10, type=int, help='Number of nodes')
args = parser.parse_args()

n = args.n
p = 2*math.log(n)/n

graphconnected=True

while graphconnected:
    graph = networkx.generators.random_graphs.erdos_renyi_graph(n,p)
    if networkx.is_connected(graph) == True:
        graphconnected = False

updatingnode = {}
for n in list(graph.nodes()):
    updatingnode[n] = n+1
graph = networkx.relabel_nodes(graph, updatingnode)




with open('../docker-compose.yml') as ymlfile:
    data = yaml.load(ymlfile,Loader=yaml.FullLoader)


for t in list(data['services'].keys()):
    if 'node' in t:
        del data['services'][t]


for nodeindex in range(1,n+2):
    nodename = 'node'+str(nodeindex)
    port = str(8000+nodeindex)+':'+str(8000+nodeindex)
    ipaddress = '172.28.1.%s'%(nodeindex)

    if nodeindex ==1:       
        node = {nodename: 
                        {'build': './python_blockchainapp',
                        'ports': [port], 
                        'command': ["python","node_server.py","-p",str(8000+nodeindex)], 
                        'networks': {'mynet': {'ipv4_address': ipaddress}}}}

    
    else:
        node = {nodename: 
                        {'image': 'pythonblockchainapp_node1', 
                        'ports': [port], 
                        'command': ["python","node_server.py","-p",str(8000+nodeindex)], 
                        'networks': {'mynet': {'ipv4_address': ipaddress}}}}


    data['services'][nodename] = node[nodename]


with open('../docker-compose.yml' ,'w') as ymlfile:
    yaml.dump(data,ymlfile,default_flow_style=False)


edgelist = list(graph.edges())

connectionlist=[]
for fn,tn in edgelist:
    fnip = 'http://172.28.1.'+str(fn)+':'+str(8000+int(fn))+'/register_with'
    tnip = 'http://172.28.1.'+str(tn)+':'+str(8000+int(tn))
    connectionlist.append((fnip,tnip))


with open('./flaskapp.sh','w') as f:
    f.write('#!/bin/sh\n')
    f.write('\n')
    for fnip,tnip in connectionlist:
        request = "curl -X POST "+fnip+" -H 'Content-Type: application/json' -d '{\"node_address\": \""+tnip+"\"}'\n"
        f.write(request)
f.close()

fig = plt.figure(3,figsize=(20,20))
ax= fig.subplots()

networkx.draw(graph,with_labels=True)

ax.set_title('Network Structure',fontsize=20)

pltname = './Node'+str(n+1)+'_networkstructure.png'
plt.savefig(pltname,bbox_inches = "tight")
