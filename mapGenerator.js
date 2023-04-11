// Get the generate button and map container elements
const generateBtn = document.getElementById('generate-btn');
const mapContainer = document.getElementById('map-container');

// Add an event listener to the generate button
generateBtn.addEventListener('click', function() {
	// Create a new image object
	const image = new Image();

	// Generate the terrain values using Perlin noise
	const terrain_values = generate_terrain_values((map_height, map_width), scale, octaves, persistence, lacunarity);

	// Smooth the terrain values using Gaussian blur
	terrain_values = gaussian_filter(terrain_values, sigma=blur_radius);

	// Determine the terrain type for each pixel in the image
	const canvas = document.createElement('canvas');
	canvas.width = map_width;
	canvas.height = map_height;
	const context = canvas.getContext('2d');
	for (let y = 0; y < map_height; y++) {
		for (let x = 0; x < map_width; x++) {
			// Determine the terrain type for this pixel based on its value
			let terrain_type = null;
			const value = terrain_values[y][x];
			for (let t in thresholds) {
				if (value < thresholds[t]) {
					terrain_type = t;
					break;
				}
			}

			// Set the pixel color based on the terrain type
			context.fillStyle = `rgb(${colors[terrain_type].join(',')})`;
			context.fillRect(x, y, 1, 1);
		}
	}

	// Set the map container's HTML to the generated map
	mapContainer.innerHTML = '';
	mapContainer.appendChild(image);
});
