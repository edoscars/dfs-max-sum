# coding=utf-8
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pl


import sys, os
from collections import defaultdict
import random
import argparse
import itertools
import math
import pdb

from copy import deepcopy

import time
import Queue
import numpy

sys.path.append(os.path.abspath('../maxsum/'))
sys.path.append(os.path.abspath('../solver/'))
sys.path.append(os.path.abspath('../system/'))
sys.path.append(os.path.abspath('../Graph/'))
sys.path.append(os.path.abspath('../misc/'))
sys.path.append(os.path.abspath('../function/'))

from Agent import Agent
from NodeVariable import NodeVariable
from NodeFunction import NodeFunction
from TabularFunction import TabularFunction
from NodeArgument import NodeArgument
from COP_Instance import COP_Instance
from MaxSum import MaxSum


def main():    
    '''
        invoke the parser that takes parameters from the command line
    '''
    args = getParser()
    '''
        How many iterations?
    '''
    nIterations = args.iterations
    '''
        How many instances? 
    '''   
    nIstances = args.instances
    '''
        file of the factor graph
    '''
    file = args.file
    dire = file[:-2]
    '''
        max/min
    '''
    op = args.op
	
    '''
        Constraint Optimization Problem
    '''
    cop = None 
          
    domain = 0
     
    variables = list()
    functions = list()
    agents = list()
     
    agent = None
     
    finalAssignaments = list()
     
    oldAssignaments = list()
     
    core = None
    
    originalCop = None
    
    actualValue = 0

    '''
        list of all values of RUN for each iteration
    '''
    averageValues = list()
    
    iterations = list()
    
    iterationsInstances = list()
    
    averageValuesInstances= list()

    relations = list()	

    '''
	create directories
    '''
    if not os.path.exists("DFSParallelConditioning/"):
        os.makedirs("DFSParallelConditioning/")
    if not os.path.exists("DFSParallelConditioning/" + dire ):
        os.makedirs("DFSParallelConditioning/" + dire)
    if not os.path.exists("DFSParallelConditioning/"+dire+"/Charts/"):
        os.makedirs("DFSParallelConditioning/"+dire+"/Charts/")
    if not os.path.exists("DFSParallelConditioning/"+dire+"/FactorGraph/"):
        os.makedirs("DFSParallelConditioning/"+dire+"/FactorGraph/")

    dir_charts = "DFSParallelConditioning/"+dire+"/Charts/"
    dir_factorgraph = "DFSParallelConditioning/"+dire+"/FactorGraph/"
    
    string = "Max Sum\t Average Conflicts\n"
    precop = loadDcopFromFile1(file)
	
    factorgraph = precop.getFactorGraph()
	
    nVariables = len(factorgraph.getNodeVariables())
    varSet = (0.1 * nVariables)
	
    choice = True
    
    for run in range(nIstances): 
		
            print('\n\n###########################\n#\n#\tRUN ' + str(run) + '\n#\n###########################')

            averageValues = list()
            
            iterations = list()
       
            finalAssignaments = list()
             
            oldAssignaments = list()
             
            for i in range(nVariables):
                finalAssignaments.append(0)
                oldAssignaments.append(0)
                         
            '''
                values of MaxSum for each iteration
            '''
            values = list()    
			
            '''
                id for conditioning functions
            '''
            fId = 200
           
            '''
                create a new DCOP by visiting the initial graph
                save the factorgraph on file
            '''
            print('\ncreating dfs pseudo tree...')
            
            dfs_tree = dfs(factorgraph)
			            
            dfs_tree.dfsVisit() #actual visit	

            domain = factorgraph.getNodeVariables()[0].size()  
            relation = dfs_tree.getRelations()
            
            cop = dfs_tree.getDCopPseudoGraph(dir_factorgraph, run, domain)

            print('...created:\n')
			
            i = 0
             
            going = False
             
            functions = cop.getNodeFunctions()
            variables = cop.getNodeVariables()
             
            toRemove = list()
            toRemoveOld = list()
			
            iterations_bundling = int(nIterations) 
			
            total_time = 0
            
            '''
                repeat the algorithm for 50 times
                every exec set the value of variable
            '''
            while((len(variables) > 0) & (len(functions) > 0)):
                '''
                    if it isn't the first exec of MaxSum,
                    change the factor graph and repeat the algorithm
                '''
                if(going == True):      
                    '''
                        the agent of the cop
                    '''
                    agent = (core.getCop().getAgents())[0]
                     
                    '''
                        the variables of the cop
                    '''
                    variables = core.getCop().getNodeVariables()
                     
                    '''
                        the functions of the cop
                    '''
                    functions = core.getCop().getNodeFunctions()
                                      
                   					
                    if not toRemoveOld:
                        toRemove = dfs_tree.getInitToRemove() #prende le teste degli alberi
												
                        graph = dict()
						
                        for variable in variables:
                            graph[variable] = list()

                            for f in variable.getNeighbour():
                                for v in f.getNeighbour():
                                    if((v.getId()) != (variable.getId())):
                                        graph[variable].append(v)                             
                    
                        count = 0
                                        
                        while((count < (50)) and ((len(variables) - count) > 0) and (len(toRemove) < 10)):
                        
                            v = None
                            maxGrade = float('-inf')

                            for var in graph.keys():
                                if(len(graph[var]) > maxGrade):
                                    maxGrade = len(graph[var]) 
                                    v = var
									
                            if(len(toRemove) == 0):
                                toRemove.append(v)
                            else:
                                n2 = set(v.getNeighbour())
                                for var in toRemove:
                                    n1 = set(var.getNeighbour())
                                    inter = set(n1).intersection(n2)
                                    if(len(inter) == 0):
                                        if v not in toRemove:
                                            toRemove.append(v)                            
                            del graph[v] 
                         
                            count = count + 1										
                            
                        toRemoveOld = toRemove
                    else:
					
                        toRemove = None
                        toRemove = list()
                        
                        for node in toRemoveOld:
                            nodeId = node.getId()
                            for toAppend in relation[nodeId][1]:                                                                
                                toRemove.append(toAppend)
								
                        for rel in relation:
                            for toRem in toRemove:
                                if toRem in rel[1]:
                                    rel[1].remove(toRem)
									
                        if len(toRemove) == 0: 						
                            if len(variables) < nVariables/10: 
                                for var in variables:
                                    toRemove.append(var)
                            else:							
                                numberOfFunctions = list()
                                for node_id in range(0, len(variables)):
                                    numberOfFunctions.append(len( variables[node_id].getVariableNeighbour()))
                                
                                while (numberOfFunctions.index(max(numberOfFunctions)) != -1) and len(toRemove) < 5:
                                    node_id = numberOfFunctions.index(max(numberOfFunctions))
                                    toRemove.append( variables[node_id] )
							    
                                    numberOfFunctions[numberOfFunctions.index(max(numberOfFunctions))] = -1
                        	
                        toRemove = list(toRemove)	
                        toRemoveOld = list()
                        toRemoveOld = toRemove
									
                    iterations_bundling = iterations_bundling - len(toRemove)
					
                    state = 0
					
                    for j in range(len(toRemove)):     
                        '''
                            state of variable i
                        '''
                        state = toRemove[j].getStateArgument()
						
                        print('conditioning on:', toRemove[j].toString(), state.getValue())
                        
                        index = getIndex(originalCop,toRemove[j])
                        '''
                            save the value of the variable
                        '''
                        finalAssignaments[index] = state.getValue()
                         
                        oldAssignaments[index] = finalAssignaments[index]

                    if(len(toRemove) > 0):
                        for variableToRemove in toRemove:
                            for rel in relation:
                                if( variableToRemove in rel[1]):
                                    rel[1].remove(variableToRemove)
									
                        for variableToRemove in toRemove:
                            
                            functionsToRemove = variableToRemove.getNeighbour()
                            
                            if variableToRemove in agent.getVariables():
                                agent.removeNodeVariable(variableToRemove)
                            if variableToRemove in variables:
                                variables.remove(variableToRemove) 
                           	
                            for otherVar in variables:
                                n1 = set(functionsToRemove)
                                n2 = set(otherVar.getNeighbour())
                                inter = set(n1).intersection(n2)
								
                                while(len(inter) > 0):
                                    argsOfFunction = list()
                                    func = inter.pop()
                                    argsOfFunction.append(otherVar)
                                    if func in functions:
                                        functions.remove(func)
                                    if func in agent.getFunctions():
                                        agent.removeNodeFunction(func)
                                    otherVar.removeNeighbours(functionsToRemove)
                                    
                                    nodefunction = NodeFunction(fId)
                                    functionevaluator = TabularFunction()
                                    nodefunction.setFunction(functionevaluator)
                                    otherVar.addNeighbour(nodefunction)
                                    nodefunction.addNeighbour(otherVar)
                                    costTable = (func.getFunction()).getCostTable()
                                    index = (func.getFunction()).getParameterPosition(variableToRemove)
                                    state = (variableToRemove.getStateArgument()).getValue()
									
                                    for j in range(0,otherVar.size()):
                                        t = (j)
                                        if index == 0:
                                            cost = costTable[(state, j)] 
                                        else:
                                            cost =costTable[(j,state)]
                                        nodefunction.getFunction().addParametersCost(t, cost)     
                                                
                                    nodefunction.getFunction().setParameters(argsOfFunction)

                                    agent.addNodeFunction(nodefunction)
                                    functions.append(nodefunction)
                            
                                    fId = fId + 1  
                                    
                                otherVar.removeNeighbours(functionsToRemove)
                           	
                            for fictfun in functionsToRemove:
                                if fictfun.getId() >= 5000:
                                    if fictfun in functions:
                                        functions.remove(fictfun)
							
  
                    if((len(variables) > 0) & (len(functions) > 0)):
                    
                        agents = list() 
                             
                        agents.append(agent)    
                                 
                        cop = COP_Instance(variables, functions, agents)
                             
                        i = i + varSet
 
                     
                if((len(variables) > 0) & (len(functions) > 0)):
                    '''
                        create new MaxSum instance (max/min)
                    '''           

                    core = MaxSum(cop, "min", run) 
                    
                    '''
                        update only at end?
                    '''
                    core.setUpdateOnlyAtEnd(False)    
         
                    core.setIterationsNumber(iterations_bundling)
                             
                    start_time = time.time()          
                                                                     
                    '''
                        invoke the method that executes the MaxSum algorithm
                    '''
                    
                    print('\n###running solve_complete()\n')
					
                    core.solve_complete()
					                    
                    values = core.getValues()

                    elapse_time = time.time() - start_time
                    print('MaxSum elapse_time:', elapse_time)  

                    total_time = total_time + elapse_time					
                     
                    going = True 
                     
                    if(i == 0):
                        '''
                             create a copy of cop
                        '''
                        originalCop = deepcopy(core.getCop())
                         
                        oldVariables = originalCop.getNodeVariables()
                         
                        for k in range(len(oldVariables)):
                            oldAssignaments[k] = oldVariables[k].getStateIndex()
                                                                     
                    actualValue = calculateActualValue(originalCop, oldAssignaments) 
                    averageValues.append(actualValue)

                    iterations.append(len(values))                    
                     
            if((len(variables) > 0) & (len(functions) == 0)):
                '''
                    the variables of the cop
                '''
                
                variables = core.getCop().getNodeVariables()

                '''
                    remaining variables to set
                '''
                index = (nVariables - i) - 1
                
                k = 0   
                
                j = 1

                while(j < ((index / varSet) + 1)):   
                
                    while(k < (varSet * j)):
                        '''
                            state of variable i
                        '''
                        state = (variables[k]).getStateArgument() 
                        '''
                            save the value of the variable
                        '''
                        finalAssignaments[i] = state.getValue()
                         
                        oldAssignaments[i] = finalAssignaments[i]

                        i = i + k
                        
                        k = k + 1
                        
                    actualValue = calculateActualValue(originalCop,oldAssignaments)                    
                         
                    averageValues.append(actualValue)
                        
                    iterations.append(len(values))
                    
                    j = j + 1
            
            for i in range(len(iterations)):
                if(i > 0):
                    iterations[i] = iterations[i] + iterations[i-1]
                    
            averageValuesInstances.append(averageValues)
            iterationsInstances.append(iterations)
                         
            # draw the chart 
            # x axis: number of MaxSum exec
            # y axis: conflicts
            x = iterations
             
            '''
                x axis: number of MaxSum exec
            '''
            y = averageValues
            pl.title('Cost / Iterations chart')
            pl.xlabel('Iterations')
            pl.ylabel('Cost')
            pl.plot(x, y)
            pl.savefig(dir_charts + "Chart_RUN_" + str(run) + ".png")
            pl.close()
			
            print('total time for MaxSum ', total_time)
      
    sumIterations = [sum(x) for x in zip(*iterationsInstances)] 
    sumValues = [sum(x) for x in zip(*averageValuesInstances)] 
    
    stdIterations = [numpy.std(x) for x in zip(*iterationsInstances)]
    stdValues = [numpy.std(x) for x in zip(*averageValuesInstances)]
	
    for i in range(len(sumIterations)):
        sumIterations[i] = sumIterations[i] / nIstances
        
    for i in range(len(sumValues)):
        sumValues[i] = sumValues[i] / nIstances

    totalIterations = list(itertools.izip_longest(*iterationsInstances, fillvalue=0))
    totalConflicts = list(itertools.izip_longest(*averageValuesInstances, fillvalue=0))
	
    sumIterations_correct = [sum(x)/len_not_0(x) for x in totalIterations]
    sumValues_correct = [sum(x)/len_not_0(x) for x in totalConflicts]    
	
    stdIterations = list()
    stdValues = list()
	
    for i in range(0, len(totalConflicts)):
        appoggio = list()
        if(len_not_0(totalConflicts[i]) < 50):
            for elem in totalConflicts[i]:
                if(int(elem) != 0):
                    appoggio.append(elem)
					
            stdValues.append(numpy.std(appoggio))
        else:
            stdValues.append(numpy.std(totalConflicts[i]))
			
    for i in range(0, len(totalIterations)):
        appoggio = list()
        if(len_not_0(totalConflicts[i]) < 50):
            for elem in totalConflicts[i]: 
                if(int(elem) != 0):
                    appoggio.append(elem)
            stdIterations.append(numpy.std(appoggio))
        else:
            stdIterations.append(numpy.std(totalIterations[i]))
			

    median_iterations = list()
    median_conflicts = list()
	
    number_of_iterations = list() #each elements indicate how many runs are still active at that iteration number
	
    for x in totalIterations:
        number_of_iterations.append(len_not_0(x))
		
    finished_runs = list() #how many runs are terminated at that iteration number

    runs = nIstances
	
    for x in number_of_iterations:
        finished_runs.append(runs - int(x))
		
        runs = runs -(runs-int(x))
		
    runs = nIstances
	
    how_many_runs = 0
	
    for x in finished_runs:
        runs = runs - x
        if runs <= math.floor(nVariables / 2):
            how_many_runs = x
            break
	
    max_number_of_finished_runs = max(finished_runs)
	
    for i in range(0, finished_runs.index(how_many_runs)):
        median_iterations.append(sumIterations_correct[i])
        median_conflicts.append(sumValues_correct[i])
				
    # draw the chart 
    # x axis: number of MaxSum exec
    # y axis: conflicts
    x = median_iterations
             
    '''
        x axis: number of MaxSum exec
    '''
    y = median_conflicts
    pl.title('Cost / Iterations chart')
    pl.xlabel('Iterations')
    pl.ylabel('Cost')
    pl.plot(x, y)
    pl.savefig(dir_charts + "/AverageAllInstances.png")
    pl.close()    
	
    string = 'Iteration\tStdDevIter\t\t\tConflict\tStdDevConflicts\t\tHowManyStopped\n'
    
    for i in range(len(sumIterations_correct)):
        string = string + str(sumIterations_correct[i]) + '\t\t' + str(stdIterations[i]) + '\t\t' + str(sumValues_correct[i]) + '\t\t' + str(stdValues[i]) + '\t\t' + str(number_of_iterations[i]) + '\n'
		           
    output_file = open(dir_factorgraph + "/reportIterations.txt", "w")
    output_file.write(string)
    output_file.write("\n")
    output_file.close()
	
