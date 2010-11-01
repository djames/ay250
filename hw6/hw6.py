# Daren Hasenkamp
# 19362801

from numpy import *
from matplotlib.figure import *
from enthought.traits.api import *
from enthought.traits.ui.api import *
from mpl_figure_editor import MPLFigureEditor
from yahoo.search.image import ImageSearch
import matplotlib.pyplot as plt
import commands
import wx
import scipy.ndimage as imgproc

# input: query string    output: tuple(img array, url string)
def getImage(q) :
    srch = ImageSearch(app_id="YahooDemo",query=q)
    # get one result in png format
    srch.results = 1
    srch.format = "png"
    for res in srch.parse_results():
        # the file-like object returned by
        # urllib doesn't implement some of the methods needed by imread. i
        # tried to read() the urllib object and convert that to a string
        # stream, but imread didn't like that, either. i knew creating
        # a file and reading it would work, so i did it.
        commands.getoutput("wget '"+res.Url+"' -O tmpfile")
        x = plt.imread("tmpfile")
        commands.getoutput("rm tmpfile")
        # images get reversed for some reason, reverse it back
        x = x[::-1]
        return (x, res.Url)

class Test(HasTraits):
    query = Str
    run_query = Button
    gaussian_filter = Button
    rotate = Button
    fourier_gaussian = Button
    url = Str
    figure = Instance(Figure, ())
    curimage = None
    view = View(Item('query'),Item("run_query"),Item('url'),Item("gaussian_filter"),Item("rotate"),Item("fourier_gaussian"),Item('figure', editor=MPLFigureEditor(),
                                show_label=False),
                        width=700,
                        height=700,
                        resizable=True)
    # same init function as in lecture slides (no reason to change it)
    def __init__(self):
        super(Test, self).__init__()
        axes = self.figure.add_subplot(111)
        t = linspace(0, 2*pi, 200)
        axes.plot(sin(t)*(1+0.5*cos(11*t)), cos(t)*(1+0.5*cos(11*t)))
    # run a query and update image/url field (target of "run query" button)
    def _run_query_fired(self) :
        (x, u) = getImage(self.query)
        self.curimage = x
        self.url = u
        self.figure.axes[0].images = []
        self.figure.axes[0].imshow(x)
        # schedule image update
        wx.CallAfter(self.figure.canvas.draw)
    # apply gaussian filter to image (target of "gaussian filter" button)
    def _gaussian_filter_fired(self) :
        self.curimage = imgproc.filters.gaussian_filter(self.curimage, 2.0)
        self.figure.axes[0].images = []
        self.figure.axes[0].imshow(self.curimage)
        wx.CallAfter(self.figure.canvas.draw)
    # rotate image 90 degrees counterclockwise (target of "rotate" button)
    def _rotate_fired(self) :
        self.curimage = imgproc.interpolation.rotate(self.curimage, 90.0)
        self.figure.axes[0].images = []
        self.figure.axes[0].imshow(self.curimage)
        wx.CallAfter(self.figure.canvas.draw)
    # convert image to a fourier transformed image (target of "fourier gaussian" button)
    def _fourier_gaussian_fired(self) :
        self.curimage = imgproc.fourier.fourier_gaussian(self.curimage, 2.0)
        self.figure.axes[0].images = []
        self.figure.axes[0].imshow(self.curimage)
        wx.CallAfter(self.figure.canvas.draw)

# run everything
c = Test()
c.configure_traits()

