import random
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
import noise

# Map dimensions
mapWidth = 800
mapHeight = 600

# Colors for the different terrain types
colors = {
    "water": (0, 0, 255),       # blue
    "land": (0, 255, 0),        # green
    "mountain": (128, 128, 128), # gray
    "snowy peak": (255, 255, 255)  # white
}

# Parameter for terrain generation
scale = 200         #
octaves = 6         #
persistence = 0.5   #
lacunarity = 2.0    #
blurRadius = 2.0    #
thresholds = {
    'water':0,
    'land':0.4,
    'mountain':0.65,
    'snowy peak':0.75
}

# Define a function to generate the terrain values using Perlin noise
def generate_terrain_values(shape, scale, octaves, persistence, lacunarity):
    terrain_values = np.zeros(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            terrain_values[i][j] = noise.snoise2(i/scale, j/scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity)
    return terrain_values

# Create Image Object
map = Image.new("RGB", (mapWidth, mapHeight))

# Assign terrains
terrain_values = generate_terrain_values((mapHeight, mapWidth), scale, octaves, persistence, lacunarity)

# Smooth Terrain
terrain_values = gaussian_filter(terrain_values, sigma=blurRadius)

# Change pixel colors depending on assigned terrain
for y in range(mapHeight):
    for x in range(mapWidth):
        # Determine the terrain type for this pixel based on its value
        terrain_type = None
        value = terrain_values[y][x]
        for t in thresholds:
            if value < thresholds[t]:
                terrain_type = t
                break

        # Set the pixel color based on the terrain type
        map.putpixel((x, y), colors[terrain_type])

# Show the resulting map
map.show()