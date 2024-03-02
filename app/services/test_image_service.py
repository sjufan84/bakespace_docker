import unittest
import asyncio
from unittest.mock import patch, MagicMock
from image_service import create_image_string, get_image_prompt

class TestImageService(unittest.TestCase):

    @patch('image_service.OpenAI')
    async def test_create_image_string(self, mock_openai):
        # Arrange
        mock_openai.images.generate.return_value = MagicMock(data=[MagicMock(b64_json="test_image")])
        prompt = "Test prompt"

        # Act
        result = await create_image_string(prompt)

        # Assert
        self.assertEqual(result, "test_image")
        mock_openai.images.generate.assert_called_once_with(
            prompt=prompt,
            model="dall-e-3",
            size="1024x1024",
            quality="hd",
            n=1,
            response_format="b64_json"
        )

    @patch('image_service.OpenAI')
    async def test_get_image_prompt(self, mock_openai):
        # Arrange
        mock_openai.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="Test prompt"))])
        recipe = "Test recipe"

        # Act
        result = await get_image_prompt(recipe)

        # Assert
        self.assertEqual(result, "Test prompt")
        mock_openai.chat.completions.create.assert_called_once()

if __name__ == '__main__':
    asyncio.run(unittest.main())
