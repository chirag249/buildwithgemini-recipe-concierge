import asyncio
import os
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

async def record():
    output_dir = Path("/config/Desktop/BuildWithGemini/recipe-concierge/scratch/demo_video")
    output_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            record_video_dir=str(output_dir),
            record_video_size={"width": 1280, "height": 800},
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        print("Navigating to http://localhost:8080...")
        await page.goto("http://localhost:8080", wait_until="networkidle")
        await asyncio.sleep(2)

        # Prompt 1: Show database lookup for recipes
        prompt1 = "Search for pasta recipes in the database"
        print(f"Sending prompt 1: {prompt1}")
        await page.fill("#input", prompt1)
        await page.click("button")
        
        # Wait for agent response
        await asyncio.sleep(12)

        # Prompt 2: Richer prompt - Generate an image of a dish
        prompt2 = "Generate a picture of a fresh Margherita pizza"
        print(f"Sending prompt 2: {prompt2}")
        await page.fill("#input", prompt2)
        await page.click("button")

        # Wait for image generation tool call and card render
        await asyncio.sleep(18)

        # Save video path before closing context
        video_path = await page.video.path()
        print("Raw video path:", video_path)

        await context.close()
        await browser.close()

        # Copy recorded video to artifacts directory
        artifact_dir = Path("/config/.gemini/antigravity/brain/69c35a2c-f102-44e0-b908-239d7f031d8d")
        dest_video = artifact_dir / "demo_video.webm"
        shutil.copy(video_path, dest_video)
        print("Saved demo video to artifact:", dest_video)

if __name__ == "__main__":
    asyncio.run(record())
