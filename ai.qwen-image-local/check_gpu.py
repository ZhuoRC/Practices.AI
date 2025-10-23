#!/usr/bin/env python3
"""
GPU 检测和诊断脚本
"""
import sys
import subprocess
import platform

def check_nvidia_driver():
    """检查NVIDIA驱动"""
    print("🔍 检查 NVIDIA 驱动...")
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ NVIDIA 驱动已安装")
                print("📊 nvidia-smi 输出:")
                print(result.stdout)
                return True
            else:
                print("❌ NVIDIA 驱动未正确安装")
                return False
        else:
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ NVIDIA 驱动已安装")
                print(result.stdout)
                return True
            else:
                print("❌ NVIDIA 驱动未正确安装")
                return False
    except subprocess.TimeoutExpired:
        print("❌ nvidia-smi 命令超时")
        return False
    except FileNotFoundError:
        print("❌ nvidia-smi 命令未找到")
        return False
    except Exception as e:
        print(f"❌ 检查驱动时出错: {e}")
        return False

def check_pytorch_cuda():
    """检查 PyTorch CUDA 支持"""
    print("\n🔍 检查 PyTorch CUDA 支持...")
    try:
        import torch
        print(f"✅ PyTorch 版本: {torch.__version__}")
        print(f"🔧 CUDA 编译版本: {torch.version.cuda}")

        cuda_available = torch.cuda.is_available()
        print(f"🚀 CUDA 可用: {cuda_available}")

        if cuda_available:
            device_count = torch.cuda.device_count()
            print(f"📱 GPU 设备数量: {device_count}")

            for i in range(device_count):
                device_name = torch.cuda.get_device_name(i)
                device_capability = torch.cuda.get_device_capability(i)
                device_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                print(f"  GPU {i}: {device_name}")
                print(f"    计算能力: {device_capability}")
                print(f"    显存: {device_memory:.1f} GB")

                # 测试简单的CUDA操作
                try:
                    x = torch.randn(1000, 1000).cuda()
                    y = x @ x
                    print(f"    ✅ CUDA 测试通过")
                except Exception as e:
                    print(f"    ❌ CUDA 测试失败: {e}")
        else:
            print("❌ PyTorch 无法检测到 CUDA")

            # 显示可能的原因
            print("\n🔍 可能的原因:")
            print("1. 未安装 NVIDIA 驱动")
            print("2. 安装了 CPU 版本的 PyTorch")
            print("3. CUDA 版本不匹配")
            print("4. NVIDIA 驱动版本过旧")

        return cuda_available

    except ImportError:
        print("❌ PyTorch 未安装")
        return False
    except Exception as e:
        print(f"❌ 检查 PyTorch 时出错: {e}")
        return False

def check_system_info():
    """检查系统信息"""
    print("\n🔍 系统信息:")
    print(f"🖥️  操作系统: {platform.system()} {platform.release()}")
    print(f"🐍 Python 版本: {sys.version}")

    if platform.system() == "Windows":
        try:
            import wmi
            c = wmi.WMI()
            for gpu in c.Win32_VideoController():
                print(f"🎮 显卡: {gpu.Name}")
        except ImportError:
            print("📝 提示: 安装 wmi 模块可查看显卡信息 (pip install wmi)")
        except Exception as e:
            print(f"❌ 获取显卡信息失败: {e}")

def main():
    print("=" * 50)
    print("        GPU 检测和诊断工具")
    print("=" * 50)

    check_system_info()

    driver_ok = check_nvidia_driver()
    pytorch_ok = check_pytorch_cuda()

    print("\n" + "=" * 50)
    print("📋 诊断结果:")
    print("=" * 50)

    if driver_ok and pytorch_ok:
        print("🎉 GPU 环境配置正确！可以使用 GPU 加速")
    elif driver_ok and not pytorch_ok:
        print("⚠️  NVIDIA 驱动正常，但 PyTorch CUDA 不可用")
        print("💡 建议:")
        print("   1. 检查是否安装了 CPU 版本的 PyTorch")
        print("   2. 重新安装支持 CUDA 的 PyTorch:")
        print("      pip uninstall torch torchvision torchaudio")
        print("      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    elif not driver_ok and pytorch_ok:
        print("⚠️  PyTorch CUDA 可用，但 NVIDIA 驱动有问题")
        print("💡 建议: 重新安装或更新 NVIDIA 驱动")
    else:
        print("❌ GPU 环境配置有问题")
        print("💡 建议:")
        print("   1. 安装 NVIDIA 显卡驱动")
        print("   2. 安装支持 CUDA 的 PyTorch")
        print("   3. 确保 CUDA 版本兼容")

if __name__ == "__main__":
    main()