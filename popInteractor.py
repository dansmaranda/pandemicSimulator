import numpy as np
import matplotlib.pyplot as plt
import random
import time
import math

from matplotlib.animation import FuncAnimation
from printutils import *


# initX, initY = 0, 0
infectProb = 0.01
infectRadius = 2.0
xyBounds = 10.0
unitSize = 1.0

popMembDict = {'0': {'Status': 'NotCarrying',
                     'RepColor': 'green'},
               '1': {'Status': 'Carrier-Symptoms',
                     'RepColor': 'red'},
               '2': {'Status': 'Carrier-NO-Symptoms',
                     'RepColor': 'yellow'},
               '3': {'Status': 'Immune/Dead.',
                     'RepColor': 'grey'}}
attrList = ['spaceXY', 'pointType', 'NN']

# plotDict = {}

# class_colours = ['g', 'r', 'y', 'grey']
# plotDict = {str(typeNb): color for typeNb, color in enumerate(class_colours)}

fig, (ax, axHist) = plt.subplots(2, 1, sharex=True, figsize=(8, 8))


ln = ax.scatter([], [], s=50)
histLn = axHist.hist([])


def _genInitConfig(nbPeople=100, nbCarriersSympt=1, nbCarriersNoSympt=1):
    '''
        Creates a random seed of nbPeople people with the randomly selected attributes in attrList.
    '''
    psDict = {}
    auxLst = ['0'] * (nbPeople - nbCarriersSympt - nbCarriersNoSympt) + \
             ['1'] * nbCarriersSympt + ['2'] * nbCarriersNoSympt

    for numbID in range(nbPeople):
        attrDict = {}
        # x and y coordinate initialisation
        attrDict['spaceXY'] = {'xPos': random.uniform(-xyBounds, xyBounds),
                               'yPos': random.uniform(-xyBounds, xyBounds)}

        # initialise random types
        randIdx = random.randint(0, len(auxLst) - 1)
        attrDict['pointType'] = str(auxLst[randIdx])
        del auxLst[randIdx]

        # create empty field for nearest neighbourghs
        attrDict['NN'] = {}

        # add point ID and update the phase space dictionary
        persID = 'ID-' + str(numbID)
        psDict[persID] = attrDict

    return psDict


def _makeListFromDict(phaseSpaceDict, attrList):
    '''
        Given a phase space dictionary, the function produces a dictionary of ordered lists with all the attributes
        of the phaseSpaceDict.

        Arguments:
            - phaseSpaceDict        ::      A valid phase space dictionary.

        Returns:
            - dictOfLists={
                        Attr1: [point1_Attr1, point2_Attr1, ...],
                        Attr2: [point1_Attr2, point2_Attr2, ...],
                        ...
                            }

            Dictionary containing all the attributes as keys and lists with the points attibute values.

    '''
    # Make empty list with all the attributes
    dictOfLists = {}
    for modelAttribute in attrList:
        dictOfLists[modelAttribute] = []

    for point in phaseSpaceDict.keys():
        for modelAttribute in attrList:

            if (phaseSpaceDict[point][modelAttribute] is not None):

                # dictOfLists[modelAttribute].append( float(phaseSpaceDict[point][modelAttribute]) )
                if type(phaseSpaceDict[point][modelAttribute]) == dict:

                    for subAttr in phaseSpaceDict[point][modelAttribute]:
                        if modelAttribute + '-' + subAttr not in dictOfLists.keys():
                            dictOfLists[modelAttribute + '-' + subAttr] = []

                        dictOfLists[modelAttribute + '-' + subAttr].append(phaseSpaceDict[point][modelAttribute][subAttr])
                else:
                    dictOfLists[modelAttribute].append(phaseSpaceDict[point][modelAttribute])

            # except Exception as e:
            #     print(e)
            #     pass

    # print(len (  list(dictOfLists['Higgs']) ))
    # exit()
    return dictOfLists


