"""Pure helper functions (no Streamlit / GPU needed) so they can be unit-tested."""
import re
import sys

STYLE_SUFFIX = {
    "Cartoon": "cartoon style, vibrant colors, animated, playful",
    "Realistic": "realistic, photorealistic, high detail, 4K",
    "Abstract": "abstract art, surreal, colorful, imaginative",
}

THEME_SUFFIX = {
    "Japanese": "Japanese art, cherry blossoms, traditional Japanese architecture, anime style",
    "Indian": "Indian art, vibrant colors, traditional Indian patterns, Bollywood style",
    "African": "African art, tribal patterns, safari, vibrant earthy tones",
    "European": "European art, Renaissance style, classical architecture, pastel colors",
    "Chinese": "Chinese art, traditional Chinese painting, dragons, bamboo forests",
}

ABUSIVE_WORDS = ["hate", "kill", "violence", "abuse", "offensive"]


def translate_to_english(text, translator_cls=None):
    """Translate any language to English. Returns (text, error_or_None)."""
    try:
        if translator_cls is None:
            from deep_translator import GoogleTranslator as translator_cls
        out = translator_cls(source="auto", target="en").translate(text)
        return (out or text), None
    except Exception as e:  # network / rate-limit problems: fall back to original text
        return text, str(e)


def apply_style(prompt, style, language_theme):
    if style in STYLE_SUFFIX:
        prompt = f"{prompt}, {STYLE_SUFFIX[style]}"
    if language_theme in THEME_SUFFIX:
        prompt = f"{prompt}, {THEME_SUFFIX[language_theme]}"
    return prompt


def is_abusive(prompt):
    """Whole-word match, so 'skill' does not trigger 'kill'."""
    return any(re.search(rf"\b{w}\w*\b", prompt.lower()) for w in ABUSIVE_WORDS)


def safe_slug(text, n=20):
    slug = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")[:n]
    return slug or "video"


def build_command(basepath, prompt, negative_prompt, steps, seed, width, height,
                  video_frames, video_duration, scheduler, output_path,
                  upscale=0, lora_file_name="", gif_name="", control_type="depth",
                  conditioning_scale=0.8, guidance_start=0.0, guidance_end=1.0):
    """Build the inference.py command as a list (no shell, so quotes in prompts are safe)."""
    cmd = [
        sys.executable, f"{basepath}/inference.py",
        f"--prompt={prompt}",
        f"--negative_prompt={negative_prompt}",
        f"--steps={int(steps)}",
        f"--seed={int(seed)}",
        f"--width={int(width)}",
        f"--height={int(height)}",
        f"--video_length={int(video_frames)}",
        f"--video_duration={int(video_duration)}",
        f"--scheduler={scheduler}",
    ]
    if int(upscale) in (2, 4):
        cmd.append(f"--upscale={int(upscale)}")
    if lora_file_name:
        cmd.append(f"--lora={basepath}/lora/{lora_file_name}")
    if gif_name:
        cmd += [
            f"--gif={basepath}/input/{gif_name}",
            f"--control_type={control_type}",
            f"--controlnet_conditioning_scale={conditioning_scale}",
            f"--control_guidance_start={guidance_start}",
            f"--control_guidance_end={guidance_end}",
        ]
    cmd.append(f"--output={output_path}")
    return cmd
