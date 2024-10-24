import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
import os
from shapely.geometry import Point, LineString

roadwidth = 0.7
roadstroke = roadwidth + 0.3
image_alpha = 0.9

def visualize_road_map():
    for country in os.listdir("genshin_map/2D"):
        file_dir = f"genshin_map/2D/{country}/"
        print("Country: ", country)

        for file_name in os.listdir(file_dir):
            if file_name.endswith(".png"):
                if "roadmap" not in file_name:
                    image_path = os.path.join(file_dir, file_name)
                    print("Image: ", file_name)
                    map_img = plt.imread(image_path)

            if file_name.endswith(".gpkg"):
                # Load the road network data
                if "normal" in file_name:
                    normal_path_dir = os.path.join(file_dir, file_name)
                if "jump" in file_name:
                    jump_path_dir = os.path.join(file_dir, file_name)
                if "fly" in file_name:
                    fly_path_dir = os.path.join(file_dir, file_name)
                if "swim" in file_name:
                    swim_path_dir = os.path.join(file_dir, file_name)
                
        normal_path_gdf = gpd.read_file(normal_path_dir)
        jump_path_gdf = gpd.read_file(jump_path_dir)
        fly_path_gdf = gpd.read_file(fly_path_dir)
        swim_path_gdf = gpd.read_file(swim_path_dir)

        # Create a graph from the road network
        G_normal = nx.Graph()
        for idx, row in normal_path_gdf.iterrows():
            line = row.geometry
            if isinstance(line, LineString):
                for start, end in zip(list(line.coords[:-1]), list(line.coords[1:])):
                    G_normal.add_edge(Point(start), Point(end), time=row['time'], move_mode=row['move_mode'])  # Add 'move_mode' attribute
        
        G_jump = nx.Graph()
        for idx, row in jump_path_gdf.iterrows():
            line = row.geometry
            if isinstance(line, LineString):
                for start, end in zip(list(line.coords[:-1]), list(line.coords[1:])):
                    G_jump.add_edge(Point(start), Point(end), time=row['time'], move_mode=row['move_mode'])  # Add 'move_mode' attribute

        G_fly = nx.Graph()
        for idx, row in fly_path_gdf.iterrows():
            line = row.geometry
            if isinstance(line, LineString):
                for start, end in zip(list(line.coords[:-1]), list(line.coords[1:])):
                    G_fly.add_edge(Point(start), Point(end), time=row['time'], move_mode=row['move_mode'])

        G_swim = nx.Graph()
        for idx, row in swim_path_gdf.iterrows():
            line = row.geometry
            if isinstance(line, LineString):
                for start, end in zip(list(line.coords[:-1]), list(line.coords[1:])):
                    G_swim.add_edge(Point(start), Point(end), time=row['time'], move_mode=row['move_mode'])

        # Plot the road network
        fig, ax = plt.subplots()
        # Get the size of the map image
        img_height, img_width, _ = map_img.shape
        
        # Set the extent based on the image size
        ax.imshow(map_img, extent=[0, img_width, -img_height, 0], alpha=image_alpha)

        # Plot the road network
        for line in normal_path_gdf.geometry:
            if isinstance(line, LineString):
                x, y = line.xy
                ax.plot(x, y, color='orange', linewidth=roadwidth, label='Normal Path', zorder=1)
                ax.plot(x, y, color='black', linewidth=roadstroke, zorder=0)

        for line in jump_path_gdf.geometry:
            if isinstance(line, LineString):
                x, y = line.xy
                ax.plot(x, y, color='red', linewidth=roadwidth, label='Jump Path', zorder=1)
                ax.plot(x, y, color='black', linewidth=roadstroke, zorder=0)

        for line in fly_path_gdf.geometry:
            if isinstance(line, LineString):
                x, y = line.xy
                ax.plot(x, y, color='green', linewidth=roadwidth, label='Fly Path', zorder=1)
                ax.plot(x, y, color='black', linewidth=roadstroke, zorder=0)

        for line in swim_path_gdf.geometry:
            if isinstance(line, LineString):
                x, y = line.xy
                ax.plot(x, y, color='cyan', linewidth=roadwidth, label='Swim Path', zorder=1)
                ax.plot(x, y, color='black', linewidth=roadstroke, zorder=0)
        # plt.show()

        # Save the plot
        output_path = os.path.join(file_dir, f"{country}_roadmap.png")
        fig.savefig(output_path, bbox_inches='tight', pad_inches=0, dpi=map_img.shape[0] / fig.get_size_inches()[1])


if __name__ == "__main__":
    visualize_road_map()