def _convertTypeToCol(typeList):
    '''
        Converts type 0, 1, 2, ... into a color list.
    '''
    colorList = []
    for typeNb in typeList:
        try:
            colorList.append(popMembDict[str(typeNb)]['RepColor'])
        except Exception as e:
            print(e, 'No such type! Putting type as neutral, i.e. GREY.')
            colorList.append('grey')

    return colorList


def countTypes(psDict):
    '''
        Counts each type of the population in the current phase space dictionary, and returns a
        dictionary with their specific numbers.
    '''
    return tyCountDict


def initEnviron():
    '''
        Initialise the scatter frame.
    '''
    global psDict, attrList
    # ax.set_xlim(-1, 1)
    # ax.set_ylim(-1, 1)
    axDict = _makeListFromDict(psDict, attrList)
    colorList = _convertTypeToCol(axDict['pointType'])
    ax.scatter(axDict['spaceXY-xPos'], axDict['spaceXY-yPos'], c=colorList)
    ax.set_xlim((-xyBounds - unitSize/2, xyBounds + unitSize/2))
    ax.set_ylim((-xyBounds - unitSize/2, xyBounds + unitSize/2))
    return ln,


def evolveLocDt(currX, currY, pointID, moveMthd='normalRnd', mtdDict={'stepSigma': 0.05}):
    '''
        Given the current X and Y coordinates at time t, function returns the evolved position at the next instance
        in time t + dt. Specify method via moveMthd and supply arguments via mtdDict
    '''

    if moveMthd == 'normalRnd':
        stepSigma = mtdDict['stepSigma'] * unitSize
        newX = currX + random.normalvariate(0, stepSigma)
        newY = currY + random.normalvariate(0, stepSigma)
    elif moveMthd == 'circPattern':
        stepθ = 0.05 * ((-1)**int(pointID.split('-')[1]))
        rotRad = random.uniform(0, 0.001)

        if (currX > 0 and currY > 0) or (currX > 0 and currY < 0):
            thetaInit = np.arctan(currY / currX)
        else:
            thetaInit = np.arctan(currY / currX) - np.pi
        rOrigin = np.sqrt(currX**2 + currY**2)
        rNew = abs(rOrigin - rotRad)

        newX = rNew * np.cos(thetaInit + stepθ)
        newY = rNew * np.sin(thetaInit + stepθ)
        # exit()

    elif moveMthd == 'upDown':
        stepSigma = mtdDict['stepSigma']
        if int(pointID.split('-')[1]) % 2 == 0:
            newX = currX + random.uniform(0, stepSigma)
            newY = currY
        else:
            newX = currX
            newY = currY + random.uniform(0, stepSigma)
    return {'newX': newX, 'newY': newY}


def probInfectNN(psDict, listNN, carrierList=[1, 2]):
    '''
        Given the list of NN of the current carrier, roll the dice and update the type of the IDs in the list,
        i.e. see if they're now infected.

        If generated number ∈ [0, 1] is below infectProb, then the candidate is infected, otherwise it remains
        unchanged.
    '''
    for pointID in listNN:
        if random.uniform(0, 1) < infectProb:
            if psDict[pointID]['pointType'] not in carrierList:
                psDict[pointID]['pointType'] = random.choice(carrierList)
        else:
            pass

    return psDict


