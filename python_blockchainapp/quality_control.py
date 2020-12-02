class QualityControl:
    '''
    This is class for generating new qc checker
    '''
    def __init__(self,CI,term,d1=None,d2=None):
        '''
        CI : Correlation Identifier
        term : Term of CI, beginning with 0
        d1 : Data type 1
        d2 : Data type 2
        '''
        self.CI = CI
        self.term = term
        self.validation = False
        self.data ={}    
    def update_validation(self):
        '''
        Change validation attribute of class
        '''

        self.validation = True

    def add_variable(self,variable,value):
        '''
        Add/update class attributes
        '''
        
        self.data[variable]= value

    def tx_content(self):
        '''
        Print content of the qc
        '''
        return self.__dict__
 