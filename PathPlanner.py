import geopandas as gpd
import networkx as nx
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
import yaml
from PIL import Image
import json
import logging
from tabulate import tabulate
import pandas as pd

class PathPlanner:
    def logger(self):
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # Create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s][%(message)s]')
        
        # Add formatter to ch
        ch.setFormatter(formatter)
        
        # Add ch to logger
        self.logger.addHandler(ch)

    def __init__(self, coord, coord_config_file_path=None):
        self.logger()

        # 定义路径点使用的坐标系（"minimap"/"BGI"）
        self.coord = coord
        self.logger.info("PathPlanner initialized with coordinate system: %s", coord)

        # 加载坐标配置文件
        with open(coord_config_file_path, 'r', encoding='utf-8') as file:
            self.coord_config = yaml.safe_load(file)
            self.logger.info("Loaded coordinate configuration from file path: %s", coord_config_file_path)

        # 定义目标点列表文件
        self.target_list_json = None
        # 定义计划路径JSON
        self.planned_path_json = None
        # 定义路径名称
        self.path_name = None
        # 定义国家名称
        self.country_name = None
        # 定义目标点
        self.target_list_global = []
        self.target_list_QGIS = []
        # 定义规划后路径
        self.planned_path_QGIS = None
        self.planned_path_global = None
        # 定义传送点flag
        self.search_teleport_flag = None
        # 定义路径图
        self.combined_gdf = None
        # 定义国家名称映射
        self.country_map = {
            "蒙德": "mengde",
            "璃月": "liyue",
            "稻妻": "daoqi",
            "枫丹": "fengdan",
            "纳塔": "nata",
            "层岩巨渊": "juyuan",
            "渊下宫": "yuanxiagong"
        }


    def load_target_points(self, target_file_path):
        # 从文件中加载目标点
        with open(target_file_path, 'r', encoding='utf-8') as file:
            self.target_list_json = json.load(file)

        # 获取路径名称
        self.path_name = self.target_list_json.get('name', 'Unknown')
        self.logger.info("Loaded path name: %s", self.path_name)
        # 获取国家名称
        self.country_name = self.target_list_json.get('country', 'Unknown')
        self.logger.info("Loaded country: %s", self.country_name)

        # 获取目标点列表
        self.target_list_global = self.target_list_json.get('positions', [])
        if self.target_list_global[0].get('type', None) == "path":
            # 第一个是传送点
            self.logger.info("Loaded 1 teleport and %d target points in the %s coordinate from file path %s", len(self.target_list_global)-1, self.coord, target_file_path)
            self.search_teleport_flag = False
            self.logger.info("Teleport is pre-defined, set search_teleport_flag to False")
        else:
            # 第一个是目标点
            self.logger.info("Loaded 0 teleport and %d target points in the %s coordinate from file path %s", len(self.target_list_global), self.coord, target_file_path)
            self.search_teleport_flag = True
            self.logger.info("Teleport is not pre-defined, set search_teleport_flag to True")
        
        # Print the target list with table
        self.logger.info("Target list in the %s coordinate: \n%s", self.coord, tabulate(self.target_list_global, headers='keys', tablefmt='pretty'))

    # Function to find the nearest node in the graph
    def get_nearest_node(self, graph, point):
        nearest_node = None
        min_dist = float('inf')
        for node in graph.nodes:
            dist = point.distance(node)
            if dist < min_dist:
                nearest_node = node
                min_dist = dist
        return nearest_node
    
    def search_path(self, normal_mode=True, fly_mode=False, jump_mode=False, swim_mode=True):
        # 转换坐标系：minimap/BGI -> QGIS
        if self.coord == "minimap":
            self.minimap_to_QGIS()
        elif self.coord == "BGI":
            self.BGI_to_minimap()

        # Get the map name for the current country
        map_name = self.country_map.get(self.country_name, None)
        if map_name is None:
            self.logger.error("Country name %s is not recognized.", self.country_name)
            return

        # Construct the file path
        mode_list = []
        if normal_mode:
            mode_list.append("normal")
        if fly_mode:
            mode_list.append("fly")
        if jump_mode:
            mode_list.append("jump")
        if swim_mode:
            mode_list.append("swim")
        self.logger.info("Search path with modes: %s", mode_list)

        for mode in mode_list:
            roadmap_file = f"genshin_map/2D/{map_name}/{map_name}_{mode}_paths.gpkg"
            # Load the geopandas dataframe
            gdf = gpd.read_file(roadmap_file)
            self.logger.info("Loaded geopandas dataframe from file path: %s", roadmap_file)

            self.combined_gdf = pd.concat([self.combined_gdf, gdf], ignore_index=True)
        self.logger.info("Combined geopandas dataframe with %d rows", len(self.combined_gdf))

        # Create the graph
        G = nx.Graph()
        for idx, row in self.combined_gdf.iterrows():
            line = row.geometry
            if isinstance(line, LineString):
                for start, end in zip(list(line.coords[:-1]), list(line.coords[1:])):
                    G.add_edge(Point(start), Point(end), time=row['time'], move_mode=row['move_mode'])  # Add 'move_mode' attribute

        # Print the move_mode for each LineString in the graph
        # for u, v, data in G.edges(data=True):
        #     self.logger.info("Edge from %s to %s has move_mode: %s", u, v, data['move_mode'])

        # Initialize the planned path
        self.planned_path_QGIS = []
        # Find the nearest node to the start and end points and compute the shortest path
        for i in range(len(self.target_list_QGIS) - 1):
            start_point = Point(self.target_list_QGIS[i]['x'], self.target_list_QGIS[i]['y'])
            end_point = Point(self.target_list_QGIS[i + 1]['x'], self.target_list_QGIS[i + 1]['y'])
            start_node = self.get_nearest_node(G, start_point)
            end_node = self.get_nearest_node(G, end_point)
            self.logger.info("Start point: %s, End point: %s", start_node, end_node)
            try:
                shortest_path = nx.shortest_path(G, source=start_node, target=end_node, weight='time')
                self.logger.info("Shortest path found with %d nodes", len(shortest_path))

                self.planned_path_QGIS.append(self.target_list_QGIS[i])
                # Collect the path with attributes
                path_with_attributes = []
                for u, v in zip(shortest_path[:-1], shortest_path[1:]):
                    edge_data = G.get_edge_data(u, v)
                    path_with_attributes.append((u, v, edge_data['move_mode']))

                    # Append each segment to the planned path JSON
                    self.planned_path_QGIS.append({
                    'x': v.x,
                    'y': v.y,
                    'type': 'path',
                    'action': '',
                    'move_mode': edge_data['move_mode']
                    })
                # Append the last point to the planned path
                self.planned_path_QGIS.append(self.target_list_QGIS[-1])

            except nx.NetworkXNoPath:
                self.logger.error("No path found between %s and %s", start_node, end_node)
                continue

        # Print the planned path with table
        self.logger.info("Planned path in the QGIS coordinate: \n%s", tabulate(self.planned_path_QGIS, headers='keys', tablefmt='pretty'))

        # 转换坐标系：QGIS -> minimap/BGI
        if self.coord == "minimap":
            self.QGIS_to_minimap()
        elif self.coord == "BGI":
            self.QGIS_to_BGI()

    def visualize_path(self):
        # 可视化路径
        # Load the map image
        map_name = self.country_map.get(self.country_name, self.country_name)
        map_img = plt.imread(f"genshin_map/2D/{map_name}/{map_name}_2048_v0.png")

        # Plot the map image with the correct extent (set to UTM zone bounds)
        fig, ax = plt.subplots(figsize=(10, 10))

        # Modify this extent to match your UTM zone coordinates (xmin, xmax, ymin, ymax in UTM)
        # Get the size of the map image
        img_height, img_width, _ = map_img.shape
        
        # Set the extent based on the image size
        ax.imshow(map_img, extent=[0, img_width, -img_height, 0])

        # Extract the coordinates from the planned path
        path = [(point['x'], point['y']) for point in self.planned_path_QGIS]

        # Plot the road network
        self.combined_gdf.plot(ax=ax, edgecolor='black', linewidth=0.5)
        self.combined_gdf.plot(ax=ax, color='white', linewidth=2, alpha=0.5)
        # Plot the shortest path
        path_line = LineString(path)
        gpd.GeoSeries([path_line]).plot(ax=ax, edgecolor='black', linewidth=5)
        gpd.GeoSeries([path_line]).plot(ax=ax, color='orange', linewidth=3)

        # Plot the start and end points
        start_point = path[0]
        end_point = path[-1]
        
        ax.scatter([start_point[0]], [start_point[1]], edgecolor='black', s=250)
        ax.scatter([end_point[0]], [end_point[1]], edgecolor='black', s=250)

        ax.scatter([start_point[0]], [start_point[1]], color='green', s=200, label='Start')
        ax.scatter([end_point[0]], [end_point[1]], color='blue', s=200, label='End')

        # Add legend
        ax.legend()

        # Show the plot
        # Extract the coordinates from the planned path
        path = [(point['x'], point['y']) for point in self.planned_path_QGIS]

        # Calculate the bounding box of the path
        min_x = min(point[0] for point in path)
        max_x = max(point[0] for point in path)
        min_y = min(point[1] for point in path)
        max_y = max(point[1] for point in path)

        # Set the extent to the bounding box with some padding
        padding = 100  # Adjust padding as needed
        ax.set_xlim(min_x - padding, max_x + padding)
        ax.set_ylim(min_y - padding, max_y + padding)

        plt.show()

    def save_path(self):
        # 保存路径
        self.planned_path_json = {
            "name": self.path_name,
            "anchor_name": "传送锚点",
            "country": self.country_name,
            "positions": self.planned_path_global
        }
        with open(f"planned_path\\{self.path_name}_planned.json", 'w', encoding='utf-8') as file:
            json.dump(self.planned_path_json, file, ensure_ascii=False, indent=4)
        self.logger.info("Saved planned path to file path: %s", f"planned_path\\{self.path_name}_planned.json")

    def get_nearest_teleport(self):
        # 搜索最近的传送点
        pass

    def minimap_to_QGIS(self):
        # 将minimap坐标转换为QGIS坐标
        QGIS_center = self.coord_config[self.country_name].get("center", None)
        self.logger.info("In global coordinate, center of %s - center of global is %s", self.country_name, QGIS_center)
        self.target_list_QGIS = []
        for point_global in self.target_list_global:
            x_QGIS = point_global['x'] + QGIS_center[0]
            y_QGIS = -(point_global['y'] + QGIS_center[1])
            point_QGIS = point_global.copy()
            point_QGIS['x'] = x_QGIS
            point_QGIS['y'] = y_QGIS
            self.target_list_QGIS.append(point_QGIS)
        self.logger.info("Converted %d points from %s coordinate to QGIS coordinate: \n%s", len(self.target_list_global), self.coord, tabulate(self.target_list_QGIS, headers='keys', tablefmt='pretty'))

    def QGIS_to_minimap(self):
        # 将QGIS坐标转换为minimap坐标
        QGIS_center = self.coord_config[self.country_name].get("center", None)
        self.logger.info("In global coordinate, center of %s - center of global is %s", self.country_name, QGIS_center)
        self.planned_path_global = []
        for point_QGIS in self.planned_path_QGIS:
            x_global = point_QGIS['x'] - QGIS_center[0]
            y_global = -point_QGIS['y'] - QGIS_center[1]
            point_global = point_QGIS.copy()
            point_global['x'] = x_global
            point_global['y'] = y_global
            self.planned_path_global.append(point_global)
        self.logger.info("Converted %d points from QGIS coordinate to %s coordinate: \n%s", len(self.planned_path_QGIS), self.coord, tabulate(self.planned_path_global, headers='keys', tablefmt='pretty'))

    def BGI_to_minimap(self):
        # 将BGI坐标转换为minimap坐标
        pass

    def QGIS_to_BGI(self):
        # 将QGIS坐标转换为BGI坐标
        pass

if __name__ == '__main__':
    path_planner = PathPlanner(coord="minimap", coord_config_file_path="minimap.config.map.yaml")

    # path_planner.load_target_points("target_list\风车菊_蒙德_8个_20240814_101536.json")
    path_planner.load_target_points("target_list\坠星山谷_千风神殿西.json")

    path_planner.search_path()

    path_planner.save_path()

    path_planner.visualize_path()
