import re
import warnings

from printutils import *
from colorama import Fore, Style


class dirGraph:
    '''
        General graph class.
    '''

    def __init__(self, nodeList, pathList):
        '''
            Construct a graph dict out of the nodeList and the pathList, assumes to be directed.
        '''
        regC = re.compile(r'[^a-zA-Z\s]')

        graphDict = {node: [] for node in nodeList}
        for path in pathList:
            nodeListRaw = path.split('-')
            nodeA, nodeB = regC.sub('', nodeListRaw[0]), regC.sub('', nodeListRaw[1])

            if '<' in nodeListRaw[0]:
                graphDict[nodeB].append(nodeA)
            if '>' in nodeListRaw[1]:
                graphDict[nodeA].append(nodeB)

        self.graphDict = graphDict

    def checkPath(self, pathToCheck):
        '''
            Checks if the entered path is valid.
        '''
        if len(pathToCheck) >= 2:
            # print('aaaaaa')
            currNode = pathToCheck[0]
            nextNode = pathToCheck[1]
            if currNode in self.graphDict.keys() and (nextNode in self.graphDict[currNode]):
                return self.checkPath(pathToCheck[1:])
            else:
                return False
        else:
            return True

    def findPaths_NN(self, nodeA, nodeB, listOfPaths=[], currPath=''):
        '''
            Finds all the possible paths from nodeA, to nodeB.
        '''

        if nodeA == nodeB:
            warnings.warn('Require nodeA and nodeB to be distinct!', Warning)
            return None

        if currPath == '':
            currPath += nodeA
        #
        # print('\n', listOfPaths, f'Current Node {nodeA}')
        # print(f'Node {nodeA} connections : {self.graphDict[nodeA]},\n')

        nodeConnecs = [node for node in self.graphDict[nodeA]]
        while nodeConnecs:
            currNode = nodeConnecs[0]
            # print(f'Traversed so far: {currPath}, dealing with node {currNode} @ node {nodeA}')

            if currNode in currPath:
                # print(f'    Already traversed node {currNode}!\n')
                del nodeConnecs[0]

            elif currNode == nodeB:
                # print(f'    Reached node {nodeB}!')
                # currPath += nodeB
                listOfPaths.append(currPath + nodeB)
                # print(f'   List of Paths {listOfPaths}')
                del nodeConnecs[0]

            elif currNode not in currPath:
                del nodeConnecs[0]

                # print(f'\n! Starting with node {currNode}.')
                self.findPaths_NN(currNode, nodeB, listOfPaths=listOfPaths, currPath=currPath + currNode)

        # print(f'    Finished Node {nodeA}')
        return listOfPaths


class costGraph(dirGraph):
    '''
        Graph class with cost associated to the paths
    '''
    defaultCost = 0.0

    def __init__(self, nodeList, pathList, costDict):
        '''
            Inheret attributes from the directed graph class and expand the cost dictionary.
        '''
        super().__init__(nodeList, pathList)
        expandCostDict = {}
        for graphConn in costDict.keys():
            if '<->' in graphConn:
                rawNodes = graphConn.split('<->')
                expandCostDict[rawNodes[0] + '->' + rawNodes[1]] = costDict[graphConn]
                expandCostDict[rawNodes[1] + '->' + rawNodes[0]] = costDict[graphConn]
            elif '<-' in graphConn:
                rawNodes = graphConn.split('<-')
                expandCostDict[rawNodes[1] + '->' + rawNodes[0]] = costDict[graphConn]
            elif '->' in graphConn:
                expandCostDict[graphConn] = costDict[graphConn]

        self.pathCost = expandCostDict

    def findCostPath(self, graphPath, checkPath=True, costPath=0):
        '''
            Given a valid path the function returns the associated cost for traversing the path.
        '''
        if checkPath is True:
            try:
                if self.checkPath(graphPath) is False:
                    raise Exception('Invalid Graph Path!')
            except Exception as inst:
                print(Fore.RED + inst.args[0] + Style.RESET_ALL)
                return None

        if len(graphPath) >= 2:
            # currPath = graphPath[0:2]
            pathKey = graphPath[0] + '->' + graphPath[1]
            costPath += self.pathCost[pathKey]

            return self.findCostPath(graphPath[1:], checkPath=False, costPath=costPath)
        else:
            return costPath


if __name__ == '__main__':
    nodeList = ['A', 'B', 'C', 'D', 'E']
    # pathList = ['A<->E', 'B<->E', 'E->C', 'C<->B', 'B->D', 'A->D', 'D->C']
    costDict = {'A<->E': 0.3, 'B<->E': 0.5, 'E->C': 0.4, 'C<->B': 0.9, 'B->D': 0.1, 'A->D': 0.9, 'D->C': 0.4,
                'A<-B': 1.0}
    print(delimitator2, "Graph strcture is as follows:")
    pp(costDict)

    testGraph = dirGraph(nodeList, list(costDict.keys()))
    costGraphInst = costGraph(nodeList, list(costDict.keys()), costDict)

    startNode, endNode = 'A', 'C'
    print(delimitator2, f"Finding shortest path between {startNode} and {endNode}")
    possPaths = costGraphInst.findPaths_NN(startNode, endNode)

    print(f"All the possible paths between {startNode} and {endNode} :", possPaths)
    pathsCostDict = {}
    for path in possPaths:
        pathsCostDict[path] = costGraphInst.findCostPath(path)

    print(f"List of paths and costs between {startNode} and {endNode}", sorted(pathsCostDict.items(),
          key=lambda kv: kv[1]), delimitator2)

    # print(testGraph.findPaths_NN('E', 'D'))
