# 水网数字孪生平台 (Water Network Digital Twin Platform)

这是一个水网数字孪生平台示例，用于演示水务系统数字孪生技术的基本概念和实现。

## 系统架构

该平台包含三个主要组件：
1. **云端服务** - 负责数据存储、处理和可视化
2. **边缘节点** - 负责数据收集、预处理和本地决策
3. **终端设备** - 物理设备及其数字孪生表示

## 功能特点

- 水网设备实时数据采集与监控
- 水流量、水压、水质数据可视化和分析
- 阀门和水泵状态同步与控制
- 边缘计算与本地决策
- 历史数据存储与查询

## 安装与运行

1. 安装依赖：
```
pip install -r requirements.txt
```

2. 启动云端服务：
```
python cloud/app.py
```

3. 启动边缘节点：
```
python edge/edge_node.py
```

4. 启动模拟设备：
```
python device/device_simulator.py
```

## 系统访问

- 云端服务界面：http://localhost:5000
- API文档：http://localhost:5000/api/docs 