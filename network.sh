#!/bin/sh
#
#This shell script is to control blockchain mockup network.
#If the argument is up, script will clean the settings and start new network
#If the argument is down, script will close the network
#If the argument is connect, script will connect each node.


DIR='./mongodb/data/'
MODE=$1

if [ -z "$2" ];
    then
        echo "Default node number is 5"
        Node_number = 5        
else
    Node_number=$2
    echo "Node number is $Node_number"
fi


if [ "$MODE" = "up" ]; then
    if [ "$(ls -A $DIR)" ]; then
        echo "Take action $DIR is not Empty"
        sudo rm -rf $DIR
        mkdir $DIR
        echo "Erase all files in $DIR"
    else
        echo "DIR is already empty"
    fi
    echo '\n'
    echo "Generate random network"
    cd python_blockchainapp
    chmod +x networkgenerate.py
    python3 networkgenerate.py -n $Node_number

    echo '\n'
    echo "Docker network up"
    cd ..
    docker-compose up -d --build

elif [ "$MODE" = "down" ]; then
    docker-compose down

elif [ "$MODE" = "connect" ]; then
#     docker exec -it pythonblockchainapp_node1_1 /bin/bash
    echo '\n'
    echo "Connect each nodes according to random network"
    cd python_blockchainapp
    sh ./flaskapp.sh

fi
