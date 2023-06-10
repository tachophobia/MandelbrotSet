# MandelbrotSet

## Interactive Mandelbrot set using Tkinter in python

### **What is the Mandelbrot set?**


A number $c$ on the complex plane is an element of the Mandelbrot set if it does not diverge when iterated to infinity with $z_{n+1} = z_n^2 + c$ from $z = 0$. In simpler terms, it's a special set of complex numbers that iterates over itself to produce an ever intricate and elaborate pattern whose complexity is best observed when you zoom into the boundaries.
_It's like an infinite loop of Russian dolls extending forever- except the level of intricacy is unparalleled._

In our interactive display of the Mandelbrot set, we let you set customizable bounds to select the reference point with which to zoom in or out. The most interesting facet of the visuals can be observed by zooming into the borders of the shape!

![Mandelbrot Set](https://github.com/tachophobia/MandelbrotSet/assets/112730336/c03db354-3bed-4f10-b32d-8ed1c3d5bb37)

We then colored the set cyclically based on the amount of iterations it took to diverge. The more confident we are that a certain pixel is convergent or divergent, the darker it is.

![Colored](https://github.com/tachophobia/MandelbrotSet/assets/112730336/724ecd44-56c6-4636-8ada-b768e793e4b0)

But how did we simulate it so smoothly? Well, since the set is infinitely complex, the only way to get a preview of what the shape looks like is by brute forcing each pixel many times. Since we can't brute force forever, we choose a certain amount of iterations for each pixel to run for. The only difference is, we made it so that you can see every step of the way. 
We iterate over each pixel, display what's been calculated so far, and then do another iteration over the entire image. This way, you get to see the shape become more and more defined until eventually their is so little uncertainty that only the edges remain.

![edges](https://github.com/tachophobia/MandelbrotSet/assets/112730336/871c2c6a-2b34-4994-96d3-36679b72f80a)

However, brute force is pretty slow. In our _test.ipynb_ file we demonstrate our process in trimming down the time it takes to iterate. Instead of simply using the given formula, we are able to acquire a lot more detail a lot more quickly by looking at the rate at which each pixel moves (the derivative). If a pixel is moving at too fast a rate, we can more quickly assume that it will diverge.
This method is called derivative bailout, or [derbail](https://en.wikipedia.org/wiki/Plotting_algorithms_for_the_Mandelbrot_set#Derivative_Bailout_or_%22derbail%22).


For more resources on the Mandelbrot Set, checkout 3Blue1Brown's [video](https://youtu.be/LqbZpur38nw) on it.
