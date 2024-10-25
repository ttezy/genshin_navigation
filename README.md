# genshin_navigation

Navigation tool for Genshin Impact

Roadmap build by QGIS

**In QGIS, set CRS as WGS 84/UTM zone 51N (Shanghai) for all layers**

configure snap tools to make sure paths are connected

## Dependencies

pip install geopandas networkx matplotlib shapely pyyaml PIL json tabulate logging pandas

## 使用说明

详情见 `example.py`

## Challenge
1. 定位误差会导致角色跑的时候可能不在主路上，会遇到撞墙蹭墙的情况，如果代码自己无法脱困，需通知更新roadmap
2. 对于小石头和树林的情况暂时唯一的解决办法就是更改roadmap连线，只能靠大家试错上报然后更改。如果后续可以做出来画面上的障碍检测，可以尝试local planning来小范围实时更新路径
3. 不建议游泳，会淹死
4. 理论上爬山和飞行路线可以靠画单行道解决，但是我还没搞明白QGIS怎么画单行道，研究明白了再说。但总体不建议爬山游泳和飞行，因为体力只降不减，且进入这三个状态时的体力条有非常大的不确定性（不知道进入状态前会被冲刺消耗掉多少）
5. 欢迎大家提出各种建议，也欢迎理性讨论。

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
