import geopandas as gpd
import networkx as nx
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt

# Load the GPKG file
gdf = gpd.read_file(r"C:\Games\Script\minimap\planner\genshin_map\mengde_normal_paths.gpkg", layer="mengde_normal_paths")

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

# Define the start and end points in UTM coordinates
start_point = Point(3127, -1685)  # Replace with your actual start UTM coordinates
end_point = Point(4670, -912)    # Replace with your actual end UTM coordinates

# Find the nearest nodes in the graph
start_node = get_nearest_node(G, start_point)
end_node = get_nearest_node(G, end_point)

# Calculate the shortest path
shortest_path = nx.shortest_path(G, source=start_node, target=end_node, weight='weight')

# Extract the coordinates of the shortest path
path_coords = [node.coords[0] for node in shortest_path]

# Load the map image
map_img = plt.imread(r"C:\Games\Script\minimap\planner\genshin_map\mengde_2048_v0.png")

# Plot the map image with the correct extent (set to UTM zone bounds)
fig, ax = plt.subplots(figsize=(10, 10))

# Modify this extent to match your UTM zone coordinates (xmin, xmax, ymin, ymax in UTM)
ax.imshow(map_img, extent=[0.0000000000000000,6994.0000000000000000, -5465.0000000000000000, 0.0000000000000000,])

# Plot the road network
gdf.plot(ax=ax, color='gray', linewidth=0.5)

# Plot the shortest path
path_line = LineString(path_coords)
gpd.GeoSeries([path_line]).plot(ax=ax, color='orange', linewidth=3)

# Plot the start and end points
ax.scatter([start_point.x], [start_point.y], color='green', s=200, label='Start')
ax.scatter([end_point.x], [end_point.y], color='blue', s=200, label='End')

# Add legend
ax.legend()

# Show the plot
plt.show()
