#known bugs 
- you must wait for finish 2d painting
- magnets dont appear on second 3d paint
import math
import matplotlib
#matplotlib.use('TkAgg')  #troche zwieksza wydajnosc matplotlib
import matplotlib.pyplot as plt
from scipy import integrate as inte
import tkinter as tk
import ast 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import numpy as np

from PyQt5 import QtCore, QtGui
import pyqtgraph as pg # http://pyqtgraph.org/
import sys
import pyqtgraph.opengl as gl   #openGL by pyqtgraph 3D dzialalo http://pyopengl.sourceforge.net/


parametersLabels=("k","m","l","g","n","xi","yi","di","ai","x0","x1","y0","y1")
parametersEntry={}
parametersSample=[1,2,4,9.81,3,[-1,1,1],[1,1,-1],[0.1,0.1,0.1],[1,-1,1.5],-1,0,-1,0]
y0Arr=[]
x0Arr=[]
def wahadlo(t, input):
    xi=ast.literal_eval(parametersEntry['xi'].get())
    yi=ast.literal_eval(parametersEntry['yi'].get())
    di=ast.literal_eval(parametersEntry['di'].get())
    ai=ast.literal_eval(parametersEntry['ai'].get())
    k = float(parametersEntry['k'].get())
    m = float(parametersEntry['m'].get())
    l = float(parametersEntry['l'].get())
    n=int(parametersEntry['n'].get())
    g = float(parametersEntry['g'].get())
    x0, x1,y0,y1 = input
   # najwyzsza pochodna
    x2 = 0
    y2 = 0
    for i in range(0,n):
        x2=x2+ai[i]*(xi[i]-x0)/(math.sqrt((xi[i]-x0)**2+(yi[i]-y0)**2+di[i]**2)**3)
        y2=y2+ai[i]*(yi[i]-y0)/(math.sqrt((xi[i]-x0)**2+(yi[i]-y0)**2+di[i]**2)**3)

    x2=x2-x1*k/m-g/l*x0
    y2=y2-y1*k/m-g/l*y0
    return [x1, x2,y1,y2]
window = tk.Tk()                     # Create a background window
window.title("Lab 7 GUI")


def integCompute():
    global x0Arr
    global y0Arr
    y0Arr.clear()
    x0Arr.clear()
    x0 = float(parametersEntry['x0'].get())
    x1 = float(parametersEntry['x1'].get())
    y0 = float(parametersEntry['y0'].get())
    y1 = float(parametersEntry['y1'].get())
    t_min = 0
    t_max = 15
    max_st = 0.02
    # tworzymy obiekt calkujacy (RK45 - Dormand–Prince)
    integrator = inte.RK45(wahadlo, t_min, [x0, x1,y0,y1], t_max, max_step = max_st)
    # listy zbierajace wyniki do wykresu
    times = [t_min]
    x0Arr = [x0]
    y0Arr = [y0]
    # kolejne kroki symulacji
    
    while integrator.t < t_max:
        integrator.step() 
        times.append(integrator.t)
        x0Arr.append(integrator.y[0])
        y0Arr.append(integrator.y[2])
    
    '''
    plot2d = tk.Toplevel(master=window) #Matplotlib ma bardzo mala wydajnosc
    plot2d.grab_set()
    plot2d.title("plot2d")
    figure2 = plt.Figure(figsize=(4,4),dpi=80)

    line2 = FigureCanvasTkAgg(figure2, plot2d)

    for i in range(0,len(x0Arr)):
        
        figure2.clear()
        figure2.add_subplot(111).plot(x0Arr[0:(i+1)],y0Arr[0:(i+1)])
        line2.get_tk_widget().pack()
        line2.draw()
        '''


def plotCreate():
    xi=ast.literal_eval(parametersEntry['xi'].get())
    yi=ast.literal_eval(parametersEntry['yi'].get())
    integCompute()
    plot=pg.plot(title="Plot 2D")   #pg jest znacznie szybsze niz matplotlib, mozna pobrac stad - http://pyqtgraph.org/
    for i in range(0,len(x0Arr)):
        plot.plot(x0Arr[0:(i+1)],y0Arr[0:(i+1)],clear=True)
        plot.plot(xi,yi,pen=None, symbol='o')
        pg.QtGui.QApplication.processEvents()
