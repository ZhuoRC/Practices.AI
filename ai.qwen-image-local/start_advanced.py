#!/usr/bin/env python3
"""
Qwen Image API 高级启动程序
提供更多配置选项和环境检查
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_virtual_environment():
    """检查并激活虚拟环境"""
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("虚拟环境不存在，正在创建...")
        try:
            subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
            print("虚拟环境创建成功")
        except subprocess.CalledProcessError:
            print("虚拟环境创建失败")
            return False

    if os.name == "nt":  # Windows
        activate_script = ".venv\\Scripts\\activate.bat"
    else:  # Unix/Linux/Mac
        activate_script = ".venv/bin/activate"

    if os.path.exists(activate_script):
        print("虚拟环境已准备")
        return True
    else:
        print(f"激活脚本不存在: {activate_script}")
        return False


def check_dependencies():
    """检查依赖包"""
    required_packages = [
        "fastapi",
        "diffusers",
        "torch",
        "uvicorn",
        "pillow",
        "transformers",
    ]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"缺少依赖包: {', '.join(missing_packages)}")
        print("正在安装依赖包...")
        try:
            subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
            print("依赖包安装完成")
        except subprocess.CalledProcessError:
            print("依赖包安装失败")
            return False
    else:
        print("所有依赖包已安装")

    return True


def check_gpu():
    """检查 GPU 可用性"""
    try:
        import torch

        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"检测到 GPU: {gpu_name}（共 {gpu_count} 个设备）")
            return True
        else:
            print("未检测到 GPU，将使用 CPU 运行（速度较慢）")
            return False
    except ImportError:
        print("无法检测 GPU 状态")
        return False


def start_server(host="127.0.0.1", port=8000, workers=1):
    """启动 API 服务"""
    print()
    print("启动 Qwen Image API 服务...")
    print(f"服务地址: http://{host}:{port}")
    print(f"API 文档: http://{host}:{port}/docs")
    print(f"工作进程: {workers}")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 50)

    env = os.environ.copy()
    if os.name == "nt":  # Windows
        env["PATH"] = ".venv\\Scripts;" + env.get("PATH", "")

    try:
        if os.name == "nt":  # Windows
            cmd = [".venv\\Scripts\\python.exe", "run_qwen_image_api_6gb.py"]
        else:
            cmd = ["python", "run_qwen_image_api_6gb.py"]

        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\n\n服务已停止")
    except Exception as exc:
        print(f"\n服务启动失败: {exc}")


def main():
    parser = argparse.ArgumentParser(description="Qwen Image API 高级启动程序")
    parser.add_argument("--host", default="127.0.0.1", help="服务器地址 (默认: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口 (默认: 8000)")
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="工作进程数量 (默认: 1)",
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="跳过环境检查",
    )

    args = parser.parse_args()

    print("=" * 50)
    print("       Qwen Image API 高级启动程序")
    print("=" * 50)

    if not args.skip_checks:
        print("\n环境检查")
        print("-" * 30)

        if not check_virtual_environment():
            sys.exit(1)

        if not check_dependencies():
            sys.exit(1)

        check_gpu()

        print("\n环境检查完成，准备启动服务...")

    start_server(args.host, args.port, args.workers)


if __name__ == "__main__":
    main()
