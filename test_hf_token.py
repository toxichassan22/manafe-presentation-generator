from huggingface_hub import InferenceClient

import os

token = os.getenv("HF_TOKEN", "your_token_here")
client = InferenceClient(token=token)

def test_text_model():
    print("Testing Text Model (meta-llama/Meta-Llama-3-8B-Instruct)...")
    try:
        response = client.text_generation("What is the capital of France?", model="meta-llama/Meta-Llama-3-8B-Instruct")
        print(f"Success! Response: {response}")
    except Exception as e:
        print(f"Failed: {e}")

def test_image_model(model_id):
    print(f"\nTesting Image Model ({model_id})...")
    try:
        image = client.text_to_image("A futuristic city skyline at sunset, cyberpunk style", model=model_id)
        print(f"Success! Generated image size: {image.size}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_text_model()
    
    models_to_test = [
        "black-forest-labs/FLUX.1-schnell",
        "stabilityai/stable-diffusion-xl-base-1.0",
        "runwayml/stable-diffusion-v1-5",
        "stabilityai/stable-diffusion-3-medium-diffusers"
    ]
    
    for model in models_to_test:
        test_image_model(model)