def getNodeById(node_id, cop):
    nodevariables = cop.getNodeVariables()
    for node in nodevariables:
        
        if int(node.getId()) == int(node_id.getId()):
            return node
    return None
    
def getIndex(originalCop, variable):
    variables = originalCop.getNodeVariables()
    
    for i in range(len(variables)):
        if(((variables[i]).getId()) == variable.getId()):
            return i
            
    return -1  
	
def len_not_0(l):
    count = 0
    for elem in range(0, len(l)):
        if(int(l[elem])) != 0:
            count = count +1 
			
    return count
    
def calculateActualValue(originalCop, oldAssignaments):     
    variables = originalCop.getNodeVariables()
    
    for i in range(len(variables)):
        (variables[i]).setStateIndex(oldAssignaments[i])
         
    return originalCop.actualValue()

def loadDcopFromFile(file):
    if file.lower().endswith('.r'):
        nodevariables = list()
        nodefunctions = list()
        agents = list()
        nogoods = list()
        domain = 0
        agent_id = 0
        variable_id = 0
        function_id = 0
        
        f = open(file, "r")
        for line in f:
            if line.startswith('AGENT'):
                splitted = line.split(" ")
                agent_id = int(splitted[1])
                agent = Agent(agent_id)
                agents.append(agent) 
                
            if line.startswith('VARIABLE'):
                splitted = line.split(" ")
                variable_id = int(splitted[1])
                agent_id = int(splitted[2])
                domain = int(splitted[3])

                nodevariable = NodeVariable(variable_id)
                nodevariable.addIntegerValues(domain)
                nodevariables.append(nodevariable)
				
                for agent in agents:
                    if int(agent.getId()) == agent_id:
                        agent.addNodeVariable(nodevariable)
						
            if line.startswith('CONSTRAINT'):
                splitted = line.split(" ")
                nodefunction = NodeFunction(function_id)
                functionevaluator = TabularFunction()
                nodefunction.setFunction(functionevaluator)
                nodefunctions.append(nodefunction)
				
                for agent in agents:
                    agent.addNodeFunction(nodefunction)
                
                argsOfFunction = list()
                
                variable_id1 = int(splitted[1])
                variable_id2 = int(splitted[2])
                #print('vars ' + str(variable_id1) + ' ' + str(variable_id2))
                #aggiungi ste due id var 
                for variable in nodevariables:
                    if int(variable.getId()) == variable_id1:
                        variable.addNeighbour(nodefunction)
                        nodefunction.addNeighbour(variable)
                        argsOfFunction.append(variable)
                        
                    if int(variable.getId()) == variable_id2:
                        variable.addNeighbour(nodefunction)
                        nodefunction.addNeighbour(variable)
                        argsOfFunction.append(variable)
                        
                nodefunction.getFunction().setParameters(argsOfFunction)
                function_id = function_id + 1
                
            if line.startswith('NOGOOD'):
                splitted = line.split(" ")
                nogoods.append(str(splitted[1]) + " " + splitted[2])
                
        computeIntegerArguments(nodefunctions, domain) #constraints have a domain of 0-9
        cop = COP_Instance(nodevariables, nodefunctions, agents)
        f.close()
        #print(cop.getFactorGraph().toString())
        return cop

