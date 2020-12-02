# How to use Mongodb in docker container

## What we need
- Launch mongodb in docker container which shares same network
- Communicate with other container to create and store data in database
- Save data in localhost directory in json format

## How to do
Please refer docker-compose.yaml file in project root.  
Mongodb environment setting is recorded in .env file in project root

## Store in localhost
Under mongodb directory in project root, there is /data folder.  
Docker container mongodb will share its files in /data/db/ to localhost's ./mongodb/data directory.

## How to export in JSON format
After start network by command 'docker-compose up -d', access to mongodb container in tty by  
1. 'docker exec -it \<mongodb container name\> /bin/bash'
2. cd /data/db
3. mongoexport -d \<database name> -c \<collection name> -o \<output file name>.json
4. exit
The json file in output file name will be stored in ./mongodb/data


