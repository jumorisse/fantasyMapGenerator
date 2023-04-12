import random
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
import noise
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

if __name__ == '__main__':
  map, heightValues, terrainValues = generateMap()
  img_file = './static/mapData/map.png'
  map.save(img_file, format='PNG')
  np.save('./static/mapData/height_values.npy', heightValues)
  np.save('./static/mapData/terrain_values.npy', terrainValues)
  print(img_file)
