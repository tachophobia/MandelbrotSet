import tkinter as tk
import numpy as np
from PIL import Image, ImageTk, ImageGrab
from datetime import datetime
from tkinter import messagebox

try:
    import cv2
    installed = True
except ImportError as e:
    installed = False
    print("OpenCV package not installed. Install it to have access to all features.")

continue_running = True

# hyperparameters
dbail = 1e6
iterations = 10000
r, g, b = 1, 1, 1


def mandelbrot(Z, max_iter):
    global dbail
    z = np.zeros_like(Z)
    iters = np.zeros_like(Z, dtype=int)
    dz = np.ones_like(Z)

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


def reset(_):
    global xmax, xmin, ymax, ymin, zoom, anchor, box, r, g, b, dbail, iterations
    zoom = 1
    anchor = WIDTH//2, HEIGHT//2
    xmin, xmax, ymin, ymax = -2, 1, -1.3, 1.3
    last_state['index'] = 0
    box = False
    r, g, b = 1, 1, 1
    dbail = 1e6
    iterations = 10000
    render_graphics()


def regen(_):
    global xmax, xmin, ymax, ymin, zoom, anchor
    zoom = 1
    anchor = WIDTH//2, HEIGHT//2
    last_state['index'] = 10
    render_graphics()


def update_state(func, max_iter: int):
    global WIDTH, HEIGHT, canvas, zoom, xmax, xmin, ymax, ymin, box

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

    x_edge = 0
    if not box:
        x_edge = (xmax-xmin)*((WIDTH/HEIGHT)-1)/2

    x = np.linspace(xmin-x_edge, xmax+x_edge, WIDTH)
    y = np.linspace(ymin, ymax, HEIGHT)

    # create cartesian plane
    X, Y = np.meshgrid(x, y)

    # make the plane complex
    Z = X + Y * 1j

    fractal = func(Z, max_iter)

    return fractal


def seizure_colors(iterations):
    colors = np.zeros((iterations, 3))
    for i in range(iterations):
        colors[i] = [i % 8 * 32, i % 16 * 16, i % 32 * 8]
    return colors


def aesthetic_colors():
    global r, g, b
    iterations = 256
    colors = np.zeros((iterations, 3), dtype=int)
    for i in range(iterations):
        colors[i] = [((i * r) % 256), ((i * g) % 256), ((i * b) % 256)]

    colors[254:] = [0, 0, 0]

    return colors


def render_graphics():
    global last_state, zoom, iterations, select_rect, display_stats

    gamestates = update_state(mandelbrot, iterations)
    color_map_arr = aesthetic_colors()   # 1, 2, 3 for default

    for i, gamestate in enumerate(gamestates):
        if not continue_running:
            return

        gamestate = gamestate.astype(np.float64)
        gamestate *= 255./gamestate.max()
        gamestate = gamestate.astype(np.uint8)

        if not np.allclose(gamestate, np.ones_like(gamestate) * 255):
            gamestate_colored = color_map_arr[gamestate % iterations]
            gamestate_colored = gamestate_colored.astype(np.uint8)

            if (i >= last_state['index'] or (last_state['state'] is None)):
                tk_image = ImageTk.PhotoImage(
                    Image.fromarray(gamestate_colored))
                last_state['state'] = tk_image
                last_state['arr'] = gamestate_colored
                last_state['index'] = i

            canvas.create_image(0, 0, image=last_state['state'], anchor=tk.NW)
            if display_stats:
                info = f"Zoom factor: {(2.6 / abs(ymax-ymin)):.0f}\nCoordinates: {round((xmax+xmin)/2, 3)} + {round((ymax+ymin)/2, 3)}i"
                canvas.create_text(WIDTH // 1.3, int(HEIGHT * .05), text=info, anchor=tk.NW,
                                   fill='red', font=("Arial", 20))
            canvas.update()
            root.update()

        if zoom != 1 and installed:
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
    global select_rect, xmax, xmin, ymax, ymin, box
    canvas.delete("selection_rect")

    diffW = abs(select_rect[2] - select_rect[0])/WIDTH
    diffH = abs(select_rect[3] - select_rect[1])/HEIGHT

    if (diffW * diffH) > 0.001:
        diffx = abs(xmax-xmin)
        diffy = abs(ymax-ymin)

        # deltax = diffW * diffx
        deltay = diffH * diffy

        xmin += diffx*min(select_rect[0], select_rect[2])/WIDTH
        # xmax = xmin + deltax

        ymin += diffy*min(select_rect[1], select_rect[3])/HEIGHT
        ymax = ymin + deltay

        # correct for aspect ratio:
        xmax = xmin + abs(ymax-ymin) * WIDTH/HEIGHT

        last_state['index'] = 10
        box = True

    select_rect = None
    render_graphics()


