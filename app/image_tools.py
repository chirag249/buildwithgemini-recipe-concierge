import time
import os
from typing import Optional
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

GCS_BUCKET_NAME = "recipe-concierge-media-qwiklabs-gcp-01-0f8258c0f681"
GCP_PROJECT_ID = "qwiklabs-gcp-01-0f8258c0f681"

def generate_recipe_image(
    prompt: str,
    filename: Optional[str] = "generated_recipe.png",
    tool_context: Optional[ToolContext] = None
) -> str:
    """Generate a photo of a dish/recipe using gemini-3.1-flash-lite-image, save as artifact, and upload to GCS.

    Args:
        prompt: Description of the dish or food item to generate an image for.
        filename: Optional filename for saving the artifact and storage object.
        tool_context: Framework-injected ToolContext used to save artifacts.

    Returns:
        A string containing the public HTTPS URL of the uploaded image on Cloud Storage.
    """
    safe_filename = filename if filename else "generated_recipe.png"
    if not safe_filename.endswith((".png", ".jpg", ".jpeg")):
        safe_filename = f"{safe_filename}.png"

    try:
        # 1. Generate image with gemini-3.1-flash-lite-image in location='global'
        genai_client = genai.Client(
            vertexai=True,
            project=GCP_PROJECT_ID,
            location="global"
        )

        response = genai_client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=f"Professional food photography of: {prompt}",
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )

        image_bytes = None
        mime_type = "image/png"

        if response.parts:
            for part in response.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/png"
                    break

        if not image_bytes:
            return "Failed to generate image: Response did not contain inline image bytes."

        # 2. Save artifact to Playground's Artifacts panel via tool_context
        if tool_context is not None:
            try:
                artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                tool_context.save_artifact(filename=safe_filename, artifact=artifact_part)
            except Exception as e:
                print(f"Artifact save warning: {e}")

        # 3. Upload image bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=GCP_PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)

        timestamp = int(time.time())
        object_name = f"recipe_images/{timestamp}_{safe_filename}"
        blob = bucket.blob(object_name)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{object_name}"
        return (
            f"🖼️ Generated recipe image successfully!\n"
            f"Public Image URL: {public_url}"
        )

    except Exception as e:
        return f"Error generating or uploading recipe image: {str(e)}"
