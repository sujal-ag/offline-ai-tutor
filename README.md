# Offline AI Tutor

A small desktop application that provides an offline conversational AI tutor using a local LLM and a PyQt5 GUI.

Quick start

1. Create and activate a Python virtual environment (recommended).

2. Install dependencies (note: `torch` may require a platform-specific wheel for best results):

```bash
pip install -r requirements.txt
```

If `pip install torch` fails or you want a CPU-only wheel on Windows, see the official instructions at https://pytorch.org/get-started/locally/.

3. Run the app from the project root:

```bash
python app.py
```

Notes
- The project currently uses `transformers` + `torch` to load models (this may be memory intensive).
- `llama-cpp-python` is also listed in `requirements.txt` and can be used with smaller local GGML-style models if you prefer a lighter-weight inference backend.

Troubleshooting
- If model loading fails due to out-of-memory, try using a smaller model or configure a llama-cpp backend.
- If you hit import errors after installing requirements, double-check your active Python interpreter and virtual environment.

License

This is a personal project template. Adjust dependencies and model choices according to your environment and license constraints.
