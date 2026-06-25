# SAS4XL - Local SAS to Python translation

Local SAS to Python translation using llama.app. No cloud. No API keys.

## Quick Start

1. Install llama.app:
   curl -fsSL https://llama.app/install.sh | sh

2. Start the server:
   llama serve -m ~/x4sas_models/qwen2.5-coder-7b.gguf -ngl 99 --port 8080

3. Translate:
   python sas2py_router.py your_file.sas

## License: MIT
