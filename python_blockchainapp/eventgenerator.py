import numpy as np
import math

eventgenerated = [(0.2939599250468105, {'sender': 'a', 'receiver': 'b', 'amount': 9, 'CI': 'x4'}), 
                    (0.05130190282329121, {'sender': 'a', 'receiver': 'b', 'amount': 14, 'CI': 'x2'}), 
                    (0.01143017025621135, {'sender': 'a', 'receiver': 'b', 'amount': 13, 'CI': 'x3'}), 
                    (0.5450362925601087, {'sender': 'a', 'receiver': 'b', 'amount': 13, 'CI': 'x1'})]
def eventgenerator(new_events):
    correlational_identifier = ['x1','x2','x3','x4']
    eventorder =[]
    for t in range(4):
        order = np.random.exponential(scale=1,size=1)[0]
        amount = math.ceil(np.random.exponential(scale=10,size=1)[0])
        y = np.random.choice(correlational_identifier,1)[0]
        print(y)
        transaction = {'sender':'a','receiver':'b','amount':amount,'CI':y}
        eventorder.append((order,transaction))
    



def newevent():
    correlational_identifier = ['x1','x2','x3','x4']
    order = np.random.exponential(scale=1,size=1)[0]
    amount = math.ceil(np.random.exponential(scale=10,size=1)[0])
    y = np.random.choice(correlational_identifier,1)[0]
    transaction = {'sender':'a','receiver':'b','amount':amount,'CI':y}
    
    return (order,transaction)
    

if __name__ =='__main__':
    statefullcheck={'x1':0,'x2':0,'x3':0,'x4':0}

    
    event_count = 300
    while event_count >0:
        n_event = eventgenerated.pop()[1]
        eventgenerated.append(newevent())
        sorted(eventgenerated)
        event_count -=1

        statefullcheck[n_event['CI']] += n_event['amount']

        for ci in statefullcheck.keys():
            if statefullcheck[ci] >100:
                print(event_count)
                event_count =0
                break
    print(statefullcheck)
        



    