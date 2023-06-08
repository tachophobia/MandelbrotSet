import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import cv2


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
    zoom += 1
    anchor = canvas.canvasx(event.x), canvas.canvasy(event.y)


def zoomOut(event):
    global zoom, anchor
    zoom -= .2
    zoom = max(.1, zoom)
    anchor = canvas.canvasx(event.x), canvas.canvasy(event.y)


def reset(event):
    global xmax, xmin, ymax, ymin, zoom, anchor
    zoom = 1
    anchor = WIDTH//2, HEIGHT//2
    xmin, xmax, ymin, ymax = -2, 1, -1.3, 1.3
    last_state['index'] = 0
    render_graphics()


def regen(event):
    global xmax, xmin, ymax, ymin, zoom, anchor
    zoom = 1
    anchor = WIDTH//2, HEIGHT//2
    last_state['index'] = 10
    render_graphics()


def update_state(func, max_iter: int):
    global WIDTH, HEIGHT, canvas, zoom, xmax, xmin, ymax, ymin

    if zoom != 1:
        anchor = last_state['anchor']
        x_offset = (xmax-xmin) * ((anchor[0] - WIDTH/2)/WIDTH)
        y_offset = (ymax-ymin) * ((anchor[1] - HEIGHT/2)/HEIGHT)

        xmax += x_offset
        xmin += x_offset
        ymax += y_offset
        ymin += y_offset

        centerx = (xmax+xmin)/2
        centery = (ymax+ymin)/2

        y_offset = (ymax-ymin)/2/zoom
        x_offset = (xmax-xmin)/2/zoom
        ymax = centery + y_offset
        ymin = centery - y_offset
        xmax = centerx + x_offset
        xmin = centerx - x_offset

    zoom = 1

    if not np.isclose(abs(xmax-xmin)/abs(ymax-ymin), WIDTH/HEIGHT):
        x_edge = (xmax-xmin)*((WIDTH/HEIGHT)-1)/2
        xmin -= x_edge
        xmax += x_edge

    x = np.linspace(xmin, xmax, WIDTH)
    y = np.linspace(ymin, ymax, HEIGHT)

    # create cartesian plane
    X, Y = np.meshgrid(x, y)

    # make the plane complex
    Z = X + Y * 1j

    fractal = func(Z, max_iter)

    return fractal


def render_graphics():
    global last_state, zoom, threshold, iterations, select_rect

    gamestates = update_state(mandelbrot, iterations)

    for i, gamestate in enumerate(gamestates):
        if last_state['reset']:
            break
        if (i+1) % 2 == 0:
            gamestate *= 255.0/gamestate.max()
            gamestate = gamestate.astype(np.uint8)

            if threshold:
                gamestate[gamestate > threshold] = 255
                gamestate[gamestate <= threshold] = 0
            gamestate = 255 - gamestate

            if (i >= last_state['index'] or (last_state['state'] is None)):

                tk_image = ImageTk.PhotoImage(Image.fromarray(gamestate))
                last_state['state'] = tk_image
                last_state['arr'] = gamestate
                last_state['index'] = i

            canvas.create_image(0, 0, image=last_state['state'], anchor=tk.NW)
            canvas.update()
            root.update()
        if zoom != 1:
            last_state['index'] = 20

            rot_mat = cv2.getRotationMatrix2D((anchor[0], anchor[1]), 0, zoom)
            gamestate = cv2.warpAffine(
                last_state['arr'], rot_mat, last_state['arr'].shape[1::-1], flags=cv2.INTER_LINEAR)

            tk_image = ImageTk.PhotoImage(Image.fromarray(gamestate))
            canvas.create_image(0, 0, image=tk_image, anchor=tk.NW)
            last_state['state'] = tk_image
            last_state['arr'] = gamestate
            last_state['anchor'] = anchor

            canvas.update()
            root.update()

            break
        if last_state['reset']:
            last_state['reset'] = False
            break

    root.after(16, render_graphics)


def start_selection(event):
    global select_rect
    select_rect = [event.x, event.y, event.x, event.y]


def update_selection(event):
    global select_rect
    select_rect[2] = event.x
    select_rect[3] = event.y
    canvas.delete("selection_rect")
    canvas.create_rectangle(
        *select_rect, outline='red', tags="selection_rect")


def end_selection(_):
    global select_rect, xmax, xmin, ymax, ymin
    canvas.delete("selection_rect")

    diffW = abs(select_rect[2] - select_rect[0])/WIDTH
    diffH = abs(select_rect[3] - select_rect[1])/HEIGHT

    if (diffW * diffH) > 0.01:
        diffx = abs(xmax-xmin)
        diffy = abs(ymax-ymin)

        deltax = diffW * diffx
        deltay = diffH * diffy

        xmin += diffx*min(select_rect[0], select_rect[2])/WIDTH
        # xmax = xmin + deltax

        ymin += diffy*min(select_rect[1], select_rect[3])/HEIGHT
        ymax = ymin + deltay

        # correct for aspect ratio:
        xmax = xmin + abs(ymax-ymin) * WIDTH/HEIGHT

        last_state['index'] = 10

    select_rect = None
    render_graphics()


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
    select_rect = None

    root.bind("<Escape>", lambda e: root.destroy())
    root.bind("<Button-4>", zoomIn)
    root.bind("<Key-z>", zoomIn)
    root.bind("<Button-5>", zoomOut)
    root.bind("<Key-r>", reset)
    root.bind("<Key-a>", regen)
    canvas.bind("<ButtonPress-1>", start_selection)
    canvas.bind("<B1-Motion>", update_selection)
    canvas.bind("<ButtonRelease-1>", end_selection)

    last_state = {'state': None, 'arr': None,
                  'index': 0, 'anchor': anchor, 'reset': False}
    xmin, xmax, ymin, ymax = -2, 1, -1.3, 1.3
    threshold = 254
    iterations = 500
    render_graphics()

    root.mainloop()
