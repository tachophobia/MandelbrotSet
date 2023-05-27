import tkinter as tk
import numpy as np
from PIL import Image, ImageTk


def mandelbrot(Z, max_iter):
    z = np.zeros_like(Z)
    iters = np.zeros_like(Z)
    dz = np.ones_like(Z)
    dbail = 1e6

    for _ in range(max_iter):
        mask = np.abs(dz) < dbail
        z[mask] = z[mask] * z[mask] + Z[mask]
        dz[mask] = 2 * dz[mask] * z[mask] + 1
        iters += mask
        yield iters


def start_pan(event):
    canvas.scan_mark(event.x, event.y)


def move_pan(event):
    canvas.scan_dragto(event.x, event.y, gain=1)


def zoom(event):
    print('cat')
    scale_factor = 1.1 if event.delta > 0 else 0.9
    canvas.scale("all", event.x, event.y, scale_factor, scale_factor)


def update_state(func, max_iter: int, xmin=-2, xmax=1, ymin=-1.3, ymax=1.3):
    global WIDTH, HEIGHT, canvas

    x_edge = (xmax-xmin)*((WIDTH/HEIGHT)-1)/2
    x = np.linspace(xmin-x_edge,
                    xmax+x_edge, WIDTH)
    y = np.linspace(ymin, ymax, HEIGHT)

    # create cartesian plane
    X, Y = np.meshgrid(x, y)

    # make the plane complex
    Z = X + Y * 1j

    fractal = func(Z, max_iter)

    return fractal


def render_graphics():
    global last_state
    gamestates = update_state(mandelbrot, 500)

    for i, gamestate in enumerate(gamestates):
        if (i+1) % 10 == 0:
            gamestate *= 255.0/gamestate.max()
            gamestate = gamestate.astype(np.uint8)
            if i >= last_state['index'] or last_state['state'] is None:
                pil_image = Image.fromarray(gamestate)
                tk_image = ImageTk.PhotoImage(pil_image)
                last_state['state'] = tk_image
                last_state['index'] = i
            canvas.create_image(
                0, 0, image=last_state['state'], anchor=tk.NW)
            canvas.update()
            root.update()
        if last_state['pan'] != [canvas.canvasx(0), canvas.canvasy(0)]:
            canvas.move("all", last_state['pan'][0], last_state['pan'][1])
            canvas.update()
            root.update()

    root.after(16, render_graphics)


if __name__ == "__main__":
    root = tk.Tk()
    WIDTH, HEIGHT = root.winfo_screenwidth()//2, root.winfo_screenheight()//2
    root.geometry(f"{WIDTH}x{HEIGHT}+{WIDTH//2}+{HEIGHT//2}")

    root.bind("<Escape>", lambda e: root.destroy())
    root.resizable(False, False)

    root.title("Mandelbrot")

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, background='black')
    canvas.bind("<ButtonPress-1>", start_pan)
    canvas.bind("<B1-Motion>", move_pan)
    canvas.bind("<MouseWheel>", zoom)

    canvas.pack()

    last_state = {'state': None, 'index': 0, 'zoom': 1, 'pan': [0, 0]}
    render_graphics()

    root.mainloop()
