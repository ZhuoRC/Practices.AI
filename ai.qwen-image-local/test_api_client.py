#!/usr/bin/env python3
"""
Example client for Qwen-Image API
Demonstrates how to use the API to generate images
"""
import requests
import base64
from pathlib import Path

# API endpoint
API_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def generate_image_binary(prompt, output_path="generated_image.png", **kwargs):
    """
    Generate an image and save it as a file (binary response)

    Args:
        prompt: Text prompt for image generation
        output_path: Path to save the generated image
        **kwargs: Additional parameters (width, height, seed, etc.)
    """
    print(f"Generating image with prompt: '{prompt}'")

    # Prepare request data
    data = {
        "prompt": prompt,
        "return_base64": False,
        **kwargs
    }

    # Make request
    response = requests.post(f"{API_URL}/generate", json=data)

    if response.status_code == 200:
        # Save the image
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Image saved to: {output_path}\n")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Details: {response.text}\n")
        return False

def generate_image_base64(prompt, output_path="generated_image_b64.png", **kwargs):
    """
    Generate an image and receive it as base64 (JSON response)

    Args:
        prompt: Text prompt for image generation
        output_path: Path to save the generated image
        **kwargs: Additional parameters (width, height, seed, etc.)
    """
    print(f"Generating image (base64) with prompt: '{prompt}'")

    # Prepare request data
    data = {
        "prompt": prompt,
        "return_base64": True,
        **kwargs
    }

    # Make request
    response = requests.post(f"{API_URL}/generate", json=data)

    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            # Decode base64 and save
            img_data = base64.b64decode(result["image_base64"])
            with open(output_path, "wb") as f:
                f.write(img_data)
            print(f"✅ Image saved to: {output_path}\n")
            return True
        else:
            print(f"❌ Generation failed: {result['message']}\n")
            return False
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Details: {response.text}\n")
        return False

def main():
    print("=" * 60)
    print("Qwen-Image API Client Example")
    print("=" * 60 + "\n")

    # Test health check
    test_health_check()

    # Example 1: Basic image generation (binary response)
    generate_image_binary(
        prompt="A serene landscape with mountains and a lake at sunset",
        output_path="example1_landscape.png"
    )

    # Example 2: Image generation with custom parameters
    generate_image_binary(
        prompt="A futuristic city with flying cars",
        output_path="example2_futuristic.png",
        width=1280,
        height=720,
        num_inference_steps=50,
        seed=42
    )

    # Example 3: Image generation with base64 response
    generate_image_base64(
        prompt="A cute cat playing with a ball of yarn",
        output_path="example3_cat.png",
        width=1024,
        height=1024
    )

    # Example 4: Chinese prompt
    generate_image_binary(
        prompt="一只可爱的熊猫在竹林中吃竹子",
        output_path="example4_panda.png"
    )

    # Example 5: Custom parameters with no prompt enhancement
    generate_image_binary(
        prompt="Abstract art with vibrant colors",
        output_path="example5_abstract.png",
        enhance_prompt=False,
        true_cfg_scale=5.0
    )

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
