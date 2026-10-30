import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import *

class FakeT:
    def __init__(self, source, target): pass
    def translate(self, t): return "hello world"
class BadT:
    def __init__(self, **k): raise RuntimeError("no network")

class T(unittest.TestCase):
    def test_abusive(self):
        self.assertTrue(is_abusive("I will KILL it"))
        self.assertFalse(is_abusive("a skilled painter"))
    def test_style(self):
        p = apply_style("cat", "Cartoon", "Japanese")
        self.assertIn("cartoon style", p); self.assertIn("anime style", p)
        self.assertEqual(apply_style("cat", "None", "None"), "cat")
    def test_translate(self):
        self.assertEqual(translate_to_english("வணக்கம்", FakeT), ("hello world", None))
        txt, err = translate_to_english("x", BadT)
        self.assertEqual(txt, "x"); self.assertTrue(err)
    def test_slug(self):
        self.assertEqual(safe_slug('a "cat"/dog, ok'), "a_cat_dog_ok"); self.assertEqual(safe_slug("!!!"), "video")
    def test_cmd(self):
        c = build_command("/h", 'a "quoted" prompt', "blurry", 40, 5, 512, 512, 8, 1000,
                          "EulerAncestralDiscreteScheduler", "/h/output/x.gif", upscale=2,
                          lora_file_name="l.safetensors", gif_name="g.gif")
        self.assertIn('--prompt=a "quoted" prompt', c); self.assertIn("--upscale=2", c)
        self.assertIn("--lora=/h/lora/l.safetensors", c); self.assertIn("--control_type=depth", c)
        self.assertEqual(c[-1], "--output=/h/output/x.gif")
        self.assertNotIn("--upscale=0", build_command("/h","p","n",1,1,1,1,1,1,"s","o"))
unittest.main()
