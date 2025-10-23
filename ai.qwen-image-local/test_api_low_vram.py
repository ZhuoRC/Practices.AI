#!/usr/bin/env python3
"""
Low VRAM Test Client for Qwen-Image API
Uses conservative settings to avoid OOM errors
"""
import requests
import time

API_URL = "http://localhost:8000"

def print_separator(char="=", length=60):
    print(char * length)

def test_health():
    """Test health endpoint and show memory stats"""
    print_separator()
    print("Health Check")
    print_separator()

    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {data.get('status')}")
            print(f"✓ Device: {data.get('device')}")

            if 'gpu_memory_total' in data:
                print(f"\nGPU Information:")
                print(f"  Name: {data.get('gpu_name')}")
                print(f"  Total: {data.get('gpu_memory_total')}")
                print(f"  Allocated: {data.get('gpu_memory_allocated')}")
                print(f"  Free: {data.get('gpu_memory_free')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print()

def cleanup_memory():
    """Call the cleanup endpoint"""
    try:
        response = requests.post(f"{API_URL}/cleanup")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Memory cleanup: {data.get('message')}")
            if 'gpu_memory_allocated' in data:
                print(f"  Allocated: {data.get('gpu_memory_allocated')}")
    except Exception as e:
        print(f"⚠ Cleanup warning: {e}")

def generate_test_image(name, prompt, width=512, height=512, steps=20, **kwargs):
    """
    Generate a test image with safe default settings

    Args:
        name: Test name
        prompt: Image prompt
        width: Image width (default: 512 - safe for 6GB GPUs)
        height: Image height (default: 512)
        steps: Inference steps (default: 20 - safe and fast)
    """
    print_separator()
    print(f"Test: {name}")
    print_separator()
    print(f"Prompt: {prompt}")
    print(f"Size: {width}x{height}")
    print(f"Steps: {steps}")

    # Prepare request
    data = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_inference_steps": steps,
        **kwargs
    }

    # Cleanup before generation
    print("\nCleaning up memory before generation...")
    cleanup_memory()

    # Start timer
    print("\nGenerating image...")
    start_time = time.time()

    try:
        response = requests.post(
            f"{API_URL}/generate",
            json=data,
            timeout=300  # 5 minute timeout
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            # Save image
            filename = f"test_{name.lower().replace(' ', '_')}.png"
            with open(filename, "wb") as f:
                f.write(response.content)

            print(f"✓ Success! Generated in {elapsed:.1f}s")
            print(f"✓ Saved to: {filename}")
            return True

        elif response.status_code == 507:
            # OOM error
            error_data = response.json()
            print(f"\n❌ OUT OF MEMORY ERROR")
            print(f"\nError: {error_data.get('detail', {}).get('message')}")

            suggestions = error_data.get('detail', {}).get('suggestions', [])
            if suggestions:
                print(f"\n💡 Suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"   {i}. {suggestion}")

            print(f"\n⚠ This test failed. Try reducing size or steps.")
            return False

        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ Request timeout (>5 minutes)")
        print(f"   Generation may be too slow. Try reducing size/steps.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        print()

def main():
    print_separator("=")
    print("Qwen-Image Low VRAM Test Suite")
    print_separator("=")
    print()

    # Check server health
    test_health()

    # Test 1: Minimal settings (should work on 6GB GPU)
    test1 = generate_test_image(
        name="Minimal (512x512, 20 steps)",
        prompt="A serene mountain landscape at sunset",
        width=512,
        height=512,
        steps=20,
        seed=42
    )

    if not test1:
        print("⚠ First test failed. Stopping here.")
        print("  Please check MEMORY_GUIDE.md for troubleshooting.")
        return

    # Test 2: Slightly larger (should work on 8GB GPU)
    test2 = generate_test_image(
        name="Medium (768x768, 25 steps)",
        prompt="A futuristic cityscape with neon lights",
        width=768,
        height=768,
        steps=25,
        seed=123
    )

    if not test2:
        print("⚠ Medium test failed. Your GPU may have 6-8GB VRAM.")
        print("  Stick to 512x512 or smaller for best results.")
        print()

    # Test 3: Larger image (may fail on <10GB GPU)
    if test2:
        print("✓ Medium test passed! Trying larger image...")
        test3 = generate_test_image(
            name="Large (1024x1024, 30 steps)",
            prompt="A magical forest with glowing mushrooms and fireflies",
            width=1024,
            height=1024,
            steps=30,
            seed=456
        )

        if not test3:
            print("⚠ Large test failed. Your GPU VRAM is likely 8-10GB.")
            print("  For 1024x1024 images, reduce steps or use smaller sizes.")
            print()

    # Test 4: Chinese prompt (if medium test passed)
    if test2:
        generate_test_image(
            name="Chinese Prompt",
            prompt="一只可爱的熊猫在竹林中",
            width=768,
            height=768,
            steps=25,
            seed=789
        )

    # Final health check
    print_separator("=")
    print("Final Health Check")
    print_separator("=")
    test_health()

    print_separator("=")
    print("Test Suite Complete!")
    print_separator("=")
    print("\n💡 Tips:")
    print("  - If tests failed, try the Low VRAM version API")
    print("  - Start with 512x512 and 20 steps")
    print("  - Check MEMORY_GUIDE.md for detailed help")
    print("  - Close other GPU applications")
    print()

if __name__ == "__main__":
    main()
