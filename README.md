# genshin_navigation

Navigation tool for Genshin Impact

Roadmap build by QGIS

**In QGIS, set CRS as WGS 84/UTM zone 51N (Shanghai) for all layers**

configure snap tools to make sure paths are connected

## Dependencies

pip install geopandas networkx matplotlib shapely pyyaml PIL json tabulate logging pandas

## 使用说明

详情见 `example.py`

# RoadMap

### Mengde

![Mengde Roadmap](genshin_map/2D/mengde/mengde_roadmap.png)
image

## Structre

```
Class PathPlanner

# 初始化planner，设立传入数据的坐标系以及坐标系配置文件， 如config.map.yaml
_init_(coord=minimap/BGI, coord_config_file_path)

# 加载目标点list, 第一个点需为传送点
load_target_points(json file)

# 生成路径
# 设置是否寻找最近传送点（如果传入的list初始点不是传送点，开启后会添加最近传点为初始点）(还没写)
# 设置travel方式，随意组合是否开启游泳、爬山和飞行
# 目前只画了部分行走路径和游泳路径
search_path(normal_mode=True, fly_mode, jump_mode, swim_mode)

# 保存路径到json（在planned_path文件夹下）
save_path

# 图像化
visualize_path

# 寻找QGIS里的最近点
search_nearest_node

# 寻找QGIS里的最近传送点（应包含传送点和秘境点）（还没写）
# search_nearest_teleport

# 坐标系转换
minimap_to_QGIS
QGIS_to_minimap
BGI_to_QGIS（还没写）
QGIS_to_BGI（还没写）
```
