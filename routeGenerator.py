import sys
from PIL import Image
import numpy as np
import networkx as nx
from networkx import NetworkXNoPath
from scipy.spatial import distance

def distHeuristic(start, end):
    startCoordinates = stringToTuple(start)
    endCoordinates = stringToTuple(end)
    return np.sqrt((startCoordinates[0]-endCoordinates[0])**2 + (startCoordinates[1]-endCoordinates[1])**2)
    #return distance.euclidean(, stringToTuple(end))

def tupleToString(tuple):
    return str(tuple[0])+','+str(tuple[1])

def stringToTuple(string):
    values = string.split(',')
    return (int(values[0]), int(values[1]))


def generateRoute(x1, y1, x2, y2):
    map = Image.open('./static/mapData/map.png')
    heightValues = np.load('./static/mapData/height_values.npy')
    terrainValues = np.load('./static/mapData/terrain_values.npy')
    mapGraph = createMapGraph(heightValues, terrainValues)
    sourceNode = tupleToString((x1,y1))
    targetNode = tupleToString((x2,y2))
    pathColor = (255, 0, 0)

    # If one of the clicks was on water, do not do anything
    if terrainValues[y1][x1] == 0 or terrainValues[y2][x2] == 0:
        return map

    # Mark clicks with red square
    for x in range(x1 - 2, x1 + 2):
        for y in range(y1 - 2, y1 + 2):
            if (x >= 0 and x < map.size[0]) and (y >= 0 and y < map.size[1]):
                map.putpixel((x, y), pathColor)

    for x in range(x2 - 2, x2 + 2):
        for y in range(y2 - 2, y2 + 2):
            if (x >= 0 and x < map.size[0]) and (y >= 0 and y < map.size[1]):
                map.putpixel((x, y), pathColor)

    # Find path between start and end via A* algorithm
    try:
        path = nx.astar_path(G=mapGraph, source=sourceNode, target=targetNode, heuristic=distHeuristic, weight='weight')
    except NetworkXNoPath:
        return map

    # Mark path in pathColor
    for node in path:
        nodeCoordinates = stringToTuple(node)
        map.putpixel((nodeCoordinates[0], nodeCoordinates[1]), pathColor)

    return map

def createMapGraph(heightValues, terrainValues):
    mapGraph = nx.Graph()
    height, width = heightValues.shape

    # Add nodes to the graph, one for each cell on the map
    for y in range(height):
        for x in range(width):
            terrainType = terrainValues[y][x]
            # If terrain is water, skip
            if terrainType == 0:
                continue

            # Add the node to the graph, node id is coordinate tuple, each node also has terrain and height stored
            mapGraph.add_node(tupleToString((x, y)), terrain=terrainType, height=heightValues[y][x])

    # Add edges to the graph, use 8-neighborhood
    for y in range(height):
        for x in range(width):
            currentNode = (x, y)

            # If current node is water, skip
            if terrainValues[y][x] == 0:
                continue

            for neighbor in [(x+1,y), (x-1,y), (x,y+1), (x,y-1), (x+1,y+1), (x+1,y-1), (x-1,y+1), (x-1,y+1)]:
                # Stay inside map boundary
                if neighbor[0] < 0 or neighbor[0] >= width or neighbor[1] < 0 or neighbor[1] >= height:
                    continue

                # If neighbor is water, skip
                if terrainValues[neighbor[1]][neighbor[0]] == 0:
                    continue

                height_diff = abs(mapGraph._node[tupleToString(currentNode)]['height'] - mapGraph._node[tupleToString(neighbor)]['height'])

                if terrainValues[neighbor[1]][neighbor[0]] == 1 or terrainValues[y][x] == 1:
                    terrainWeight = 5
                elif terrainValues[neighbor[1]][neighbor[0]] ==2 or terrainValues[y][x] ==2:
                    terrainWeight = 10
                else:
                    terrainWeight = 1

                mapGraph.add_edge(tupleToString(currentNode), tupleToString(neighbor), weight=500*height_diff*terrainWeight)

    return mapGraph

if __name__ == '__main__':
    map = generateRoute(x1=int(sys.argv[1]), y1=int(sys.argv[2]), x2=int(sys.argv[3]), y2=int(sys.argv[4]))
    map.save('./static/mapData/map.png', format='PNG')
    print('./static/mapData/map.png')
