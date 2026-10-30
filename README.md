# Multilingual GIF Generator

Streamlit app that turns a text prompt in **any language** into a short GIF/MP4 using [Hotshot-XL](https://github.com/hotshotco/Hotshot-XL).

## Features
- Auto-translates prompts to English (deep-translator)
- Style presets (Cartoon / Realistic / Abstract) and cultural themes (Japanese, Indian, African, European, Chinese)
- Multi-line prompts: one video per line
- Prompt-safety check with suggested alternatives
- Optional LoRA, upscale (2x/4x), and GIF-guided generation (depth / canny ControlNet)
- Edit generated GIFs: rotate, crop, zoom, speed

## Files
| File | Purpose |
|---|---|
| `app.py` | Streamlit UI |
| `helpers.py` | Translation, styling, safety check, command builder |
| `tests/test_helpers.py` | Unit tests (`python tests/test_helpers.py`) |
| `Multilingual_GIF_Generator.ipynb` | One-click Colab launcher (self-contained) |

## Run on Google Colab (recommended, needs a GPU)
1. Open `Multilingual_GIF_Generator.ipynb` in Colab, choose a GPU runtime.
2. Add your ngrok token to Colab **Secrets** as `NGROK_TOKEN`.
3. Run all cells and open the printed URL.

## Run locally (NVIDIA GPU, Python 3.10)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
git clone https://github.com/hotshotco/Hotshot-XL
pip install -r Hotshot-XL/requirements.txt
streamlit run app.py
```
Set `HOTSHOT_PATH` if Hotshot-XL is somewhere else. Never commit your ngrok token.

## Credits
Video generation: [Hotshot-XL](https://github.com/hotshotco/Hotshot-XL) (Apache-2.0). This repo contains only the front-end and launcher.