def computeBinaryArguments( nodefunctions, nogoods, domain):
    for function in nodefunctions:
        for i in range(0, domain):
            for j in range(0, domain):
                parameters = list()
                cost = 0
                parameters.append(NodeArgument(i).getValue())
                parameters.append(NodeArgument(j).getValue())
                
                for nogood in nogoods:
                    splitted = nogood.split(" ")
                    if (int(splitted[0]) == i and int(splitted[1]) == j) or (int(splitted[0]) == j and int(splitted[1]) == i):
                        cost = -1
                parameters = tuple(parameters)
                function.getFunction().addParametersCost(parameters, cost)  

def computeIntegerArguments( nodefunctions, domain):
    for function in nodefunctions:
        for i in range(0, domain):
            for j in range(0, domain):
                parameters = (NodeArgument(i).getValue(), NodeArgument(j).getValue())
                cost = random.randint(1, 10)                
                function.getFunction().addParametersCost(parameters, cost)  

def loadDcopFromFile1(file):
    nodevariables = list()
    nodefunctions = list()
    agents = list()
    
    domain = 0
    agent_id = 0
    variable_id = 0
    function_id = 0
        
    f = open(file, "r")
    for line in f:
        if line.startswith('AGENT'):
            splitted = line.split(" ")
            agent_id = int(splitted[1])
            agent = Agent(agent_id)
            agents.append(agent)
		
        if line.startswith('VARIABLE'):
            splitted = line.split(" ")
            variable_id = int(splitted[1])
            agent_id = int(splitted[2])
            domain = int(splitted[3])
            nodevariable = NodeVariable(variable_id)
            nodevariable.addIntegerValues(domain)
            nodevariables.append(nodevariable)
            for agent in agents:
                if int(agent.getId()) == agent_id:
                    agent.addNodeVariable(nodevariable)
            

        if line.startswith('CONSTRAINT'):
            splitted = line.split(" ")
            nodefunction = NodeFunction(function_id)
            functionevaluator = TabularFunction()
            nodefunction.setFunction(functionevaluator)
            nodefunctions.append(nodefunction)
				
            for agent in agents:
                agent.addNodeFunction(nodefunction)
                
            argsOfFunction = list()
                
            variable_id1 = int(splitted[1])
            variable_id2 = int(splitted[2])

            #aggiungi ste due id var 
            for variable in nodevariables:
                if int(variable.getId()) == variable_id1:
                    variable.addNeighbour(nodefunction)
                    nodefunction.addNeighbour(variable)
                    argsOfFunction.append(variable)
                        
                if int(variable.getId()) == variable_id2:
                    variable.addNeighbour(nodefunction)
                    nodefunction.addNeighbour(variable)
                    argsOfFunction.append(variable)
                        
            nodefunction.getFunction().setParameters(argsOfFunction)
            
            function_id = function_id + 1
                
        if line.startswith('F'):
            splitted = line.split(' ')
            node_id0 = int(splitted[1])
            node_id1 = int(splitted[2])
            cost = int(splitted[3])
            parameters = (NodeArgument(node_id0).getValue(), NodeArgument(node_id1).getValue())
            nodefunction.getFunction().addParametersCost(parameters, cost)
            

    cop = COP_Instance(nodevariables, nodefunctions, agents)
    f.close()
    
    return cop

