from PathPlanner import PathPlanner

# 创建一个PathPlanner对象，指定坐标系为minimap，配置文件为minimap.config.map.yaml
# 目前只写了minimap和QGIS的坐标转换
path_planner = PathPlanner(coord="minimap", coord_config_file_path="minimap.config.map.yaml")
# 加载目标点列表（将文件路径改为你的json）
path_planner.load_target_points("target_list\落落莓.json")
# 计算最短路径
path_planner.search_path()
# 保存路径（位置在planned_path文件夹下）
path_planner.save_path()
# 可视化路径（可选）
# path_planner.visualize_path()



