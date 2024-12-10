import openai
import base64

# Set your OpenAI API key
#openai.api_key = ''


def generate_image(prompt, output_file="generated_image.png"):
    """
    Generate an image using OpenAI's DALL·E model and save it to a file.

    Args:
        prompt (str): The text prompt for the image.
        output_file (str): The name of the file to save the generated image.
    """
    try:
        # Call OpenAI's image generation API
        response = openai.Image.create(
            prompt=prompt,
            n=1,  # Number of images to generate
            size="512x512",  # Image size (e.g., 256x256, 512x512, 1024x1024)
            response_format="b64_json"  # Get the image in base64 format
        )
        # Extract the base64-encoded image
        image_data = response["data"][0]["b64_json"]

        # Decode the image and save it to a file
        with open(output_file, "wb") as image_file:
            image_file.write(base64.b64decode(image_data))

        print(f"Image successfully generated and saved as '{output_file}'.")
    except Exception as e:
        print(f"Error generating image: {e}")


if __name__ == "__main__":
    prompt = "A fantasy warrior in a vibrant forest, detailed and cinematic"
    generate_image(prompt)
