import os
import base64
import logging
import tempfile
import subprocess
import sys

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    # Get bot code from environment variable
    bot_code_b64 = os.getenv("BOT_CODE_B64")
    bot_token = os.getenv("BOT_TOKEN")

    if not bot_code_b64:
        logger.error("BOT_CODE_B64 environment variable not set!")
        sys.exit(1)

    if not bot_token:
        logger.error("BOT_TOKEN environment variable not set!")
        sys.exit(1)

    logger.info("Decoding bot code...")

    # Decode base64 code
    try:
        bot_code = base64.b64decode(bot_code_b64).decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to decode bot code: {e}")
        sys.exit(1)

    # Write code to file
    bot_file = "/app/userbot.py"
    with open(bot_file, 'w') as f:
        f.write(bot_code)

    logger.info(f"Bot code written to {bot_file}")
    logger.info("Starting bot...")

    # Run the bot
    try:
        exec(compile(bot_code, 'userbot.py', 'exec'), {
            '__name__': '__main__',
            'BOT_TOKEN': bot_token
        })
    except Exception as e:
        logger.error(f"Bot execution error: {e}")
        # Try running as subprocess instead
        try:
            result = subprocess.run(
                [sys.executable, bot_file],
                env={**os.environ, 'BOT_TOKEN': bot_token},
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Subprocess error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
