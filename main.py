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


def zoomIn(event):
    global zoom, anchor
    zoom += .1
    anchor = canvas.canvasx(event.x), canvas.canvasy(event.y)


def zoomOut(event):
    global zoom, anchor
    zoom -= .1
    zoom = max(.1, zoom)
    anchor = canvas.canvasx(event.x), canvas.canvasy(event.y)


def reset(event):
    global xmax, xmin, ymax, ymin, zoom
    zoom = 1
    xmin, xmax, ymin, ymax = -2, 1, -1.3, 1.3


def update_state(func, max_iter: int):
    global WIDTH, HEIGHT, canvas, zoom, xmax, xmin, ymax, ymin

    if zoom != 1:
        x_offset = (xmax-xmin) * ((anchor[0] - WIDTH/2)/WIDTH)
        y_offset = (ymax-ymin) * ((anchor[1] - HEIGHT/2)/HEIGHT)

        xmax += x_offset
        xmin += x_offset
        ymax += y_offset
        ymin += y_offset

        centerx = (xmax+xmin)/2
        centery = (ymax+ymin)/2

        ymax = centery + (ymax-ymin)/2/zoom
        ymin = centery - (ymax-ymin)/2/zoom
        xmax = centerx + (xmax-xmin)/2/zoom
        xmin = centerx - (xmax-xmin)/2/zoom

    zoom = 1
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
    global last_state, zoom
    gamestates = update_state(mandelbrot, 500)

    for i, gamestate in enumerate(gamestates):
        if (i+1) % 50 == 0:
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
        if zoom != 1:
            last_state['index'] = 0
            break

    root.after(1, render_graphics)


if __name__ == "__main__":
    root = tk.Tk()
    WIDTH, HEIGHT = root.winfo_screenwidth()//2, root.winfo_screenheight()//2
    root.geometry(f"{WIDTH}x{HEIGHT}+{WIDTH//2}+{HEIGHT//2}")
    root.resizable(False, False)
    root.title("Mandelbrot")

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, background='black')
    canvas.pack()

    zoom = 1
    anchor = WIDTH//2, HEIGHT//2
    root.bind("<Escape>", lambda e: root.destroy())
    root.bind("<Button-4>", zoomIn)
    root.bind("<Button-5>", zoomOut)
    root.bind("<Button-3>", reset)

    last_state = {'state': None, 'index': 0, 'pan': [0, 0]}
    xmin, xmax, ymin, ymax = -2, 1, -1.3, 1.3
    render_graphics()

    root.mainloop()
