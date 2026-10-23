import math as m
import random as r
import time
import turtle as t
import tkinter as tk
import tkinter.font as tkf

BG = "#000000"
FONT = "Segoe UI"
RED = (255, 62, 44)
FLASH = (255, 218, 210)
SCALE = 25
OUTLINE_TIME = 4.9
FILL_START = 5.1   
FILL_SPAN = 7.0     
s = t.Screen()
s.setup(800, 800)
s.bgcolor(BG)
s.title("Love Heart")
s.tracer(0)
s.update()

cv = s.getcanvas()
rng = r.Random(11)

PHRASES = [
    "I love you", "Seni seviyorum", "Te amo", "Je t'aime",
    "Ich liebe dich", "Ti amo", "Eu te amo", "Я тебя люблю",
    "사랑해", "愛してる", "我爱你", "मैं तुमसे प्यार करता हूँ",
    "Σ' αγαπώ", "Ik hou van jou", "Jag älskar dig", "Kocham cię",
    "ฉันรักเธอ", "Anh yêu em", "Aku cinta kamu", "Я тебе кохаю",
]

_fonts = {}


def font_for(size):
    if size not in _fonts:
        _fonts[size] = tkf.Font(
            root=cv, family=FONT, size=size, weight="bold"
        )
    return _fonts[size]


def heart(a):
    x = 16 * m.sin(a) ** 3
    y = (
        13 * m.cos(a)
        - 5 * m.cos(2 * a)
        - 2 * m.cos(3 * a)
        - m.cos(4 * a)
    )
    return x * SCALE, (y + 2.5) * SCALE  

POLY = [heart(2 * m.pi * i / 120) for i in range(120)]


def inside(px, py):
    ok = False
    j = len(POLY) - 1
    for i in range(len(POLY)):
        xi, yi = POLY[i]
        xj, yj = POLY[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            ok = not ok
        j = i
    return ok


def mix(c1, c2, k):
    k = max(0.0, min(1.0, k))
    return "#%02x%02x%02x" % tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))


BG_RGB = (0, 0, 0)
placed = []  
plan = []    

def free(x, y, w, h, pad=3):
    x1, y1, x2, y2 = x - w / 2 - pad, y - h / 2 - pad, x + w / 2 + pad, y + h / 2 + pad
    for a, b, c, d in placed:
        if x1 < c and x2 > a and y1 < d and y2 > b:
            return False
    return True


def try_place(x, y, born, sizes, need_inside):
    text = rng.choice(PHRASES)
    size = rng.choice(sizes)
    f = font_for(size)
    w, h = f.measure(text), f.metrics("linespace")
    if need_inside:
        corners = [(x + dx, y + dy) for dx in (-w / 2, w / 2) for dy in (-h / 2, h / 2)]
        if not all(inside(cx, cy) for cx, cy in corners):
            return False
    if not free(x, y, w, h):
        return False
    placed.append((x - w / 2, y - h / 2, x + w / 2, y + h / 2))
    plan.append((born, x, y, text, size))
    return True


STEPS = 700
for i in range(STEPS):
    a = 2 * m.pi * i / STEPS
    x, y = heart(a)
    try_place(x * 0.97, y * 0.97 - 2, OUTLINE_TIME * i / STEPS, [10, 11, 12, 13, 15], False)

spots = []
for _ in range(4500):
    x = rng.uniform(-17, 17) * SCALE
    y = rng.uniform(-14, 15) * SCALE
    spots.append((x, y))
fill = []
for x, y in spots:
    if inside(x, y) and try_place(x, y, 0, [9, 10, 10, 11, 12, 13, 15], True):
        fill.append(len(plan) - 1)
rng.shuffle(fill)
for k, idx in enumerate(fill):
    born, x, y, text, size = plan[idx]
    plan[idx] = (FILL_START + FILL_SPAN * k / max(1, len(fill)), x, y, text, size)

plan.sort(key=lambda p: p[0])

items = [] 
t0 = time.time()
nxt = 0


def tick():
    global nxt
    try:
        now = time.time() - t0
        while nxt < len(plan) and plan[nxt][0] <= now:
            born, x, y, text, size = plan[nxt]
            iid = cv.create_text(x, -y, text=text, fill=BG, font=font_for(size))
            items.append([iid, born, False])
            nxt += 1
        for it in items:
            if it[2]:
                continue
            age = now - it[1]
            if age < 0.2:
                col = mix(BG_RGB, FLASH, age / 0.2)
            elif age < 0.8:
                col = mix(FLASH, RED, (age - 0.2) / 0.6)
            else:
                col = mix(FLASH, RED, 1)
                it[2] = True
            cv.itemconfigure(it[0], fill=col)
        s.ontimer(tick, 25)
    except (tk.TclError, t.Terminator):
        pass 

tick()
s.mainloop()