def set_display(_):
    global display_stats
    display_stats = not display_stats


def capture_screenshot(_):
    screenshot = ImageGrab.grab(bbox=(root.winfo_x(), root.winfo_y(
    ), root.winfo_x() + WIDTH, root.winfo_y() + HEIGHT))
    name = f"fractal-{datetime.now()}.png"
    screenshot.save(name)
    print(f"Screenshot captured and saved as '{name}'")


def exit_program():
    global continue_running
    continue_running = False
    root.destroy()


def set_hyperparameters():
    global dbail, iterations, r, g, b

    hyperparameters_window = tk.Toplevel(root)
    hyperparameters_window.title("Set Hyperparameters")
    hyperparameters_window.geometry(f"250x150+{WIDTH}+{HEIGHT}")

    dbail_label = tk.Label(hyperparameters_window, text="dbail:")
    dbail_label.grid(row=0, column=0)
    dbail_entry = tk.Entry(hyperparameters_window)
    dbail_entry.insert(0, str(dbail))
    dbail_entry.grid(row=0, column=1)

    iterations_label = tk.Label(hyperparameters_window, text="Iterations:")
    iterations_label.grid(row=1, column=0)
    iterations_entry = tk.Entry(hyperparameters_window)
    iterations_entry.insert(0, str(iterations))
    iterations_entry.grid(row=1, column=1)

    r_label = tk.Label(hyperparameters_window, text="R:")
    r_label.grid(row=2, column=0)
    r_entry = tk.Entry(hyperparameters_window)
    r_entry.insert(0, str(r))
    r_entry.grid(row=2, column=1)

    g_label = tk.Label(hyperparameters_window, text="G:")
    g_label.grid(row=3, column=0)
    g_entry = tk.Entry(hyperparameters_window)
    g_entry.insert(0, str(g))
    g_entry.grid(row=3, column=1)

    b_label = tk.Label(hyperparameters_window, text="B:")
    b_label.grid(row=4, column=0)
    b_entry = tk.Entry(hyperparameters_window)
    b_entry.insert(0, str(b))
    b_entry.grid(row=4, column=1)

    def update_hyperparameters():
        global dbail, iterations, r, g, b

        try:
            dbail = float(eval(dbail_entry.get()))
            iterations = int(eval(iterations_entry.get()))
            r = float(r_entry.get())
            g = float(g_entry.get())
            b = float(b_entry.get())
            hyperparameters_window.destroy()
        except:
            messagebox.showerror(
                "Invalid Input", "Please enter valid numeric values for the hyperparameters.")
        regen(None)

    update_button = tk.Button(hyperparameters_window,
                              text="Update", command=update_hyperparameters)
    update_button.grid(row=5, columnspan=2)


def show_menu(event):
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="set hyperparameters", command=set_hyperparameters)
    menu.post(event.x_root, event.y_root)


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
    display_stats = False

    root.protocol("WM_DELETE_WINDOW", exit_program)
    root.bind("<Escape>", exit_program)
    root.bind("<Button-3>", show_menu)
    root.bind("<Button-4>", zoomIn)
    root.bind("<Key-z>", zoomIn)
    root.bind("<Button-5>", zoomOut)
    root.bind("<Key-x>", zoomOut)
    root.bind("<Key-r>", reset)
    root.bind("<Key-a>", regen)
    root.bind("<KeyRelease-c>", set_display)
    root.bind("<Key-s>", capture_screenshot)
    canvas.bind("<ButtonPress-1>", start_selection)
    canvas.bind("<B1-Motion>", update_selection)
    canvas.bind("<ButtonRelease-1>", end_selection)

    last_state = {'state': None, 'arr': None,
                  'index': 0, 'anchor': anchor, 'reset': False}
    xmin, xmax, ymin, ymax = -2, 1, -1.3, 1.3
    threshold = False
    box = False
    render_graphics()

    root.mainloop()
