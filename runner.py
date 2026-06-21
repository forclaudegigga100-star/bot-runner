import os
import base64
import logging
import subprocess
import sys

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def clean_code(code: str) -> str:
    """Remove markdown code blocks if present"""
    code = code.strip()
    # Remove ```python or ``` wrapper
    if code.startswith("```"):
        lines = code.split('\n')
        lines = lines[1:]  # Remove first line with ```
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        code = '\n'.join(lines)
    return code.strip()

def fix_encoding(code: str) -> str:
    """Fix any encoding issues in the code"""
    # Add encoding declaration at top if not present
    if '# -*- coding:' not in code and '# coding:' not in code:
        code = '# -*- coding: utf-8 -*-\n' + code
    return code

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

    # Clean and fix code
    bot_code = clean_code(bot_code)
    bot_code = fix_encoding(bot_code)
    
    logger.info(f"Code starts with: {bot_code[:100]}")

    # Write to file with utf-8 encoding
    bot_file = "/app/userbot.py"
    with open(bot_file, 'w', encoding='utf-8') as f:
        f.write(bot_code)

    logger.info("Starting bot...")
    
    # Set environment
    env = {**os.environ, 'BOT_TOKEN': bot_token, 'PYTHONIOENCODING': 'utf-8'}
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                [sys.executable, '-u', bot_file],
                env=env,
                check=True
            )
            break
        except subprocess.CalledProcessError as e:
            logger.error(f"Bot error on attempt {attempt+1}: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(5)
            else:
                logger.error("All retries failed!")
                sys.exit(1)

if __name__ == "__main__":
    main()
