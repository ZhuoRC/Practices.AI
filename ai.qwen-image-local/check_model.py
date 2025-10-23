import torch
print(torch.__version__)
print(torch.version.cuda)
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))


# from transformers import AutoModelForImageGeneration, AutoTokenizer

# model = AutoModelForImageGeneration.from_pretrained(
#     "Qwen/Qwen2.5-VL",
#     torch_dtype=torch.float32,   # 改为 float32 试试
#     device_map="auto"
# )




