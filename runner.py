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
    """Remove markdown and fix encoding issues"""
    code = code.strip()
    # Remove ```python or ``` wrapper
    if code.startswith("```"):
        lines = code.split('\n')
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        code = '\n'.join(lines)
    code = code.strip()
    
    # Fix non-ASCII characters in string literals
    fixed_lines = []
    for line in code.split('\n'):
        # Check if line has non-ASCII chars inside string literals
        try:
            line.encode('ascii')
            fixed_lines.append(line)
        except UnicodeEncodeError:
            # Replace non-ASCII with escaped unicode
            new_line = ''
            for char in line:
                try:
                    char.encode('ascii')
                    new_line += char
                except UnicodeEncodeError:
                    new_line += f'\\u{ord(char):04x}'
            fixed_lines.append(new_line)
    
    code = '\n'.join(fixed_lines)
    
    # Add encoding declaration
    if '# -*- coding:' not in code:
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
    logger.info(f"Code starts with: {bot_code[:100]}")

    # Write to file
    bot_file = "/app/userbot.py"
    with open(bot_file, 'w', encoding='utf-8') as f:
        f.write(bot_code)

    logger.info("Starting bot...")
    env = {**os.environ, 'BOT_TOKEN': bot_token, 'PYTHONIOENCODING': 'utf-8'}

    try:
        subprocess.run(
            [sys.executable, '-u', bot_file],
            env=env,
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