def plotCreate3D():
    #pg.mkQApp()
    i=0
    app = QtGui.QApplication(sys.argv)
    def exitHandler():
        global i
        view.removeItem(magnets)
        view.destroy()
        i=0
    app.aboutToQuit.connect(exitHandler)

    xi=ast.literal_eval(parametersEntry['xi'].get())
    yi=ast.literal_eval(parametersEntry['yi'].get())
    di=ast.literal_eval(parametersEntry['di'].get())

    integCompute()
    view = gl.GLViewWidget()
    view.show()
    ## create three grids, add each to the view
    xgrid = gl.GLGridItem()
    ygrid = gl.GLGridItem()
    zgrid = gl.GLGridItem()
    view.addItem(xgrid)
    view.addItem(ygrid)
    view.addItem(zgrid)

    ## rotate x and y grids to face the correct direction
    xgrid.rotate(90, 0, 1, 0)
    ygrid.rotate(90, 1, 0, 0)
    xgrid.translate(-4,0,4)
    ygrid.translate(0,-10,4)
    l = float(parametersEntry['l'].get())
    ## scale each grid differently
    xgrid.scale(0.4, 1, 0.1)
    ygrid.scale(0.4, 0.4, 1)
    zgrid.scale(0.4, 1, 0.1)
    # first line
    zFound=-(math.sqrt(l**2-x0Arr[0]**2-y0Arr[0]**2)-l)   #ze wzoru na odleglosc punktu w 3d
    p=np.array([[0,x0Arr[0]],[0,y0Arr[0]],[l,zFound]])
    p=p.transpose() 
    C=pg.glColor('b')
    plt = gl.GLLinePlotItem(pos=p,color=C)  #dodaje linke wahadla
    view.addItem(plt)
    pBall=np.array([[x0Arr[0]],[y0Arr[0]],[zFound]])
    pBall=pBall.transpose() 
    cBall=pg.glColor('r')
    ball = gl.GLScatterPlotItem(pos=pBall,color=cBall,size=0.3,pxMode=False)  #dodaje linke wahadla
    view.addItem(ball)

    Zm=np.zeros(len(xi))
    pM=np.array([np.add(xi,di),np.add(yi,di),Zm])
    pM=pM.transpose() 
    Cm=pg.glColor('w')
    magnets = gl.GLScatterPlotItem(pos=pM,color=Cm,size=0.25,pxMode=False)
    view.addItem(magnets)
    
    def update():
        global i
        if i==len(x0Arr):
            i=0
            return
        zFound=-(math.sqrt(l**2-x0Arr[i]**2-y0Arr[i]**2)-l)   #ze wzoru na odleglosc punktu w 3d
        p=np.array([[0,x0Arr[i]],[0,y0Arr[i]],[l,zFound]])
        p=p.transpose() 
        plt.setData(pos=p,color=C)
        pBall=np.array([[x0Arr[i]],[y0Arr[i]],[zFound]])    #aktualizuje wspolrzedne linki
        pBall=pBall.transpose()
        cBall=pg.glColor('r')
        ball.setData(pos=pBall,color=cBall,size=0.3,pxMode=False)  #aktualizuje wspolrzedne kulki
        
        i=i+1   
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(20)     #predkosc symulacji (mniej - szybciej)
    app.exec()
    '''
    xi=ast.literal_eval(parametersEntry['xi'].get())
    yi=ast.literal_eval(parametersEntry['yi'].get())
    integCompute()
    plot=pg.plot(title="Plot 3D")   #pg jest znacznie szybsze niz matplotlib, mozna pobrac stad - http://pyqtgraph.org/
    for i in range(0,len(x0Arr)):
        plot.plot(x0Arr[0:(i+1)],y0Arr[0:(i+1)],clear=True)
        plot.plot(xi,yi,pen=None, symbol='o')
        pg.QtGui.QApplication.processEvents()
        '''
def quitHandler():
    sys.exit()
for i in range(0,len(parametersLabels)):
    tk.Label(window, text=parametersLabels[i]).grid(row=i)
    temp=tk.Entry(window)
    temp.insert(i,str(parametersSample[i]))
    temp.grid(row=i,column=1)
    window.grid_rowconfigure(i,weight=1)
    parametersEntry[parametersLabels[i]]=temp

btnPaint2D = tk.Button(window, text="Paint2D", padx=4,command = plotCreate)
btnPaint3D = tk.Button(window, text="Paint3D", padx=4,command = plotCreate3D)
btnQuit = tk.Button(window, text="Quit", padx=4,command = quitHandler)
btnPaint2D.grid(row=i+1,column=0,columnspan=2)
btnPaint3D.grid(row=i+2,column=0,columnspan=2)
btnQuit.grid(row=i+3,column=0,columnspan=2)
window.protocol("WM_DELETE_WINDOW", quitHandler)

window.grid_columnconfigure(0, minsize=50,weight=1)
window.grid_columnconfigure(1, minsize=100,weight=1)
window.mainloop()





