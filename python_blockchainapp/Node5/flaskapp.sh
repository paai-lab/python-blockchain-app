#!/bin/sh

curl -X POST http://172.28.1.1:8001/register_with -H 'Content-Type: application/json' -d '{"node_address": "http://172.28.1.2:8002"}'
curl -X POST http://172.28.1.1:8001/register_with -H 'Content-Type: application/json' -d '{"node_address": "http://172.28.1.5:8005"}'
curl -X POST http://172.28.1.2:8002/register_with -H 'Content-Type: application/json' -d '{"node_address": "http://172.28.1.4:8004"}'
curl -X POST http://172.28.1.2:8002/register_with -H 'Content-Type: application/json' -d '{"node_address": "http://172.28.1.5:8005"}'
curl -X POST http://172.28.1.3:8003/register_with -H 'Content-Type: application/json' -d '{"node_address": "http://172.28.1.4:8004"}'
curl -X POST http://172.28.1.3:8003/register_with -H 'Content-Type: application/json' -d '{"node_address": "http://172.28.1.5:8005"}'