def saveToFile(file, cop):
    f = open(file, "w")
    nodevariables = cop.getNodeVariables()
    nodefunctions = cop.getNodeFunctions()
    agents = cop.getAgents()
    
    agentsOf = list()
    agentsOf = nodevariables
    
    for agent in agents:
        variables = agent.getVariables()

    for agent in agents:
        f.write('AGENT ' + str(agent.getId()) + '\n')
        
    for variable in nodevariables:
        string = ''
        string = 'VARIABLE ' + str(variable.getId())
        for agent in agents:
            variables = agent.getVariables()
            for v in variables:
                if v.getId() == variable.getId():
                    string = string + ' ' + str(agent.getId())
        string = string + ' ' + str(variable.size()) + '\n'
        f.write(string)
        
    for function in nodefunctions:
        neighbours = list()
        neighbours = function.getNeighbour()
        string = "CONSTRAINT "
        for n in neighbours:
            string = string + str(n.getId()) + ' '
        string = string + '\n'
		
        costtable = function.getFunction().getCostTable()
        
        for row in costtable:
            if int(costtable[row]) < 0:
                string = string + 'NOGOOD '
                arguments = row.getArray()
                for i in range(len(arguments)):
                    string = string + (arguments[i].toString()) + ' '
                string = string + '\n'
				
            else:
                string = string + 'F '
                arguments = row.getArray()
                for i in range(len(arguments)):
                    string = string + (arguments[i].toString()) + ' '
                string = string + '\n'
        string = string[:-1]
        string = string + '\n'
        f.write(string)
    f.close()
	
