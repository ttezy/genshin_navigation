import geopandas as gpd
import networkx as nx
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
import yaml
from PIL import Image
import json

# Define the start and end points in minimap coordinates
# start_point = Point(3127, -1685)  # Replace with your actual start UTM coordinates
# end_point = Point(4670, -912)    # Replace with your actual end UTM coordinates
start_point_minimap = Point(4076.02001953125, -6604.75140380859) #坠星山谷
end_point_minimap = Point(3807.869968750001, -5832.896328125) #千风神殿西


# Load the GPKG file
gdf = gpd.read_file(r"C:\Games\Script\minimap\planner\genshin_map\mengde_normal_paths.gpkg", layer="mengde_normal_paths")
# Load the YAML file
with open('config.map.yaml', 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)    

# Access the center coordinates for "蒙德"
minimap_center = config['蒙德']['center']
# Print the center coordinates
print("Center coordinates for '蒙德':", minimap_center)

# Load the image
image_path = r"C:\Games\Script\minimap\planner\genshin_map\mengde_2048_v0.png"
image = Image.open(image_path)

# Get the size of the image
width, height = image.size

# Print the size
print(f"Width: {width} pixels, Height: {height} pixels")

# Function to negate the y-values of the geometry
def negate_y(geometry):
    if isinstance(geometry, Point):
        return Point(geometry.x, -geometry.y)
    elif isinstance(geometry, LineString):
        return LineString([(x, -y) for x, y in geometry.coords])
    else:
        return geometry

def QGIS_to_minimap_coordinates(geometry, minimap_center):
    """
    Convert QGIS coordinates to minimap coordinates
    """
    # Get the center coordinates
    geometry = negate_y(geometry)

    if isinstance(geometry, Point):
        return Point(geometry.x - minimap_center[0], geometry.y - minimap_center[1])
    elif isinstance(geometry, LineString):
        return LineString([(x - minimap_center[0], y - minimap_center[1]) for x, y in geometry.coords])
    else:
        return geometry

# Apply the transformation to the GeoDataFrame
gdf['geometry'] = gdf['geometry'].apply(QGIS_to_minimap_coordinates, minimap_center=minimap_center)

# Create a NetworkX graph from the GeoDataFrame
G = nx.Graph()

# Add edges to the graph
for idx, row in gdf.iterrows():
    line = row.geometry
    if isinstance(line, LineString):
        for start, end in zip(list(line.coords[:-1]), list(line.coords[1:])):
            G.add_edge(Point(start), Point(end), weight=LineString([start, end]).length)

# Function to find the nearest node in the graph
def get_nearest_node(graph, point):
    nearest_node = None
    min_dist = float('inf')
    for node in graph.nodes:
        dist = point.distance(node)
        if dist < min_dist:
            nearest_node = node
            min_dist = dist
    return nearest_node



# Find the nearest nodes in the graph
start_node = get_nearest_node(G, start_point_minimap)
end_node = get_nearest_node(G, end_point_minimap)

# Calculate the shortest path
shortest_path = nx.shortest_path(G, source=start_node, target=end_node, weight='weight')

# Extract the coordinates of the shortest path
path_coords = [node.coords[0] for node in shortest_path]

# # Load the map image
# map_img = plt.imread(r"C:\Games\Script\minimap\planner\genshin_map\mengde_2048_v0.png")

# # Plot the map image with the correct extent (set to UTM zone bounds)
# fig, ax = plt.subplots(figsize=(10, 10))

# # Modify this extent to match your UTM zone coordinates (xmin, xmax, ymin, ymax in UTM)
# ax.imshow(map_img, extent=[0.0000000000000000,6994.0000000000000000, -5465.0000000000000000, 0.0000000000000000,])

# # Plot the road network
# gdf.plot(ax=ax, color='gray', linewidth=0.5)

# # Plot the shortest path
# path_line = LineString(path_coords)
# gpd.GeoSeries([path_line]).plot(ax=ax, color='orange', linewidth=3)

# # Plot the start and end points
# ax.scatter([start_point_minimap.x], [start_point_minimap.y], color='green', s=200, label='Start')
# ax.scatter([end_point_minimap.x], [end_point_minimap.y], color='blue', s=200, label='End')

# # Add legend
# ax.legend()

# # Show the plot
# plt.show()

# Extract the coordinates of the shortest path
path_coords = [start_point_minimap] + [Point(x, y) for x, y in path_coords[1:-1]] + [end_point_minimap]
# Create the JSON structure
path_points = []
for i, point in enumerate(path_coords):
    path_point = {
        "x": point.x,
        "y": point.y,
        "type": "path" if i != len(path_coords) - 1 else "target",
        "move_mode": "normal",
        "action": ""
    }
    path_points.append(path_point)

# Create the final JSON object
path_json = {
    "name": "Demo_坠星山谷",
    "anchor_name": "传送锚点",
    "country": "蒙德",
    "executor": "CollectPathExecutor",
    "positions": path_points,
}

# Convert to JSON string
path_json_str = json.dumps(path_json, ensure_ascii=False, indent=4)

# Save the JSON string to a file
output_file_path = r"C:\Games\Script\minimap\planner\Demo_坠星山谷.json"
with open(output_file_path, 'w', encoding='utf-8') as file:
    file.write(path_json_str)

# Print the JSON string
print(path_json_str)