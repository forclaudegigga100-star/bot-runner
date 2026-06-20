import os
import base64
import logging
import subprocess
import sys
import re

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def clean_code(code: str) -> str:
    """Remove markdown code blocks if present"""
    # Remove ```python or ``` at start
    code = code.strip()
    if code.startswith("```"):
        # Remove first line (```python or ```)
        lines = code.split('\n')
        lines = lines[1:]  # Remove first line
        # Remove last ``` if present
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        code = '\n'.join(lines)
    return code.strip()

def main():
    bot_code_b64 = os.getenv("BOT_CODE_B64")
    bot_token = os.getenv("BOT_TOKEN")

    if not bot_code_b64:
        logger.error("BOT_CODE_B64 not set!")
        sys.exit(1)

    if not bot_token:
        logger.error("BOT_TOKEN not set!")
        sys.exit(1)

    logger.info("Decoding bot code...")
    try:
        bot_code = base64.b64decode(bot_code_b64).decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to decode: {e}")
        sys.exit(1)

    # Clean markdown backticks
    bot_code = clean_code(bot_code)
    logger.info(f"Code starts with: {bot_code[:50]}")

    # Write to file
    bot_file = "/app/userbot.py"
    with open(bot_file, 'w') as f:
        f.write(bot_code)

    logger.info("Starting bot...")
    try:
        result = subprocess.run(
            [sys.executable, bot_file],
            env={**os.environ, 'BOT_TOKEN': bot_token},
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Bot error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
