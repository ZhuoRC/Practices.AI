# Image Editing Guide - Qwen-Image-Edit-2509

A comprehensive guide to using the Qwen-Image-Edit API for image editing tasks.

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Capabilities](#capabilities)
- [Prompt Engineering](#prompt-engineering)
- [Parameters Guide](#parameters-guide)
- [Common Use Cases](#common-use-cases)
- [Tips and Best Practices](#tips-and-best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The Qwen-Image-Edit-2509 model is built on the 20B Qwen-Image foundation and specializes in:
- Text-guided image editing
- Style transfer and enhancement
- Object addition/removal
- Lighting and color adjustments
- Detail enhancement
- Multi-image input support (1-3 images)

## Quick Start

### Basic Editing Example

```python
import requests

# Simple edit with file upload
with open("photo.png", "rb") as f:
    response = requests.post(
        "http://localhost:8021/edit",
        files={"image": f},
        data={"prompt": "make the sunset more vibrant"}
    )

with open("edited_photo.png", "wb") as f:
    f.write(response.content)
```

### Using cURL

```bash
curl -X POST "http://localhost:8021/edit" \
  -F "image=@photo.png" \
  -F "prompt=enhance colors and add dramatic lighting" \
  --output edited_photo.png
```

## Capabilities

### 1. Style Transfer

Change the artistic style of an image:

```python
{
    "prompt": "convert to oil painting style",
    "guidance_scale": 8.0,
    "num_inference_steps": 50
}
```

**Example prompts:**
- "convert to watercolor painting"
- "make it look like a sketch"
- "apply anime art style"
- "transform into pixel art"

### 2. Object Modification

Add, remove, or modify objects:

```python
{
    "prompt": "add a rainbow in the sky",
    "guidance_scale": 7.5,
    "num_inference_steps": 50
}
```

**Example prompts:**
- "remove the person in the background"
- "add flowers in the foreground"
- "replace the car with a bicycle"
- "add clouds to the sky"

### 3. Lighting and Atmosphere

Adjust lighting, time of day, and atmosphere:

```python
{
    "prompt": "change to golden hour lighting",
    "guidance_scale": 7.0,
    "num_inference_steps": 40
}
```

**Example prompts:**
- "add dramatic sunset lighting"
- "make it look like midnight"
- "add fog and mist"
- "brighten the scene with sunlight"

### 4. Color and Tone Adjustment

Modify colors and overall tone:

```python
{
    "prompt": "increase saturation and make colors more vibrant",
    "guidance_scale": 6.0,
    "num_inference_steps": 40
}
```

**Example prompts:**
- "convert to black and white"
- "add warm tones"
- "make colors cooler and more blue"
- "increase contrast and vibrancy"

### 5. Detail Enhancement

Enhance or modify details:

```python
{
    "prompt": "enhance details and sharpness",
    "guidance_scale": 5.0,
    "num_inference_steps": 50
}
```

**Example prompts:**
- "add more texture and detail"
- "make it more photorealistic"
- "soften and blur the background"
- "enhance facial features"

## Prompt Engineering

### Effective Prompt Structure

**Good prompts are:**
1. **Specific**: "add golden hour sunset lighting" vs "make it better"
2. **Descriptive**: "convert to impressionist oil painting with visible brush strokes"
3. **Action-oriented**: Start with verbs (add, remove, change, enhance, convert)

### Prompt Templates

**For Style Changes:**
```
"convert to [style] style with [characteristics]"
Example: "convert to vintage film style with grain and warm tones"
```

**For Object Modifications:**
```
"[add/remove/replace] [object] [location/details]"
Example: "add cherry blossoms in the foreground with soft pink petals"
```

**For Lighting:**
```
"change lighting to [description] with [effects]"
Example: "change lighting to dramatic sunset with warm orange glow"
```

**For Color Adjustments:**
```
"adjust colors to [description]"
Example: "adjust colors to cool blue tones with high contrast"
```

### Multi-Step Prompts

For complex edits, combine multiple aspects:

```
"add sunset lighting, increase saturation, and add clouds to the sky"
```

## Parameters Guide

### `guidance_scale`

Controls how closely the edit follows your prompt.

- **Low (3-5)**: Subtle changes, preserves more of the original
- **Medium (6-8)**: Balanced changes (recommended starting point)
- **High (9-15)**: Strong changes, more creative interpretation

**Example:**
```python
# Subtle edit
{"prompt": "add warm tones", "guidance_scale": 4.0}

# Moderate edit
{"prompt": "add warm tones", "guidance_scale": 7.5}

# Strong edit
{"prompt": "add warm tones", "guidance_scale": 12.0}
```

### `num_inference_steps`

Controls quality and processing time.

- **Fast (15-25)**: Quick edits, lower quality
- **Balanced (30-40)**: Good quality/speed balance
- **High Quality (50-70)**: Best quality, slower

**Recommendations:**
- **Quick tests**: 20 steps
- **Production use**: 40-50 steps
- **Critical quality**: 60-70 steps

### `seed`

Use seeds for reproducibility:

```python
{
    "prompt": "add dramatic lighting",
    "seed": 42,  # Same seed = same result
    "num_inference_steps": 50
}
```

### `width` and `height`

Control output dimensions:

```python
{
    "prompt": "enhance details",
    "width": 1024,   # None = keep original size
    "height": 1024
}
```

**Memory considerations:**
- **Low VRAM**: Max 768x768
- **Standard**: Up to 1024x1024
- Larger sizes may cause OOM errors

### `negative_prompt`

Specify what to avoid:

```python
{
    "prompt": "add sunset colors",
    "negative_prompt": "blurry, distorted, low quality, artifacts, watermark"
}
```

**Common negative prompts:**
- "blurry, out of focus, low quality"
- "distorted, deformed, artifacts"
- "oversaturated, unnatural colors"
- "text, watermark, signature"

## Common Use Cases

### Use Case 1: Enhance a Photo

**Goal:** Improve a photo's overall quality

```python
{
    "prompt": "enhance colors, increase sharpness, improve lighting, photorealistic",
    "guidance_scale": 6.0,
    "num_inference_steps": 50,
    "negative_prompt": "blurry, low quality, artifacts"
}
```

### Use Case 2: Change Time of Day

**Goal:** Transform day scene to night

```python
{
    "prompt": "change to nighttime scene with moonlight and stars",
    "guidance_scale": 8.0,
    "num_inference_steps": 50,
    "negative_prompt": "daytime, sunlight"
}
```

### Use Case 3: Artistic Style Transfer

**Goal:** Convert photo to painting

```python
{
    "prompt": "convert to impressionist oil painting with visible brush strokes and vibrant colors",
    "guidance_scale": 9.0,
    "num_inference_steps": 60,
    "negative_prompt": "photorealistic, digital, photograph"
}
```

### Use Case 4: Background Modification

**Goal:** Change the background

```python
{
    "prompt": "change background to mountain landscape with blue sky",
    "guidance_scale": 7.5,
    "num_inference_steps": 50,
    "negative_prompt": "blurry background"
}
```

### Use Case 5: Seasonal Transformation

**Goal:** Change summer to winter

```python
{
    "prompt": "transform to winter scene with snow, frost, and cold atmosphere",
    "guidance_scale": 8.5,
    "num_inference_steps": 60,
    "negative_prompt": "summer, warm, green leaves"
}
```

## Tips and Best Practices

### 1. Start Simple

Begin with basic edits and gradually increase complexity:

```python
# Start here
{"prompt": "enhance colors"}

# Then try
{"prompt": "enhance colors and add warm sunset lighting"}

# Finally
{"prompt": "enhance colors, add warm sunset lighting, increase contrast, and add dramatic clouds"}
```

### 2. Iterate with Seeds

Use the same seed to iterate on prompts:

```python
# First attempt
{"prompt": "add sunset", "seed": 42}

# Refine
{"prompt": "add dramatic golden sunset with orange and pink clouds", "seed": 42}
```

### 3. Adjust Guidance Scale

If edits are too subtle or too strong:

```python
# Too subtle? Increase guidance_scale
{"guidance_scale": 10.0}

# Too strong? Decrease guidance_scale
{"guidance_scale": 5.0}
```

### 4. Balance Quality and Speed

For testing:
```python
{"num_inference_steps": 20}  # Fast iterations
```

For final output:
```python
{"num_inference_steps": 50}  # High quality
```

### 5. Use Negative Prompts

Always include negative prompts to avoid common issues:

```python
{
    "negative_prompt": "blurry, distorted, low quality, artifacts, watermark, text"
}
```

### 6. Preserve Original Details

For subtle edits, use lower guidance_scale:

```python
{
    "prompt": "slightly enhance colors",
    "guidance_scale": 4.0
}
```

### 7. Test on Small Images First

For low VRAM setups, start small:

```python
{
    "width": 512,
    "height": 512,
    "num_inference_steps": 20
}
```

## Troubleshooting

### Issue: Edits Don't Match Prompt

**Solutions:**
1. Increase `guidance_scale` (try 10-12)
2. Be more specific in prompt
3. Add negative prompts for unwanted elements
4. Increase `num_inference_steps` (try 60-70)

**Example:**
```python
# Instead of:
{"prompt": "improve image"}

# Try:
{
    "prompt": "enhance colors, increase sharpness, improve lighting, add contrast",
    "guidance_scale": 10.0,
    "num_inference_steps": 60
}
```

### Issue: Result Too Different from Original

**Solutions:**
1. Decrease `guidance_scale` (try 4-5)
2. Use more conservative prompts
3. Reduce `num_inference_steps`

**Example:**
```python
{
    "prompt": "slightly enhance colors",
    "guidance_scale": 4.0,
    "num_inference_steps": 30
}
```

### Issue: Blurry or Low Quality

**Solutions:**
1. Increase `num_inference_steps` to 50-70
2. Add to negative prompt: "blurry, low quality"
3. Include "sharp, detailed, high quality" in prompt

### Issue: Out of Memory (OOM)

**Solutions:**
1. Use low VRAM version (port 8021)
2. Reduce image dimensions:
   ```python
   {"width": 512, "height": 512}
   ```
3. Reduce steps:
   ```python
   {"num_inference_steps": 20}
   ```
4. Use cleanup endpoint:
   ```bash
   curl -X POST "http://localhost:8021/cleanup"
   ```

### Issue: Unwanted Artifacts

**Solutions:**
1. Add to negative prompt: "artifacts, distorted, deformed"
2. Try different seed values
3. Reduce guidance_scale
4. Increase num_inference_steps

## Advanced Techniques

### Batch Processing

Process multiple images with the same edits:

```python
import requests
import os

prompt = "add sunset lighting and enhance colors"
params = {
    "guidance_scale": 7.5,
    "num_inference_steps": 50
}

for filename in os.listdir("input_folder"):
    if filename.endswith(".png"):
        with open(f"input_folder/{filename}", "rb") as f:
            response = requests.post(
                "http://localhost:8021/edit",
                files={"image": f},
                data={**params, "prompt": prompt}
            )

        with open(f"output_folder/{filename}", "wb") as f:
            f.write(response.content)
```

### Progressive Editing

Apply multiple edits sequentially:

```python
import requests

# Step 1: Enhance lighting
with open("original.png", "rb") as f:
    r1 = requests.post("http://localhost:8021/edit",
        files={"image": f},
        data={"prompt": "enhance lighting"})
with open("step1.png", "wb") as f:
    f.write(r1.content)

# Step 2: Add colors
with open("step1.png", "rb") as f:
    r2 = requests.post("http://localhost:8021/edit",
        files={"image": f},
        data={"prompt": "add vibrant sunset colors"})
with open("final.png", "wb") as f:
    f.write(r2.content)
```

### A/B Testing Different Edits

Compare different editing approaches:

```python
prompts = [
    "add warm sunset lighting",
    "add dramatic golden hour lighting",
    "add soft evening lighting"
]

for i, prompt in enumerate(prompts):
    with open("original.png", "rb") as f:
        response = requests.post("http://localhost:8021/edit",
            files={"image": f},
            data={"prompt": prompt, "seed": 42})

    with open(f"variant_{i}.png", "wb") as f:
        f.write(response.content)
```

## API Endpoints Summary

### Standard Version (Port 8020)
- Better quality for GPUs with 12GB+ VRAM
- Default: 50 inference steps
- Recommended for final production edits

### Low VRAM Version (Port 8021)
- Optimized for 6-10GB VRAM
- Default: 30 inference steps
- Includes `/cleanup` endpoint
- Recommended for most users

## Further Reading

- **API_USAGE.md**: Complete API reference and examples
- **QUICK_START.md**: Getting started guide
- **MEMORY_GUIDE.md**: Memory optimization tips
- **Qwen-Image GitHub**: https://github.com/QwenLM/Qwen-Image

---

**Happy editing! 🎨✨**
