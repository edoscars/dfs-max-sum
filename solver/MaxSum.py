#coding=utf-8

'''
Created on 19 apr 2017

@author: Andrea Montanari

This is the solver module.
It implements the Max Sum Algorithm (max/min)
'''

import time
import sys, os
from decimal import Decimal
import datetime
import pdb

sys.path.append(os.path.abspath('../maxsum/'))
sys.path.append(os.path.abspath('../messages/'))
sys.path.append(os.path.abspath('../operation/'))
sys.path.append(os.path.abspath('../system/'))

from MailMan import MailMan
from MessageFactory import MessageFactory
from Sum import Sum
from Max import Max
from Min import Min
from MSumOperator import MSumOperator


class MaxSum:
    '''
        COP_Instance, Constraint Optimization Problem
    '''
    cop = None
    '''
        PostService to send and retrieve messages. Used by the Nodes.
    '''
    ps = None
    '''
        MaxSum operation: maximization/minimization
    '''
    op = None
    
    report = ""
    
    '''
        the latest value of MaxSum
    '''
    latestValue_start = 0
    '''
        number of iterations of MaxSum
    '''
    iterationsNumber = 300
    '''
        update Z-Function only the end of the algorithm
    '''
    updateOnlyAtEnd = True
    '''
        actual value  of MaxSum
    '''
    actualValue = None
    '''
        Interface that permits to create q-message and r-message
    '''
    mfactory = None
    '''
        MaxSum operator: Max - Sum
    '''
    ms = None
    '''
        Sum operator
    '''
    sum = None
    '''
        list of values found in each iteration of the algorithm
    ''' 
    values = list()
    '''
        location where saving the MaxSum report
    '''
    reportpath = None
    
    lastAverage = -1
	
    average_final = None	
    
    count = 0
	
    howMany = None
    
    def __init__(self, cop, plus_operation, run):
        '''
            cop: COP_Instance, Constraint Optimization Problem
            plus_operation: Sum operator
            reportpath: location where saving the MaxSum report
        '''
        self.reportpath = "MaxSumReport_RUN_" + str(run) + ".txt"  
        self.cop = cop
        self.mfactory = MessageFactory()
        self.ps = MailMan(self.mfactory)
        self.sum = Sum(self.mfactory)
        
        if plus_operation == 'max':
            self.op = Max(self.mfactory)
            self.latestValue_start = float('-inf')
            
        elif plus_operation == 'min':
            self.op = Min(self.mfactory)
            self.latestValue_start = float('+inf')
         
        '''
            create MaxSumOperator: Max - Sum
        '''    
        self.ms = MSumOperator(self.sum, self.op)
        
        self.values = list()
        
        self.lastAverage = -1
        self.count = 0
        self.howMany = ''
        
    def getReport(self):
        return self.report
		
    def howMany(self):
        return self.howMany
    
    def setReport(self, report):
        self.report = report
        
    def getMFactory(self):
        '''
            returns the Interface that permits to create q-message and r-message
        '''
        return self.mfactory
    
    def getRmessagesAverageDifferenceIteration(self):
        '''
            returns the average of difference of rmessages for each link 
            and for each iteration
        '''
        return self.ps.getRmessagesAverageDifferenceIteration() 
        
    def setIterationsNumber(self, iterations):
        '''
            How many steps to do?
        '''
        self.iterationsNumber = iterations
        
    def getCop(self):
        '''
            returns the cop associated to MaxSum
        '''
        return self.cop
    
    def setCop(self, cop):
        '''
            COP: COP_Instance, Constraint Optimization Problem
            Sets COP of MaxSum with cop
        '''
        self.cop = cop
        
    def getValues(self):
        '''
            returns values for each iteration found by MaxSum
        '''
        return self.values
           
    def getActualValue(self):
        '''
            returns the actual value found by MaxSum in this iteration
        '''
        return self.cop.actualValue()
        
    def stringStatus(self, iteration):
        
        status_i = ""
        
        if(iteration >= 0):
            status_i = status_i + "iteration_" + str(iteration) + "="
        else:
            status_i = status_i + "final="
        
        status_i = status_i + self.cop.status()
        
        return status_i
    
    
    def stringToFile(self, string, file):
        '''
            Simple method that stores a String into a file.
        '''
        output_file = open(file, "w")
        output_file.write(string)
        output_file.write("\n")
        output_file.close()
        
    def setUpdateOnlyAtEnd(self, updateOnlyAtEnd):
        '''
            updateOnlyAtEnd: boolean
            It is True if the update functions of algorithm is at End else False
        '''
        self.updateOnlyAtEnd = updateOnlyAtEnd
        
    def getUpdateOnlyAtEnd(self):
        '''
            returns when is updating of functions
            True at end else False 
        '''
        return self.updateOnlyAtEnd
        
     
    def solve_complete(self):  
        '''
            Apply the Max Sum algorithm.
        '''  
        i = 0
        
        '''
            set the postservice
        '''
        self.cop.setPostService(self.ps);
        '''
            set the operator
        '''
        self.cop.setOperator(self.ms);
        
        #self.report = self.report + "==============================================================================================\n\n" 
        
        #self.report = self.report + "\t\t\t\t\t\t\t MAX SUM INIT\n\n"
        
        status = ""
        
        startTime = time.clock()
        
        self.report = self.report + "\n==============================================================================================\n"
        self.report = self.report + "======================   in   solve_complete()   =============================================\n"
        self.report = self.report + "==============================================================================================\n\n" 
        
        
        average = False
        
        while((average == False) and (i < self.iterationsNumber)):
		
            self.report = self.report + "\n\n#######\tITERATION " + str(i) + "\t#######\n\n"
                        
            for agent in self.cop.getAgents():
                
                self.report = self.report + str(datetime.datetime.now())[:23] + "\t\t\t\tAgent: " + str(agent.toString()) + " send Q message\n"

                agent.sendQMessages(i)
               
                agent.sendRMessages(i)
                     
                if(self.updateOnlyAtEnd == False):
                    '''
                        updating in each iteration
                    '''
                    self.report = self.report + "\n"
                    
                    agent.updateZMessages()
                    self.report = self.report + agent.getReport() + "\n\n"
                    
                    agent.updateVariableValue()
                    self.report = self.report + agent.getReport() + "\n"
                    
                    '''
                        updating the actual value of MaxSum
                    '''
                    self.actualValue = self.getActualValue()
                    '''
                        append the value found in this iteration
                    '''
                    self.values.append(self.actualValue)
                          
                    status = self.stringStatus(i + 1)
                    self.report = self.report + status + "\n\n"
                    self.report = self.report + "==============================================================================================\n"
                    self.report = self.report + "==============================================================================================\n"
                    self.report = self.report + "==============================================================================================\n\n"
                                    
                '''
                    calculate the average of diff RMessages in this iteration
                '''
                self.report = self.report + "\n\naverage of diff RMessages in iteration " + str(i) + " is "
                average = self.average(i)
                
                i = i + 1			
        #print("iteration " + str(i))
		
        self.howMany = 'Last iteration: ' + str(i) + '/' + str(self.iterationsNumber)
				
    def average(self,iter):  
            '''
                average of rmessages difference in the instance
            '''
            rMessagesAverageDifference = self.getRmessagesAverageDifferenceIteration()
			            
            '''
                number of link in factor graph
            '''
            links = 0
            
            messages = list()
                          
            for (k1,k2) in rMessagesAverageDifference.keys():
                messages.append(rMessagesAverageDifference[(k1,k2)])

                links = links + 1
                
            sumList = [sum(x) for x in zip(*messages)] 
						                        
            average = (sumList[iter] / links) 
            
            #print('Last average:', self.lastAverage)
            #print('average iteration', iter, ':', average)
			
            self.report = self.report + str(average) + "\n"
            						
            if(average <= 0.05) and (iter >= 2):
                return True
			
            return False

