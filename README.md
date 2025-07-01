# digital-twin-water-network

# 数字孪生富水水库系统UE

基于 Vue 2、Cesium 与 SuperMap 技术开发的数字孪生富水水库仿真系统，融合倾斜摄影建模与三维地理可视化能力，支持丰富的水文动态模拟与场景交互展示。

## ✨ 项目特色

- 🎯 **高精度建模**：集成水库地形、3D Titles 水坝与居民点模型
- 🌦️ **多种天气模拟**：支持晴天、雨天等气象变化演示
- 🌊 **水文动态仿真**：
  - 模拟水位变化、水体流动、水面淹没过程
  - 支持开闸放水等控制场景演示
- 🗺️ **地图模式切换**：支持 2D/3D 地图切换
- 💻 **前端技术栈**：Vue 2 + Cesium + SuperMap iClient3D

具体展示效果如下：
![图片1](imgs/1.png)

# 大坝数字孪生系统

这是一个基于Python的大坝数字孪生系统演示项目，基于富水水库案例模拟，实现了从传感器数据采集、边缘计算到云端分析的完整流程。代码位于digital-twin-platform文件夹下。
### 项目结构

```
digital-twin-water-network/
├── public/                # 静态资源
├── src/
│   ├── assets/            # 项目资源文件
│   ├── components/        # 组件目录
│   │   ├── Map/           # 地图相关组件
│   │   └── Controls/      # 控制面板组件
│   ├── utils/             # 工具函数
│   │   ├── cesium/        # Cesium相关工具
│   │   └── supermap/      # SuperMap相关工具
│   ├── services/          # API服务
│   ├── store/             # 状态管理
│   ├── views/             # 页面视图
│   ├── App.vue            # 根组件
│   └── main.js            # 入口文件
├── .env                   # 环境变量
└── vue.config.js          # Vue配置
```

### 核心技术实现

- **三维场景加载**：基于Cesium与SuperMap iClient3D实现高精度三维场景加载与渲染
- **水文模拟系统**：通过自定义着色器实现水面动态效果，结合水位数据实现淹没分析
- **交互控制系统**：采用Vue组件化设计，实现场景漫游、天气切换、水位调节等功能
- **性能优化**：实现三维瓦片按需加载、LOD层级控制，保证大场景流畅运行

### 开发环境

- Node.js >= 12.0.0
- Vue 2.6.x
- Cesium 1.8x.x
- SuperMap iClient3D 10.x