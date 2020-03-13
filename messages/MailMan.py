# coding=utf-8

'''
Created on 21 apr 2017

@author: Andrea Montanari

This class implements the Post Service in local mode.
It manages: sending and receiving the messages
'''
import pdb
import sys, os
from collections import defaultdict

from collections import OrderedDict

import time

sys.path.append(os.path.abspath('../Graph/'))
sys.path.append(os.path.abspath('../messages/'))

class MailMan:
    
    '''
        interface that permits to create q-message and r-message
    '''
    factory = None
    '''
        list of qmessages
    '''
    qmessages = None
    '''
        list of rmessages
    '''
    rmessages = None
    '''
        Z-Function (sum of qmessages)
    '''
    zmessages = None
    '''
        It contains the average of the differences of the r-messages for each link
        and for each step of the MaxSum 
    '''
    rmessagesAverageDifferenceIteration = OrderedDict()
    
    '''
        R-messages to x
    '''
    messagesRtoX = OrderedDict()
    
    report = ""

    
    def __init__(self, factory):
        '''
            factory: interface that permits to create q-message and r-message
        '''
        self.factory = factory
        self.rmessages = OrderedDict()
        self.qmessages = OrderedDict()
        self.zmessages = OrderedDict()
        
        self.messagesRtoX = OrderedDict()

        self.rmessagesAverageDifferenceIteration = OrderedDict()
        
        self.report = ""
        
    def setReport(self, report):
        self.report = report
        
    def getReport(self):
        return self.report
        
    def setMessagesList(self, qmessages, rmessages):
        '''
            qmessages: list of qmessages
            rmessages: list of rmessages
            Sets the lists with qmessages and rmssages
        ''' 
        self.qmessages = qmessages
        self.rmessages = rmessages
        
    def getAverageIteration(self):
        return self.averageIteration
    
    def getRmessagesAverageDifferenceIteration(self):
        '''
           returns the average of the differences of the r-messages  
        '''
        return self.rmessagesAverageDifferenceIteration
        
    def clearMessagesRtoX(self):
        for x in self.messagesRtoX.keys():
            self.messagesRtoX[x] = list()
    
        
    def sendQMessage(self, x, f, value, iter):
        
        #start_time = time.time()
        
        '''
            x: NodeVariable sender
            f: NodeFunction receiver
            value: Message from variable to function
            Reads the qmessage (x->f) and stores it 
        '''  
        
        '''
            sets sender and receiver of the message
        '''
        value.setSender(x)      
        value.setReceiver(f)  
        
        '''
            retVal is False when actual qmessage is different from the previous one
            else it is True
        '''
        retVal = True#False

        '''
            (x,f) key isn't in the dictionary
        '''        
        if iter == 0:
            
            self.qmessages[(x,f)] = OrderedDict()

            retVal = True
        #else:
            '''
                verify if the mapping has value as a result 
            '''
             #retVal = not(self.equals(self.qmessages[(x,f)], value))
            
        
        # stores the actual qmessage (x->f)
        self.qmessages[(x,f)] = value  
		
        #pdb.set_trace()
                    
        return retVal
                
 
 
    def readQMessage(self, x, f, iter):  
        '''
            x: NodeVariable sender
            f: NodeFunction receiver
            Reads the qmessage (x->f), if there is a new qmessage
            returns it 
        '''                
        if iter == 0:
            return None
        else:       
            return self.qmessages[(x,f)]
        
          
    
    def sendRMessage(self, f, x, value, iter):
        '''
            x: NodeFunction sender
            f: NodeVariable receiver
            value: Message from function to variable
            Reads the rmessage (f->x) and stores it 
        '''  
        
        '''
            sets sender and receiver of the message
        '''
        value.setSender(f)      
        value.setReceiver(x) 
        
        '''
            retVal is False when actual rmessage is different from the previous one
            else it is True
        '''
        retVal = True#False
        
        '''
            c1 key isn't in the dictionary
        '''
        if iter == 0:
            self.rmessages[(f,x)] = OrderedDict()
            self.messagesRtoX[x] = list()
            retVal = True
        #else:
            '''
                verify if the mapping has value as a result 
            '''
            #retVal = not(self.equals(self.rmessages[(f,x)], value))
        
                                                                                
        '''
            calculates the difference between previous rmessage and the actual message sent,
            if it has sent a rmessage previously
        '''
        if((f,x) in self.rmessagesAverageDifferenceIteration.keys()):#if((f in self.rmessages.keys()) & (x in self.rmessages[f])):
            average = self.difference(self.rmessages[(f,x)], value)
        
            '''
                appends the average difference between the messages in this iteration
            '''
            (self.rmessagesAverageDifferenceIteration[(f,x)]).append(average) 
            
        else:                  
            average = 0
            
            self.rmessagesAverageDifferenceIteration[(f,x)] = list()
            '''
                if in the first iteration there isn't a previuos message, recopies 
                the rmessage received
            '''
            for i in range(value.size()):
                average = average + abs(value.getValue(i))
           
            '''
                calculates the average of the difference about this iteration
            '''
            (self.rmessagesAverageDifferenceIteration[(f,x)]).append(average / (value.size()))

        # stores the actual rmessage (f->x)
        self.rmessages[(f,x)] = value        
        
        (self.messagesRtoX[x]).append(value.getContent())

        return retVal
        
        
    def readRMessage(self, f, x, iter):   
        '''
            f: NodeFunction sender
            x: NodeVariable receiver
            Reads the rmessage (f->x), if there is a new rmessage
            returns it 
        '''       
        if iter == 0:
            return None
        else:
            return self.rmessages[(f,x)]
  
        
    def readZMessage(self, x):
        '''
            x: NodeVariable respect to read the value
            Reads the value of x in Z-Function and returns it 
        '''    
        return self.zmessages[x]
    
    def setZMessage(self, x, mc):
        '''
            x: NodeVariable
            mc: MessageContent of x
            Sets the value of x with mc in Z-Function 
        '''    
        #self.report = ""
        
        self.zmessages[x] = mc
        
        #self.report = self.report + "ZFunction of " + str(x.toString()) + self.zmessages[x].toString() + "\n"
          
    
    def getMessageRToX(self, x):
        '''
            x: NodeVariable receiver
            List of message R addressed to x
        '''
        '''print('x:', x.toString())
        
        for key in self.messagesRtoX.keys():
            print('key:', key.toString())
            print('value:', self.messagesRtoX[key])
            
        print('\n')
        
        print(' print(self.messagesRtoX[key])',  self.messagesRtoX[x])'''
          
        return self.messagesRtoX[x]
    
        
        
    #def equals(self, message, mc):
        '''
            message: first Message 
            mc: second Message 
            returns True if they are equal for each value in the message
            else returns false
        '''
        
        '''for i in range(mc.size()):
            if(not(message.getValue(i) == mc.getValue(i))):
                return False'''
            
        #return False 
    
    def difference(self, message, value):  
        '''
            message: first Message
            value: second Message
            returns the average of difference between message and value
        '''
        
        '''
            average of difference
            (previous message - actual message)
        '''
        average = 0
        
        for i in range(message.size()):   
            average = average + (abs(message.getValue(i) - value.getValue(i)))

            
        return (average / (message.size()))
            
        