'''
creates a full connected factor graph of num_nodes nodes
'''
def getConnectedFactorGraph(num_nodes):
    nodeVariables = list()
    nodeFunctions = list()
    agents = list()

    edges=0

    variable_id = 0
    function_id = 0
    agent_id = 0

    arguments = [0, 0, 0, 1, 0, 2, 1, 0, 1, 1, 1, 2, 2, 0, 2, 1, 2, 2]

    agent = Agent(agent_id)

    #creo i nodi variabile
    for i in range(0, num_nodes):
        nodeVariable = NodeVariable(variable_id)
        nodeVariable.addIntegerValues(3)

        val = random.randint(0, 100)
        if( val < 34 ):
            nodeVariable.setColor(0)
        if( val >= 34 and val < 66):
            nodeVariable.setColor(1)
        else:
            nodeVariable.setColor(2)

        nodeVariables.append(nodeVariable)
        agent.addNodeVariable(nodeVariable)

        variable_id=variable_id+1
    
    #creo matrice di adiacenza del grafo
    adjmatrix = numpy.zeros((num_nodes,num_nodes))
    for i in range(0, num_nodes):
        for j in range(0, num_nodes):
            if j>i:
                adjmatrix[i][j] = 1
                edges = edges +1 #numero di archi da fare
            else:
                adjmatrix[i][j] = 0

    #scorri nella adjmatrix e da li fai i nodi

    for i in range(0, num_nodes):
        for j in range(0, num_nodes):
            if adjmatrix[i][j] == 1:
                nodefunction = NodeFunction(function_id)
                functionEvaluator = TabularFunction()
                nodefunction.setFunction(functionEvaluator)

                nodeVariables[i].addNeighbour(nodefunction)
                nodeVariables[j].addNeighbour(nodefunction)

                nodefunction.addNeighbour(nodeVariables[i])
                nodefunction.addNeighbour(nodeVariables[j])

                argsOfFunction = list()
                argsOfFunction.append(nodeVariables[i])
                argsOfFunction.append(nodeVariables[j])
                nodefunction.getFunction().setParameters(argsOfFunction)

                for index in range(0,9):
                    param=list()
                    for v in range(0,2):
                        if v == 0:
                            param.insert(v, NodeArgument(arguments[(index*2)]).getValue())
                        else:
                            param.insert(v, NodeArgument(arguments[(index*2)+1]).getValue())
                    if(param[0].equals(param[1])):
                        cost = -1
                    else:
                        cost = 0
                    nodefunction.getFunction().addParametersCost(param, cost)

                nodeFunctions.append(nodefunction)
                agent.addNodeFunction(nodefunction)
                function_id = function_id + 1

    agents.append(agent)
    
    cop = COP_Instance(nodeVariables, nodeFunctions, agents)
    return cop
                         

