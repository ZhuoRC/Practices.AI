#!/usr/bin/env python3
"""
GPU Detection and Diagnostic Tool
GPU 检测和诊断工具

For DeepSeek-OCR project
用于 DeepSeek-OCR 项目
"""
import sys
import subprocess
import platform

def check_nvidia_driver():
    """Check NVIDIA driver / 检查 NVIDIA 驱动"""
    print("[INFO] Checking NVIDIA driver... / 检查 NVIDIA 驱动...")
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("[OK] NVIDIA driver is installed / NVIDIA 驱动已安装")
                print("[OUTPUT] nvidia-smi output / nvidia-smi 输出:")
                print(result.stdout)
                return True
            else:
                print("[ERROR] NVIDIA driver not properly installed / NVIDIA 驱动未正确安装")
                return False
        else:
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("[OK] NVIDIA driver is installed / NVIDIA 驱动已安装")
                print(result.stdout)
                return True
            else:
                print("[ERROR] NVIDIA driver not properly installed / NVIDIA 驱动未正确安装")
                return False
    except subprocess.TimeoutExpired:
        print("[ERROR] nvidia-smi command timeout / nvidia-smi 命令超时")
        return False
    except FileNotFoundError:
        print("[ERROR] nvidia-smi command not found / nvidia-smi 命令未找到")
        return False
    except Exception as e:
        print(f"[ERROR] Error checking driver / 检查驱动时出错: {e}")
        return False

def check_pytorch_cuda():
    """Check PyTorch CUDA support / 检查 PyTorch CUDA 支持"""
    print("\n[INFO] Checking PyTorch CUDA support... / 检查 PyTorch CUDA 支持...")
    try:
        import torch
        print(f"[OK] PyTorch version / PyTorch 版本: {torch.__version__}")
        print(f"[INFO] CUDA compile version / CUDA 编译版本: {torch.version.cuda}")

        cuda_available = torch.cuda.is_available()
        print(f"[INFO] CUDA available / CUDA 可用: {cuda_available}")

        if cuda_available:
            device_count = torch.cuda.device_count()
            print(f"[INFO] GPU device count / GPU 设备数量: {device_count}")

            for i in range(device_count):
                device_name = torch.cuda.get_device_name(i)
                device_capability = torch.cuda.get_device_capability(i)
                device_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                print(f"  GPU {i}: {device_name}")
                print(f"    Compute capability / 计算能力: {device_capability}")
                print(f"    VRAM / 显存: {device_memory:.1f} GB")

                # Test simple CUDA operation / 测试简单的 CUDA 操作
                try:
                    x = torch.randn(1000, 1000).cuda()
                    y = x @ x
                    print(f"    [OK] CUDA test passed / CUDA 测试通过")
                except Exception as e:
                    print(f"    [ERROR] CUDA test failed / CUDA 测试失败: {e}")
        else:
            print("[ERROR] PyTorch cannot detect CUDA / PyTorch 无法检测到 CUDA")

            # Show possible reasons / 显示可能的原因
            print("\n[INFO] Possible reasons / 可能的原因:")
            print("1. NVIDIA driver not installed / 未安装 NVIDIA 驱动")
            print("2. CPU-only version of PyTorch installed / 安装了 CPU 版本的 PyTorch")
            print("3. CUDA version mismatch / CUDA 版本不匹配")
            print("4. NVIDIA driver version too old / NVIDIA 驱动版本过旧")

        return cuda_available

    except ImportError:
        print("[ERROR] PyTorch not installed / PyTorch 未安装")
        return False
    except Exception as e:
        print(f"[ERROR] Error checking PyTorch / 检查 PyTorch 时出错: {e}")
        return False

def check_flash_attention():
    """Check Flash Attention installation / 检查 Flash Attention 安装"""
    print("\n[INFO] Checking Flash Attention (REQUIRED for DeepSeek-OCR)...")
    print("[INFO] 检查 Flash Attention（DeepSeek-OCR 必需）...")
    try:
        import flash_attn
        print(f"[OK] Flash Attention version / Flash Attention 版本: {flash_attn.__version__}")
        return True
    except ImportError:
        print("[ERROR] Flash Attention not installed / Flash Attention 未安装")
        print("[SUGGEST] Install with / 安装命令:")
        print("  pip install flash-attn==2.7.3 --no-build-isolation")
        return False
    except Exception as e:
        print(f"[ERROR] Error checking Flash Attention / 检查 Flash Attention 时出错: {e}")
        return False

