import numpy as np
import math  
import time
import pandas as pd

import sys
sys.path.insert(0,'../python_blockchainapp/')
import quality_control


class create_event:
    def __init__(self):
        self.NC=10
        self.SC=10
        self.data_candidates = {1:[]}
        for ci in range(self.NC):
            for x in range(self.SC):
                self.data_candidates[1].append([str(ci+1),str(x+1)])
        self.used_ci_candidates = {}

        self.citerm = {}
        for x in range(self.NC):
            self.citerm[x+1] = [1]
            
    def newevent(self,node_number):
        node = int(np.random.choice(node_number,1)[0])

        ci = int(np.random.choice(self.NC,1)[0]+1)
        # print()
        term =self.citerm[ci][-1]

        if ci not in list(self.used_ci_candidates.keys()):
            self.used_ci_candidates[ci]={}
            self.used_ci_candidates[ci][term] = []
        else:
            if term not in list(self.used_ci_candidates[ci].keys()):
                self.used_ci_candidates[ci][term] = []
            

        while True:
            d = np.random.choice(self.SC,1)[0]+1
            if d not in list(self.used_ci_candidates[ci][term]):
                break

        data = 'd'+str(d)
        d_content = int(math.ceil(np.random.exponential(scale=10,size=1)[0]))
        
        transaction = {'ci':ci,'data':{data:d_content}}

        self.used_ci_candidates[ci][term].append(d)

        if len(self.used_ci_candidates[ci][term])==self.SC:
            self.citerm[ci].append(term+1)
        
        return (transaction,term,node+1)

    def invoke_event(self,e_time,node_number):
        
        start_time = time.time()
        while True:
            now = time.time()
            if now > start_time +e_time:
                break
            return self.newevent(node_number)
            


if __name__ =='__main__':
    qc_checker = {}
    generator = create_event()
    e_time =3
    node_number=5
    # nt = generator.invoke_event(e_time=e_time,node_number=node_number)
    txlist=[]
    for t in range(100):
        nt = generator.invoke_event(e_time=e_time,node_number=node_number)
        txlist.append(nt)

    print(generator.used_ci_candidates)
    # print(txlist)
