# genshin_navigation

Navigation tool for Genshin Impact

Install QGIS

Add Georeferencer plugin

**set CRS as WGS 84/UTM zone 51N for shanghai**

configure snap tools to make sure paths are connected

pip install geopandas networkx

```
Class PathPlanner

# 初始化planner，设立传入数据的坐标系以及坐标系配置文件， 如config.map.yaml
_init_(coord=minimap/BGI, coord_config_file_path)

# 加载目标点，可以是一个目标点也可以是目标点list
load_target_points(json file)

# 生成路径
# 设置是否寻找最近传送点（如果传入的list初始点不是传送点，开启后会添加最近传点为初始点）(还没写)
# 设置travel方式，随意组合是否开启游泳、爬山和飞行
search_path(normal_mode=True, fly_mode, jump_mode, swim_mode)

# 图像化
visualize_path

# 保存路径到json
save_path

# 寻找QGIS里的最近点
search_nearest_node

# 寻找QGIS里的最近传送点（应包含传送点和秘境点）
# search_nearest_teleport

# 坐标系转换
minimap_to_QGIS
QGIS_to_minimap
BGI_to_QGIS
QGIS_to_BGI
```

# RoadMap

### Mengde

![Mengde Roadmap](genshin_map/2D/mengde/mengde_roadmap.png)
image