def evolveTimeDt(*args):
    '''
        Update function for the animation
    '''
    global psDict, attrList

    frameNb = args[0]
    psDict = args[1]
    # print(delimitator2)
    # printCentered(f'Frame number {frameNb}')

    for pointID in psDict.keys():
        # Get the current point's location and calculate the new position
        currX, currY = psDict[pointID]['spaceXY']['xPos'], psDict[pointID]['spaceXY']['yPos']
        pointType = psDict[pointID]['pointType']

        # Calculate new infection generation #rollThemDice
        if 'Carrier' in popMembDict[str(pointType)]['Status']:
            # print(Fore.RED + f'💀 Point {pointID} has the PLAGUE 💀' + Style.RESET_ALL)
            psDict = findNN(psDict, allDict=pointID)

            psDict = probInfectNN(psDict, list(psDict[pointID]['NN'].keys()))
        # Evolve and Update the point's location in the dictionary
        newLocDict = evolveLocDt(currX, currY, pointID)
        psDict[pointID]['spaceXY']['xPos'] = newLocDict['newX']
        psDict[pointID]['spaceXY']['yPos'] = newLocDict['newY']

    # pp(psDict)
    # Update the NN entries in the dictionary every N frames
    # if frameNb % 10 == 0:
    #     findNN(psDict)
        # print(delimitator2)

    axDict = _makeListFromDict(psDict, attrList)
    colorList = _convertTypeToCol(axDict['pointType'])
    newPlotData = np.transpose(np.array([axDict['spaceXY-xPos'], axDict['spaceXY-yPos']]))

    ln.set_offsets(np.array(newPlotData))
    ln.set_color(colorList)
    # time.sleep(1.0)
    return ln,


def findNN(psDict, intRad=infectRadius, nSigma=2, allDict=None):
    '''
        Given a psDict, function will find each points nearest neighbourghs, corresponding to 1σ, 2σ, ..., nSigma radii
        defined by intRad.
    '''
    # pointList = list(psDict.keys())
    # nbOfPoints = len(pointList)

    if allDict is not None:
        auxList = list(psDict.keys())
        auxList.remove(allDict)
        pointList = [allDict] + auxList
        del auxList
        # print(pointList)

    else:
        pointList = list(psDict.keys())
    nbOfPoints = len(pointList)

    for pointNb in range(nbOfPoints):
        origID = pointList[pointNb]
        if (allDict is not None) and (origID is not allDict):
            break

        origX, origY = psDict[origID]['spaceXY']['xPos'], psDict[origID]['spaceXY']['yPos']
        origContr2 = origX**2 + origY**2 - intRad**2
        for nextPointNb in range(pointNb+1, nbOfPoints):
            compID = pointList[nextPointNb]
            compX, compY = psDict[compID]['spaceXY']['xPos'], psDict[compID]['spaceXY']['yPos']
            compContr2 = compX**2 + compY**2

            if (compX * origX + compY * origY) >= ((origContr2 + compContr2) / 2.0):
                # print(f'Point {compID} is in range of Point {origID}')
                if compID not in psDict[origID]['NN']:
                    psDict[origID]['NN'][compID] = None
                    psDict[compID]['NN'][origID] = None
            elif compID in psDict[origID]['NN'].keys():
                del psDict[origID]['NN'][compID], psDict[compID]['NN'][origID]
        # print(f"Point {origID} has NN: {psDict[origID]['NN'].keys()} .")

    return psDict



# psDict = {'ID-0': {'spaceXY': {'xPos': 0.3, 'yPos': 0}, 'pointType': 0, 'NN': {}}
#           ,
#           'ID-1': {'spaceXY': {'xPos': 0.1, 'yPos': 0.3}, 'pointType': 2, 'NN': {}}
#           ,
#           'ID-2': {'spaceXY': {'xPos': 0.5, 'yPos': -0.3}, 'pointType': 0, 'NN': {}}
#           ,
#           'ID-3': {'spaceXY': {'xPos': -0.3, 'yPos': -0.3}, 'pointType': 0, 'NN': {}},
#           'ID-4': {'spaceXY': {'xPos': -0.3, 'yPos': 0.3}, 'pointType': 0, 'NN': {}}
#           }

psDict = _genInitConfig(nbPeople=300)

# posDict = {'xPos': initX, 'yPos': initY}
# findNN(psDict)
# initEnviron()
# plt.show()
# time.sleep(100000)

ani = FuncAnimation(fig, evolveTimeDt, fargs=[psDict], init_func=initEnviron, frames=10000,
                    interval=30, blit=True)
plt.show()
# try:
#     while True:
#         continue
# except KeyboardInterrupt:
#     print('Process killed by user')
