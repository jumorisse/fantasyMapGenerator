import random
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
import noise
import networkx as nx
import io
import sys

def generateMap():
    # Map dimensions
    mapWidth = 800
    mapHeight = 600

    # Mapping of terrains to ints (for storing terrain values as .npy)
    terrainIds = {
        "water": 0,
        "land": 1,
        "mountain": 2,
        "snowy peak": 3,
    }

    # Colors for the different terrain types
    colors = {
        "water": [(0, 0, 10), (0, 0, 255)],       # dark blue to light blue       
        "land": [ (102, 205, 102), (0, 100, 0)],        # green
        "mountain": [(80, 80, 80), (180, 180, 180)], # gray
        "snowy peak": [(220, 220, 220), (255, 255, 255)]  # white
    }

    # Parameters for terrain generation
    numLayers = np.random.randint(1, 6)
    scales = [np.random.randint(150, 300) for _ in range(numLayers)]
    octaves = [6 + np.random.randint(-2, 2) for _ in range(numLayers)]
    persistences = [0.5 + np.random.uniform(-0.1, 0.1) for _ in range(numLayers)]
    lacunarities = [2.0 + np.random.uniform(-0.1, 0.1) for _ in range(numLayers)]
    blurRadius = 2.0
    thresholds = {
        'water':[0,0],
        'land':[0,0],
        'mountain':[0,0],
        'snowy peak':[0,0]
    }

    for terrain, minRange, maxValue in [('water', 0.7,0), ('land',0.2,0.3), ('mountain', 0.15,0.4), ('snowy peak', None, None)]:
        if terrain == 'water':
            lowerBound = -1
        else:
            lowerBound = upperBound
        thresholds[terrain][0] = lowerBound

        if terrain == 'snowy peak':
            upperBound = 1
        else:
            upperBound = np.random.uniform(lowerBound+minRange, maxValue)
        thresholds[terrain][1] = upperBound

    # Define a function to generate the terrain map using Perlin noise
    def generateHeightValues(shape, scales, octaves, persistence, lacunarity):
        heightValues = np.zeros(shape)
        for i in range(shape[0]):
            for j in range(shape[1]):
                # Combine multiple layers of Perlin noise
                noiseSum = 0
                for k in range(len(scales)):
                    scale = scales[k]
                    octave = octaves[k]
                    persistence = persistences[k]
                    lacunarity = lacunarities[k]
                    noiseSum += noise.snoise2(i/scale, j/scale, octaves=octave, persistence=persistence, lacunarity=lacunarity)

                # Normalize the noise value to the range [-1,1]
                heightValues[i][j] = noiseSum / len(scales)
        return heightValues

    # Map as height map, smooth it using gaussian
    map = Image.new("RGB", (mapWidth, mapHeight))
    heightValues = generateHeightValues((mapHeight, mapWidth), scales, octaves, persistences, lacunarities)
    heightValues = gaussian_filter(heightValues, sigma=blurRadius)

    # Create ndarray to store terrain types
    terrainValues = np.empty((mapHeight, mapWidth))

    # Change pixel colors depending on assigned terrain
    for y in range(mapHeight):
        for x in range(mapWidth):
            # Determine the terrain type for this pixel based on its height
            terrainType = None
            height = heightValues[y][x]
            for t in thresholds:
                if height < thresholds[t][1]:
                    terrainType = t
                    terrainValues[y][x] = terrainIds[t]
                    break

            # Set the pixel color based on the terrain type
            lower_color, upper_color = colors[terrainType]
            normHeight = (height - thresholds[terrainType][0]) / (thresholds[terrainType][1] - thresholds[terrainType][0])
            new_color = tuple(int(lower_color[i] + normHeight * (upper_color[i] - lower_color[i])) for i in range(3))
            map.putpixel((x, y), new_color)

    # Return the resulting map
    return map, heightValues, terrainValues

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

def tupleToString(tuple):
    return str(tuple[0])+','+str(tuple[1])

def stringToTuple(string):
    values = string.split(',')
    return (int(values[0]), int(values[1]))

if __name__ == '__main__':
  map, heightValues, terrainValues = generateMap()
  img_file = './static/mapData/map.png'
  map.save(img_file, format='PNG')
  np.save('./static/mapData/height_values.npy', heightValues)
  np.save('./static/mapData/terrain_values.npy', terrainValues)

  mapGraph = createMapGraph(heightValues, terrainValues)
  nx.write_weighted_edgelist(mapGraph, "./static/mapData/mapGraph.edgelist")
  print(img_file)
