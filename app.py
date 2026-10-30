import datetime
import os
import random
import subprocess

import streamlit as st
from moviepy.editor import VideoFileClip, vfx
from moviepy.video.fx.all import crop, resize, rotate

from helpers import (apply_style, build_command, is_abusive, safe_slug,
                     translate_to_english)

# Path to the Hotshot-XL checkout (override with the HOTSHOT_PATH env var)
BASEPATH = os.environ.get(
    "HOTSHOT_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "Hotshot-XL")
)
if not os.path.exists(os.path.join(BASEPATH, "inference.py")):
    subprocess.run(["git", "clone", "https://github.com/hotshotco/Hotshot-XL", BASEPATH], check=True)
os.makedirs(f"{BASEPATH}/output", exist_ok=True)

st.session_state.setdefault("results", [])      # list of generated file paths
st.session_state.setdefault("edited", None)     # last edited GIF path

st.title("Multilingual GIF Generator")

# ---------------- Inputs ----------------
paragraph_prompt = st.text_area("Enter your prompt (any language, one video per line):")
negative_prompt = st.text_input("Negative prompt (optional):", value="blurry")
style = st.selectbox("Style:", ["Cartoon", "Realistic", "Abstract"])
language_theme = st.selectbox("Language theme:", ["None", "Japanese", "Indian", "African", "European", "Chinese"])
seed = st.number_input("Seed (-1 for random):", value=-1, step=1)
width = st.number_input("Width:", value=512, step=8)
height = st.number_input("Height:", value=512, step=8)
upscale = st.selectbox("Upscale:", [0, 2, 4])
video_frames = st.number_input("Video frames:", value=8, min_value=1, step=1)
video_duration = st.number_input("Video duration (ms):", value=1000, min_value=100, step=100)
steps = st.number_input("Steps:", value=40, min_value=1, step=1)
lora_file_name = st.text_input("LoRA file name in Hotshot-XL/lora (optional):")
file_prefix = st.text_input("File prefix:", value="story_")
file_type = st.selectbox("File type:", [".gif", ".mp4"])
scheduler = st.selectbox("Scheduler:", ["EulerAncestralDiscreteScheduler", "EulerDiscreteScheduler"])
gif_name = st.text_input("Guide GIF name in Hotshot-XL/input (optional):")
control_type = st.selectbox("Control type:", ["depth", "canny"])
controlnet_conditioning_scale = st.number_input("ControlNet conditioning scale:", value=0.8)
control_guidance_start = st.number_input("Control guidance start:", value=0.0)
control_guidance_end = st.number_input("Control guidance end:", value=1.0)


# ---------------- GIF editing ----------------
def modify_gif(path, option, **kw):
    clip = VideoFileClip(path)
    try:
        if option == "rotate":
            out = clip.fx(rotate, kw["angle"])
        elif option == "crop":
            out = clip.fx(crop, x1=kw["x1"], y1=kw["y1"], x2=kw["x2"], y2=kw["y2"])
        elif option == "zoom":
            out = clip.fx(resize, kw["zoom_factor"])
        elif option == "speed":
            out = clip.fx(vfx.speedx, kw["speed_factor"])
        else:
            return path
        new_path = path[:-4] + f"_modified_{option}.gif"
        out.write_gif(new_path)
        return new_path
    finally:
        clip.close()


# ---------------- Generate ----------------
if st.button("Generate"):
    lines = [l.strip() for l in paragraph_prompt.splitlines() if l.strip()]
    if not lines:
        st.warning("Please enter a prompt.")
        st.stop()

    flagged = [l for l in lines if is_abusive(l)]
    if flagged:
        st.warning("Some prompts contain inappropriate content. Please rewrite them, e.g.:")
        for s in ["A cute puppy playing in a garden.", "A happy puppy enjoying the sunshine.",
                  "A playful puppy chasing butterflies.", "A peaceful puppy sleeping under a tree."]:
            st.write(f"- {s}")
        st.stop()

    st.session_state.results = []
    st.session_state.edited = None
    for line in lines:
        prompt, err = translate_to_english(line)
        if err:
            st.error(f"Translation failed, using original text: {err}")
        prompt = apply_style(prompt, style, language_theme)

        line_seed = random.randint(0, 2**32 - 1) if seed == -1 else int(seed)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        out_path = f"{BASEPATH}/output/{file_prefix}{stamp}_{safe_slug(prompt)}{file_type}"

        if gif_name and not os.path.exists(f"{BASEPATH}/input/{gif_name}"):
            st.error(f"Guide GIF not found: {BASEPATH}/input/{gif_name}")
            st.stop()

        cmd = build_command(
            BASEPATH, prompt, negative_prompt, steps, line_seed, width, height,
            video_frames, video_duration, scheduler, out_path, upscale=upscale,
            lora_file_name=lora_file_name, gif_name=gif_name, control_type=control_type,
            conditioning_scale=controlnet_conditioning_scale,
            guidance_start=control_guidance_start, guidance_end=control_guidance_end,
        )
        with st.spinner(f"Generating: {prompt[:60]}..."):
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                st.session_state.results.append(out_path)
            except subprocess.CalledProcessError as e:
                st.error(f"Generation failed:\n{e.stderr[-2000:]}")

# ---------------- Show results (persist across reruns) ----------------
for p in st.session_state.results:
    if os.path.exists(p):
        st.video(p) if p.endswith(".mp4") else st.image(p)

gifs = [p for p in st.session_state.results if p.endswith(".gif") and os.path.exists(p)]
if gifs:
    st.subheader("Edit a generated GIF")
    target = st.selectbox("GIF to edit:", gifs, format_func=os.path.basename)
    option = st.selectbox("Edit:", ["rotate", "crop", "zoom", "speed"])
    if option == "rotate":
        kw = {"angle": st.number_input("Angle (degrees):", value=90)}
    elif option == "crop":
        kw = {"x1": st.number_input("x1:", value=0), "y1": st.number_input("y1:", value=0),
              "x2": st.number_input("x2:", value=300), "y2": st.number_input("y2:", value=300)}
    elif option == "zoom":
        kw = {"zoom_factor": st.number_input("Zoom factor:", value=1.5)}
    else:
        kw = {"speed_factor": st.number_input("Speed factor:", value=2.0)}

    if st.button("Apply edit"):
        with st.spinner("Editing..."):
            st.session_state.edited = modify_gif(target, option, **kw)
    if st.session_state.edited and os.path.exists(st.session_state.edited):
        st.success("GIF modified successfully!")
        st.image(st.session_state.edited)
