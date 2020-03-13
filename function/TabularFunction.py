# coding=utf-8

'''
Created on 09 mag 2017

@author: Andrea Montanari

Tabular Function, implementation of abstract Function Evaluator.
Used for discrete functions.
This class manages the cost functions and the maximization/minimization
'''
import pdb
import sys, os
from decimal import Decimal

from collections import OrderedDict

import time

sys.path.append(os.path.abspath('../function/'))
sys.path.append(os.path.abspath('../misc/'))

from FunctionEvaluator import FunctionEvaluator


class TabularFunction(FunctionEvaluator):
    '''
        Correspondence between parameters and function values.
        The parameters are nodeVariables and the values are costs [NodeVariable -> cost]
    '''
    costTable = OrderedDict()

    '''
        list of parameters of cost function (NodeVariables)
    '''
    parameters = list()
    
    report = ""
    
    def __init__(self):
        self.parameters = list()
        self.costTable = OrderedDict()
        
        self.report = ""
        
    def setReport(self, report):
        self.report = report
        
    def getReport(self):
        return self.report    
                    
        
    def addParametersCost(self, params, cost):
        '''
            params: key of cost function (list of NodeVariables)
            cost: cost function with params
            Saves the function value for NodeArgument[] of parameter.
            The params become the key of the cost table. 
        '''
        self.costTable[params] = cost
        
        
    def getCostTable(self):
        return self.costTable
                

    def entryNumber(self):
        '''
            How much values does this function have?
        '''
        return len(self.costTable)
    
    def getCostValues(self):
        '''
            returns the costs of table
        '''
        return self.costTable.values()
    
    def clearCosts(self):
        '''
            clears the cost function
        '''
        self.costTable = OrderedDict()
        
    
    def evaluateMod(self, modifierTable):
        '''
            params: parameters to evalute
            modifierTable: cost function
            This method evaluates the function when a list of qmessages are given
        '''
        sumQmessages = OrderedDict()  
        
        if(len(modifierTable) == 1):
            
            messageq = (modifierTable.keys())[0]
                    
            for i in range(len(modifierTable[messageq])):
                
                sumQmessages[i] = (modifierTable[messageq])[i]

        return sumQmessages
    
    
    def maximizeWRT(self, x, modifierTable):
        '''
            x: variable respect to maximize
            modifierTable: cost function
            calls the maximization function
        '''
        return self.maxminWRT("max", x, modifierTable)


    def minimizeWRT(self, x, modifierTable):
        '''
            x: variable respect to minimize
            modifierTable: cost function
            calls the minimization function
        '''
        return self.maxminWRT("min", x, modifierTable)
    
    
    def maxmin(self, op, maxes, functionArgument, x, xIndex, modifierTable, sumQmessages):   
        '''
            op: max/min
            maxes: actual maxes about variable
            functionArgument: actual parameters
            x: variable to maximize
            xIndex: index of x in cost function
            modifierTable: cost function
            Calculates the maxes with functionArgument respect x
        '''
        #pdb.set_trace()		
        costQ = 0
        
        qIndex = 0
        
        '''
            binary function
        '''
        if(self.parametersNumber() == 2):
            if(xIndex == 0):
                qIndex = 1
            else:
                qIndex = 0  
                
        for xParamIndex in range(x.size()):
            
            costQ = 0
            
            functionArgument[xIndex] = xParamIndex
            
            '''            
               NOW it's pretty ready
               this is the part where it is maximized
            '''
            if(len(modifierTable) == 0):
                cost = self.evaluate(self.functionArgument(functionArgument))
            else:
                costQ = sumQmessages[functionArgument[qIndex]]
                cost = self.evaluate(self.functionArgument(functionArgument)) + costQ
    
            if(op == "max"):
                if (maxes[xParamIndex] < cost):
                    maxes[xParamIndex] = (cost)
            elif(op == "min"):
                if (maxes[xParamIndex] > cost):
                    maxes[xParamIndex] = (cost)

        return maxes
    
    def maxminWRT(self, op, x, modifierTable):
        '''
            op: max/min
            x: variable respect to maximize
            modifierTable: cost function
            Calculates the max value on function respect x
        '''
        #pdb.set_trace()		
        '''
            index of x in function
        '''
        xIndex = self.getParameterPosition(x)     
        
        '''
            number of parameters of f
        '''
        fzParametersNumber = self.parametersNumber()
        
        '''
            at the i-th position there is the number of possible values of 
            the i-th argument of f at the position of x, there will be 
            only one value available
        '''
        numberOfValues = list()
        
        '''
            the array filled with variable value positions that's gonna be evaluated
        '''
        functionArgument = list()
        
        '''
            set to zero functionArgument
        '''
        for i in range(fzParametersNumber):
            functionArgument.append(0)
            
        '''
            maximization array, wrt x possible values
        '''
        maxes = list()
        
        sumQmessages = OrderedDict()
        
        if(len(modifierTable) > 0):
            sumQmessages = self.evaluateMod(modifierTable) 
        
        for index in range(x.size()):
            if(op == "max"):
                maxes.append(float("-inf"))
            elif(op == "min"):
                maxes.append(float("+inf"))
                       
                         
        for i in range(fzParametersNumber):
            numberOfValues.append(self.getParameter(i).size())
            
        numberOfValues[xIndex] = 1
        
        imax = len(numberOfValues) - 1  
        
        i = imax  
                
        while (i >= 0):
            while(functionArgument[i] < (numberOfValues[i] - 1)):                    
                '''
                    calculate the maxes with functionArgument parameters
                '''
                maxes = self.maxmin(op, maxes, functionArgument, x, xIndex, modifierTable, sumQmessages)

                functionArgument[i] = functionArgument[i] + 1                
                
                j = i + 1
                while j <= imax:
                    functionArgument[j] = 0
                    j = j + 1
                
                i = imax
                
            i = i - 1

        '''       
            here an array ready for being evaluated 
            final max value of this cost function
        '''
        maxes = self.maxmin(op, maxes, functionArgument, x, xIndex, modifierTable, sumQmessages)
        
        return maxes 
    
    
    def toString(self):
        ris = "Function evaluator with " + str(self.entryNumber()) + " entries\n"
        ris = ris + "NodeVariable used: " 
        
        for i in range(self.parameters.__len__()):
            ris = ris + str(self.parameters[i].toString()) + " "
            
        ris = ris + "\n"
            
        for entry in self.costTable:
            ris = ris + "[ "
            
            ris = ris + str(entry) + " "
                
            ris = ris + "Value: " + str(self.costTable[entry]) + " ]\n"
         
        return ris       
    
