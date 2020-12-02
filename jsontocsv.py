import bson
import json
import csv
import pandas as pd
import os 

folders = ['Y_N5_NC_10_SC10', 'Y_N20_NC10_SC2', 'N_N20_NC2_SC10', 'Y_N20_NC_10_SC10', 'N_N5_NC2_SC10', 'N_N5_NC2_SC2', 'N_N20_NC10_SC2', 'N_N5_NC10_SC10', 'Y_N20_NC2_SC10', 'Y_N5_NC10_SC2', 'Y_N5_NC2_SC2', 'N_N20_NC2_SC2', 'Y_N5_NC2_SC10', 'N_N20_NC_10_SC10', 'Y_N20_NC2_SC2', 'N_N5_NC10_SC2']
print(len(folders))

for d in folders:
    dirname = './pythonblockchainapp/mongodb/'+d
    filename = '/output.json'
    
    dictarr =[]
    with open(dirname+filename,'rb') as f:
        for k in f:
            dictarr.append(json.loads(k))
    # print(json.loads(t))

    df = pd.DataFrame(dictarr)
    print(df.columns.values)
    # dfname = dirname+'/output.csv'

    # df.to_csv(dfname,index=False)
