import subprocess
import sys

def install_package(package):
    """安装Python包"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    """安装所有依赖"""
    packages = [
        "flask>=2.0.0",
        "requests>=2.25.0",
        "python-dateutil>=2.8.0"
    ]
    
    print("开始安装依赖包...")
    
    for package in packages:
        try:
            print(f"正在安装 {package}...")
            install_package(package)
            print(f"{package} 安装成功")
        except Exception as e:
            print(f"{package} 安装失败: {e}")
    
    print("依赖安装完成!")

if __name__ == "__main__":
    main() 