def getParser():
    '''
        This is the Parser that takes the parameters of Command Line
    '''
    parser = argparse.ArgumentParser(description="MaxSum-Algorithm")
    
    parser.add_argument("-iterations", metavar='iterations', type=int,
                        help="number of iterations")
    
    parser.add_argument("-instances", metavar='instances', type=int,
                        help="number of instances in Dcop")
        
    parser.add_argument("-op", metavar='op',
                        help="operator (max/min)")
    
    parser.add_argument("-file", metavar='file',
                        help="FILE of factor graph")
    
    
    args = parser.parse_args()

    '''
        All parameters ARE REQUIRED!!
        if the parameters are correct
    '''
    if  ((args.iterations > 0 & (not(args.iterations == None))) & 
        (args.instances > 0 & (not(args.instances == None))) & 
        (not(args.op == None) & ((args.op == 'max') | (args.op == 'min'))) & (not(args.file == None))):
        
        return args
    else:
        printUsage()
        sys.exit(2)
         

def printUsage():
    
    description = '\n----------------------------------- MAX SUM ALGORITHM ---------------------------------------\n\n'
    
    description = description + 'This program is a testing about DFS conditioning technique where each instance'
    description = description + 'is a different pseudo-tree of an initial factor graph'
    description = description + 'The results are saved as chart (.png) and as log file (.txt)\n'
    
    usage = 'All parameters ARE REQUIRED!!\n\n'
    
    usage = usage + 'Usage: python -iterations=Iter -instances=Inst -op=O -file=FILE [-h]\n\n'
    
    usage = usage + '-iterations Iter\tThe number of MaxSum iterations\n'
    usage = usage + '-instances Inst\t\tThe number of instances of Dcop to create\n'
    usage = usage + '-op O\t\t\tmax/min (maximization or minimization of conflicts)\n'
    usage = usage + '-file file\t\tFILE of the input factor graph \n'
    usage = usage + '-h help\tInformation about parameters\n'
    
    print(description)
    
    print(usage)
    

