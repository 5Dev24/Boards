import tkinter, threading

class Window:

	def __init__(self):
		self._master = tkinter.Tk()
		self._canvas = tkinter.Canvas(self._master, width = 800, height = 600)
		self._canvas.pack()

	def finalize(self):
		self._master.mainloop()

def test():
	win = Window()
	win.finalize()

if __name__ == "__main__": test()