def check_transformers():
    """Check transformers library / 检查 transformers 库"""
    print("\n[INFO] Checking transformers library... / 检查 transformers 库...")
    try:
        import transformers
        print(f"[OK] transformers version / transformers 版本: {transformers.__version__}")

        # Check if version is compatible / 检查版本是否兼容
        required_version = "4.46.3"
        if transformers.__version__ >= required_version:
            print(f"[OK] Version is compatible (>= {required_version}) / 版本兼容 (>= {required_version})")
        else:
            print(f"[WARN] Version {transformers.__version__} may not be compatible / 版本 {transformers.__version__} 可能不兼容")
            print(f"[SUGGEST] Recommended version / 推荐版本: {required_version}")
        return True
    except ImportError:
        print("[ERROR] transformers not installed / transformers 未安装")
        return False
    except Exception as e:
        print(f"[ERROR] Error checking transformers / 检查 transformers 时出错: {e}")
        return False

def check_other_dependencies():
    """Check other required dependencies / 检查其他必需依赖"""
    print("\n[INFO] Checking other dependencies... / 检查其他依赖...")

    dependencies = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "Pillow": "Pillow (PIL)",
        "einops": "einops",
        "addict": "addict",
        "easydict": "easydict"
    }

    all_installed = True
    for module_name, display_name in dependencies.items():
        try:
            if module_name == "Pillow":
                import PIL
                print(f"[OK] {display_name} version / 版本: {PIL.__version__}")
            else:
                module = __import__(module_name)
                version = getattr(module, '__version__', 'unknown')
                print(f"[OK] {display_name} version / 版本: {version}")
        except ImportError:
            print(f"[ERROR] {display_name} not installed / 未安装")
            all_installed = False
        except Exception as e:
            print(f"[WARN] Error checking {display_name} / 检查 {display_name} 时出错: {e}")

    return all_installed

def check_system_info():
    """Check system information / 检查系统信息"""
    print("\n[INFO] System information / 系统信息:")
    print(f"[INFO] Operating system / 操作系统: {platform.system()} {platform.release()}")
    print(f"[INFO] Python version / Python 版本: {sys.version}")

    if platform.system() == "Windows":
        try:
            import wmi
            c = wmi.WMI()
            for gpu in c.Win32_VideoController():
                print(f"[INFO] Graphics card / 显卡: {gpu.Name}")
        except ImportError:
            print("[INFO] Tip: Install wmi module for GPU info (pip install wmi)")
            print("[INFO] 提示: 安装 wmi 模块可查看显卡信息 (pip install wmi)")
        except Exception as e:
            print(f"[ERROR] Failed to get GPU info / 获取显卡信息失败: {e}")

def main():
    print("=" * 70)
    print("    GPU Detection and Diagnostic Tool for DeepSeek-OCR")
    print("    GPU 检测和诊断工具 - DeepSeek-OCR")
    print("=" * 70)

    check_system_info()

    driver_ok = check_nvidia_driver()
    pytorch_ok = check_pytorch_cuda()
    flash_attn_ok = check_flash_attention()
    transformers_ok = check_transformers()
    deps_ok = check_other_dependencies()

    print("\n" + "=" * 70)
    print("[RESULT] Diagnostic results / 诊断结果:")
    print("=" * 70)

    if driver_ok and pytorch_ok and flash_attn_ok and transformers_ok and deps_ok:
        print("[OK] GPU environment is properly configured! / GPU 环境配置正确！")
        print("[OK] You can use GPU acceleration / 可以使用 GPU 加速")
        print("[OK] DeepSeek-OCR is ready to run / DeepSeek-OCR 已准备就绪")
    else:
        print("[WARN] Some components are missing or not properly configured")
        print("[WARN] 某些组件缺失或未正确配置")
        print("\n[SUGGEST] Recommendations / 建议:")

        if not driver_ok:
            print("\n1. NVIDIA Driver / NVIDIA 驱动:")
            print("   - Install or update NVIDIA driver / 安装或更新 NVIDIA 驱动")
            print("   - https://www.nvidia.com/drivers")

        if not pytorch_ok:
            print("\n2. PyTorch with CUDA / 支持 CUDA 的 PyTorch:")
            print("   - Uninstall current version / 卸载当前版本:")
            print("     pip uninstall torch torchvision torchaudio")
            print("   - Install CUDA version / 安装 CUDA 版本:")
            print("     pip install torch==2.5.1+cu121 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")

        if not flash_attn_ok:
            print("\n3. Flash Attention (CRITICAL for DeepSeek-OCR) / Flash Attention（DeepSeek-OCR 必需）:")
            print("   - Install with / 安装命令:")
            print("     pip install flash-attn==2.7.3 --no-build-isolation")
            print("   - Note: This may take 5-10 minutes to compile / 注意：编译可能需要 5-10 分钟")

        if not transformers_ok:
            print("\n4. Transformers library / Transformers 库:")
            print("   - Install with / 安装命令:")
            print("     pip install transformers==4.46.3")

        if not deps_ok:
            print("\n5. Other dependencies / 其他依赖:")
            print("   - Install with / 安装命令:")
            print("     pip install -r requirements.txt")

    print("\n[INFO] For more information, see / 更多信息请参阅: docs/QUICK_START.md")

if __name__ == "__main__":
    main()
