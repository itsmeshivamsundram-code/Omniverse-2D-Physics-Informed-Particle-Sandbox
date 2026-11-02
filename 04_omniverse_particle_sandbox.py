"""Omniverse 2D: Physics-Informed Particle Sandbox
Left-drag: spawn | Right/Middle-hold: attract | 1 sand, 2 water, 3 spark | G gravity | X explode | C clear
Live readout of kinetic/potential energy and momentum."""
import tkinter as tk, math, random
W, H, R, CELL, MAXP = 900, 640, 4.0, 10, 800
MAT = {1: ("sand", "#e0c070"), 2: ("water", "#4a90e2"), 3: ("spark", "#ff7030")}

class App:
    def __init__(s, root):
        s.c = tk.Canvas(root, width=W, height=H, bg="#0b0b12", highlightthickness=0); s.c.pack()
        s.ps, s.kind, s.grav, s.mx, s.my, s.down, s.pull = [], 1, True, 0, 0, False, False
        s.c.bind("<Button-1>", lambda e: s.mouse(e, "down", True)); s.c.bind("<ButtonRelease-1>", lambda e: s.mouse(e, "down", False))
        for b in (2, 3):
            s.c.bind(f"<Button-{b}>", lambda e: s.mouse(e, "pull", True)); s.c.bind(f"<ButtonRelease-{b}>", lambda e: s.mouse(e, "pull", False))
        s.c.bind("<Motion>", s.move); s.c.bind("<B1-Motion>", s.move)
        for b in (2, 3): s.c.bind(f"<B{b}-Motion>", s.move)
        for k in "123": root.bind(k, lambda e: setattr(s, "kind", int(e.char)))
        root.bind("g", lambda e: setattr(s, "grav", not s.grav)); root.bind("c", lambda e: s.ps.clear()); root.bind("x", s.explode)
        s.loop()
    def move(s, e): s.mx, s.my = e.x, e.y
    def mouse(s, e, attr, v): s.mx, s.my = e.x, e.y; setattr(s, attr, v)
    def explode(s, e=None):
        for p in s.ps:
            dx, dy = p[0] - s.mx, p[1] - s.my; d = math.hypot(dx, dy) + 1
            if d < 160: f = 600 * (1 - d / 160); p[2] += dx / d * f; p[3] += dy / d * f
    def spawn(s):
        for _ in range(4):
            x, y = s.mx + random.uniform(-10, 10), s.my + random.uniform(-10, 10)
            if s.kind == 3: s.ps.append([x, y, random.uniform(-40, 40), random.uniform(-60, 0), 3, random.uniform(0.8, 1.8)])
            else: s.ps.append([x, y, random.uniform(-10, 10), 0.0, s.kind, 99])
        if len(s.ps) > MAXP: del s.ps[:len(s.ps) - MAXP]
    def update(s, dt):
        g = 500.0 if s.grav else 0.0
        grid = {}
        for i, p in enumerate(s.ps): grid.setdefault((int(p[0] // CELL), int(p[1] // CELL)), []).append(i)
        for i, p in enumerate(s.ps):
            if p[4] == 3: p[3] -= 160 * dt; p[5] -= dt
            else: p[3] += g * dt
            if s.pull:
                dx, dy = s.mx - p[0], s.my - p[1]; d = math.hypot(dx, dy) + 20
                p[2] += dx / d * 9000 / d * dt * 6; p[3] += dy / d * 9000 / d * dt * 6
            if p[4] != 3:
                cx, cy = int(p[0] // CELL), int(p[1] // CELL)
                for gx in range(cx - 1, cx + 2):
                    for gy in range(cy - 1, cy + 2):
                        for j in grid.get((gx, gy), ()):
                            if j <= i: continue
                            q = s.ps[j]
                            if q[4] == 3: continue
                            dx, dy = q[0] - p[0], q[1] - p[1]; d2 = dx * dx + dy * dy
                            if 0 < d2 < 4 * R * R:
                                d = math.sqrt(d2); ov = (2 * R - d) * 0.5; nx, ny = dx / d, dy / d
                                p[0] -= nx * ov; p[1] -= ny * ov; q[0] += nx * ov; q[1] += ny * ov
                                dv = (p[2] - q[2]) * nx + (p[3] - q[3]) * ny
                                if dv > 0: p[2] -= nx * dv * 0.5; p[3] -= ny * dv * 0.5; q[2] += nx * dv * 0.5; q[3] += ny * dv * 0.5
            damp = 0.985 if p[4] == 1 else 0.998
            p[2] *= damp; p[3] *= damp
            p[0] += p[2] * dt; p[1] += p[3] * dt
            if p[1] > H - R: p[1] = H - R; p[3] *= -0.2; p[2] *= 0.9
            if p[1] < R: p[1] = R; p[3] *= -0.3
            if p[0] < R: p[0] = R; p[2] *= -0.3
            if p[0] > W - R: p[0] = W - R; p[2] *= -0.3
        s.ps = [p for p in s.ps if p[5] > 0]
    def loop(s):
        if s.down: s.spawn()
        for _ in range(2): s.update(1 / 60)
        c = s.c; c.delete("all")
        for p in s.ps:
            col = MAT[p[4]][1]; c.create_rectangle(p[0] - R, p[1] - R, p[0] + R, p[1] + R, fill=col, outline="")
        ke = sum(0.5 * (p[2] ** 2 + p[3] ** 2) for p in s.ps) / 1000
        pe = sum(500 * (H - p[1]) for p in s.ps if s.grav) / 1000
        mom = math.hypot(sum(p[2] for p in s.ps), sum(p[3] for p in s.ps)) / 100
        c.create_text(10, 10, anchor="nw", fill="white", font=("Consolas", 12),
            text=f"Material: {MAT[s.kind][0]}  Gravity: {'ON' if s.grav else 'OFF'}  N={len(s.ps)}\nKE {ke:9.1f}   PE {pe:9.1f}   E {ke + pe:9.1f}   |p| {mom:7.1f}")
        s.c.after(16, s.loop)
root = tk.Tk(); root.title("Omniverse 2D Particle Sandbox"); App(root); root.mainloop()
