import subprocess
import sys

def update_paddle():
    """更新 PaddlePaddle 到兼容版本"""
    try:
        print("开始更新 PaddlePaddle...")
        
        # 先卸载现有版本
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "paddlepaddle", "-y"])
        
        # 安装兼容版本
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "pip", 
            "install", 
            "paddlepaddle==2.4.2",
            "-i", 
            "https://mirror.baidu.com/pypi/simple"
        ])
        
        print("PaddlePaddle 更新完成！")
        
    except Exception as e:
        print(f"更新过程出现错误: {str(e)}")

if __name__ == "__main__":
    update_paddle() 