'''
	class used to perform everything about dfs visit
'''
class dfs:
    nodeVariablesFactorGraph = None #list of factor graph's variables
    nodeFunctions = None # list of DCOP's constraints
    nodeVariablesDCOP = None #list of DCOP's variables
    stack = None #stack used in dfs
    visited = None #list of nodes visited by dfs
    visitedNodes = None #array to track which node has been visited in dfs procedure
    backedgesList = None #list of backedges, format: [ [father_node;children_node], [...], ...]
    dcopDFSTree = None #dcop of the pseudo-tree obtained after the dfs visit
    relations = None #used to keep track of the children of every node in the pseudo-tree
    function_id = None #id of normal constraint
    function_be_id = None #id of backedges constraint
    domain = None #domain of the problem (in this case 0-9)
    toRemove = None #which variable to remove in first conditioning step

    def __init__(self, graph):
        self.nodeVariablesFactorGraph = graph.getNodeVariables()
		
        self.domain = graph.getNodeVariables()[0].size()
		
        '''
            copy the variables in the factor graph into the DCOP formalization		
        '''
        self.nodeVariablesDCOP = list()
        for var in self.nodeVariablesFactorGraph:
            nodeVariable = NodeVariable(int(var.getId()))
            nodeVariable.addIntegerValues(int(self.domain))
            self.nodeVariablesDCOP.append(nodeVariable) 

        self.nodeFunctions = list()
        self.stack = list()
        self.visited = list()
        self.visitedNodes = numpy.full( (len(self.nodeVariablesFactorGraph), 1), False )
        self.backedgesList = list()
		
        self.function_id = 0
        self.function_be_id = 1000
		
        '''
        init of relations, the rest will be computed during the visit 		
        '''
        self.relations = list()        
        for i in range(len(self.nodeVariablesFactorGraph)):
            self.relations.append( ( self.nodeVariablesFactorGraph[i], list() ) ) 
			
        self.toRemove = list()
		
    '''
    copy and return the relation array	
    '''		
    def getRelations(self):
        rel = deepcopy(self.relations) #deepcopy needed; aliases otherwise
        relation = list()
        neighbors = list()
        for r in rel:
            neighbors = list()
            for n in r[1]:
                neighbors.append(self.getDcopNodeById(n.getId()))
            relation.append( (r[0], neighbors ))
        
        return relation
    
    '''
        main method; returns the actual DCOP to perform the conditioning procedure 
    '''	
    def getDCopPseudoGraph(self, dir_factorgraph, run, domain):
        agents = list()

        agent_id = 0
		
        agent = Agent(agent_id)
        agents.append(agent)
		
        for variable in self.nodeVariablesDCOP:
            agent.addNodeVariable(variable)
        for function in self.nodeFunctions:
            agent.addNodeFunction(function)
		
        self.dcopDFSTree = COP_Instance(self.nodeVariablesDCOP, self.nodeFunctions, agents)
        
        string = ""
        string = string + "How many agents?" + str(len(agents)) + "\n"
    
        '''
             create the factor graph report
        '''
        for agent in agents:
            string = string + "\nAgent Id: " + str(agent.getId()) + "\n\n"
            string = string + "How many NodeVariables?" + str(len(agent.getVariables())) + "\n"
            for variable in agent.getVariables():
                string = string + "Variable: " + str(variable.toString()) + "\n"
                
            string = string + "\n"
            
            for function in agent.getFunctions():
                string = string + "Function: " + str(function.toString()) + "\n"
                
            string = string + "\n"    
    
        for variable in self.nodeVariablesDCOP:
            string = string + "Variable: " + str(variable.getId()) + "\n"
            for neighbour in variable.getNeighbour():
                string = string + "Neighbour: " + str(neighbour.toString()) + "\n"
            string = string + "\n"
    
        for function in self.nodeFunctions:
            string = string + "\nFunction: " + str(function.getId()) + "\n"
            string = string + "Parameters Number: " + str(function.getFunction().parametersNumber()) + "\n"
            for param in function.getFunction().getParameters():
                string = string + "parameter:" + str(param.toString()) + "\n"

            string = string + "\n\tCOST TABLE\n"

            string = string + str(function.getFunction().toString()) + "\n" 

        string = string + "\t\t\t\t\t\t\tFACTOR GRAPH\n\n" + str(self.dcopDFSTree.getFactorGraph().toString())

        info_graph_file = open(dir_factorgraph + "/factor_graph_run_" + str(run) + ".txt", "w")
        info_graph_file.write(string)
        info_graph_file.write("\n")
        info_graph_file.close()
                
        return self.dcopDFSTree
 
    def getNodeById(self, node_id):
        for node in self.nodeVariablesFactorGraph:
            if int(node.getId()) == int(node_id):
                return node
        return None
		
    def getDcopNodeById(self, node_id):
        for node in self.nodeVariablesDCOP:
            if int(node.getId()) == int(node_id):
                return node
        return None
		
    def getInitToRemove(self):
		return self.toRemove
	
    def getNodes(self):
        return self.nodeVariablesFactorGraph

    def getResult(self):
        if self.visited==None:
            print("\n\n!!!!run dfs first, result = None atm!!!!!\n\n")
        result = list()
        for v in self.visited:
            result.append(v.getId())
        return result

    def getBackedges(self):
        if self.backedgesList==None:
            print("\n\n!!!!run dfs first, backedges = None atm!!!!!\n\n")
        return self.backedgesList

    '''
        used by a visited node to add himself to dfs result
    '''
    def nodeIsVisited(self, nodevariable):
        self.visited.append(nodevariable)

    '''
        dfs visit 
    '''
    def dfsVisit(self):
        random.shuffle(self.nodeVariablesFactorGraph)
        for v in self.nodeVariablesFactorGraph:   
            
            if((self.isVisited(v)) == False):
                self.toRemove.append(self.getDcopNodeById(v.getId()))               
                self.stack.append(v.getId())
                self.toVisit(v, None, self.stack)        
	
    '''
        recursive method for visiting all the nodes
    '''
    def toVisit(self, nodevariable, parent,  stack):
        self.visitedNodes[nodevariable.getId()] = True
        self.nodeIsVisited(nodevariable) # used to keep track of the result
        neighbours = nodevariable.getVariableNeighbour()

        if(parent != None):			
            node_id1 = self.getDcopNodeById(int(parent.getId()))
            node_id2 = self.getDcopNodeById(int(nodevariable.getId()))
			
            self.relations[node_id1.getId()][1].append(node_id2)    
            
            argsOfFunction = list()
            nodefunction = NodeFunction(self.function_id)
            functionevaluator = TabularFunction()
            nodefunction.setFunction(functionevaluator)
				
            node_id1.addNeighbour(nodefunction)
            nodefunction.addNeighbour(node_id1)
            argsOfFunction.append(node_id1)
			
            node_id2.addNeighbour(nodefunction)
            nodefunction.addNeighbour(node_id2)
            argsOfFunction.append(node_id2)
			
            nodefunction.getFunction().setParameters(argsOfFunction)
				
            for i in range(0, self.domain):
                for j in range(0, self.domain):
                    t=(i,j)
                    #print(t)
                    cost = random.randint(1, 10)
                      
                    nodefunction.getFunction().addParametersCost(t, cost)
            self.nodeFunctions.append(nodefunction)
			
            self.function_id = self.function_id + 1
        
        be = self.backedges(stack, neighbours) #calculate backedges from me to parents
        random.shuffle(neighbours) #shuffle to perform a random visit

        for n in neighbours:
            '''
            if my neighbour is not visited
            '''
            if((self.isVisited(n)) == False):
                '''
                add it to stack
                '''
                stack.append(n.getId())
                '''
                start visit it
                '''
                self.toVisit(n, nodevariable, stack)
                '''
                visit of neighbour n is finished so i remove it from stack and continue with other neighbours
                '''
                stack.remove(n.getId()) #fine visita
            elif(str(nodevariable.getId())+";"+str(n.getId()) in be):
                self.backedgesList.append(str(nodevariable.getId()) + ";" + str(n.getId()))


    '''
    check if a specific node has been visited
    '''
    def isVisited(self, node):
        return self.visitedNodes[node.getId()]

    '''
    calculate backedges from current stack and neighbours of a node variable
    '''
    def backedges(self, stack, neighbours): 
        acstack = stack
        node = acstack[-1] #current node
        backedges = list()
        for s in acstack: #scorro lo stack
            for n in neighbours: #se tra i vicini ho nodi nello stack vuol dire che potevo venire da li aka backedge

                if s == n.getId() and s!=acstack[-1] and s!=acstack[-2]: #tutta via non devo considerare mio padre
                    backedges.append(str(node) + ";" + str(s))
                    
                    node1 = self.getDcopNodeById(node)
                    node2 = self.getDcopNodeById(s)

                    nodefunction = NodeFunction(self.function_be_id)
                    
                    fe = TabularFunction()
                    nodefunction.setFunction(fe)
                    
                    node1.addNeighbour(nodefunction)
                    node2.addNeighbour(nodefunction)
                    
                    nodefunction.addNeighbour(node1)
                    nodefunction.addNeighbour(node2)
                    
                    argsOfFunction = list()
                    argsOfFunction.append(node1)
                    argsOfFunction.append(node2)
                    
                    nodefunction.getFunction().setParameters(argsOfFunction)
					
                    for i in range(0, self.domain):
                        for j in range(0, self.domain):
                            t = (i,j)
                            cost = random.randint(1, 10)

                            nodefunction.getFunction().addParametersCost(t, cost)
                    self.nodeFunctions.append(nodefunction)                    
                    self.function_be_id = self.function_be_id + 1  									
        return backedges

    def toString(self):
        report = "Visit order(ids): \t"
        for v in self.visited:
            report = report + str(v.getId()) + ", "
        report = report[:-2] #delete last ;
        report = report + "\n\nList of backedges: \t"
        be = self.getBackedges()
        b = ' '.join(be)

        report = report + b
        return report
	
    def toStringDFSTree(self):
        report = '### DFS Tree ###\nNodeVariables:'
        dfs_tree = self.getDcopDFSTree()
        if (dfs_tree == None):
            report = 'DFS Tree does not exist. Run getDCopPseudoGraph() first'
            return report
		
        nodevariables = dfs_tree.getNodeVariables()
        for n in nodevariables:
            report = report + '\nVariable: ' + str(n) + ' ID: ' + str(n.getId()) + ' color: ' + str(n.getColor())
            report = report + '\n\thas FUNCTIONS neighbours ' + n.stringOfNeighbour() + '\n\n\thas VARIABLES neighbour '
            
            varsneigh = n.getVariableNeighbour()
            for va in varsneigh:
                report = report + str(va.getId()) + ' '
            report = report + '\n'
			
        nodefunctions = dfs_tree.getNodeFunctions()
        report += '\nNodefunctions:\n'
        for n in nodefunctions:
            report = report + '\tFunction: ' + str(n) + ' ID: ' + str(n.getId())
            if (int (n.getId() )>= 500 and int( n.getId()) < 1000):
                report = report + ' fictitious function'
            if (int(n.getId() )>= 1000):
                report = report + ' backedge '
            
            report = report + '\n\thas neighbours: ' + n.stringOfNeighbour() + '\n\n'
          
        report = report + '\nVisit and backedges:\n' + self.toString()
			
        return report


    
if __name__ == '__main__':
    main()
