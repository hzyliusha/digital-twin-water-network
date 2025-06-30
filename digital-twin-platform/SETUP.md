# 水网数字孪生平台安装指南

本文档提供了安装和配置水网数字孪生平台的详细步骤。

## 系统要求

- Python 3.8+
- MongoDB 4.4+
- Mosquitto MQTT 代理 2.0+

## 安装步骤

### 1. 克隆代码库

```bash
git clone https://github.com/yourusername/water-network-twin.git
cd water-network-twin
```

### 2. 创建并激活虚拟环境

#### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 安装并配置MongoDB

#### 安装MongoDB:
- Windows: 从[MongoDB官网](https://www.mongodb.com/try/download/community)下载并安装
- Linux: 使用包管理器安装，例如`sudo apt install mongodb`
- Mac: 使用Homebrew安装，`brew install mongodb-community`

#### 启动MongoDB:
- Windows: MongoDB会作为服务自动启动，或通过服务管理器启动
- Linux: `sudo systemctl start mongod`
- Mac: `brew services start mongodb-community`

### 5. 安装并配置Mosquitto MQTT代理

#### 安装Mosquitto:
- Windows: 从[Mosquitto官网](https://mosquitto.org/download/)下载并安装
- Linux: `sudo apt install mosquitto mosquitto-clients`
- Mac: `brew install mosquitto`

#### 启动Mosquitto:
- Windows: Mosquitto会作为服务自动启动，或通过服务管理器启动
- Linux: `sudo systemctl start mosquitto`
- Mac: `brew services start mosquitto`

### 6. 配置系统

编辑`config/config.py`文件，根据您的环境设置以下参数：

```python
# 数据库配置
DB_CONFIG = {
    'host': 'localhost',  # MongoDB主机
    'port': 27017,        # MongoDB端口
    'db_name': 'water_network_twin'
}

# MQTT配置
MQTT_CONFIG = {
    'broker': 'localhost',  # MQTT代理主机
    'port': 1883            # MQTT代理端口
}

# 云端服务配置
CLOUD_CONFIG = {
    'host': '0.0.0.0',  # 监听所有网络接口
    'port': 5000,       # Web服务端口
    'debug': True       # 开发模式下设为True，生产环境设为False
}
```

## 启动系统

### 使用启动脚本

启动脚本提供了多种启动选项，可以选择性地启动系统的不同组件：

```bash
# 启动所有组件
python start.py --all

# 或者选择性启动组件
python start.py --mqtt --cloud  # 仅启动MQTT代理和云端服务
python start.py --edge --device  # 仅启动边缘节点和设备模拟器
```

### 单独启动组件

也可以单独启动各个组件：

```bash
# 启动云端服务
python cloud/app.py

# 启动边缘节点
python edge/edge_node.py

# 启动设备模拟器
python device/device_simulator.py
```

## 访问系统

启动成功后，可以通过浏览器访问以下地址：

- Web界面: http://localhost:5000
- API文档: http://localhost:5000/api/docs

## 常见问题

### 1. MongoDB连接失败

确保MongoDB服务正在运行，并且配置文件中的主机名和端口正确。

```bash
# 检查MongoDB状态
# Windows: 检查服务管理器
# Linux:
sudo systemctl status mongod
# Mac:
brew services list
```

### 2. MQTT连接失败

确保Mosquitto服务正在运行，并且配置文件中的主机名和端口正确。

```bash
# 检查Mosquitto状态
# Windows: 检查服务管理器
# Linux:
sudo systemctl status mosquitto
# Mac:
brew services list
```

### 3. 端口冲突

如果端口已被占用，可以在配置文件中修改端口号。

## 开发与调试

### 日志文件

系统运行时会生成以下日志文件，可用于调试：

- `cloud_service.log`: 云端服务日志
- `edge_*.log`: 边缘节点日志
- `device_simulator.log`: 设备模拟器日志

### 调试模式

在开发过程中，可以启用调试模式获取更详细的输出：

```bash
# 启动云端服务（调试模式）
python cloud/app.py --debug
``` 