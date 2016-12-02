# -*- coding: utf-8 -*-
"""
Created on Thu Dec 01 16:23:26 2016

@author: lynden
"""
from Tkinter import *
import ttk
import Tkconstants
import tkFileDialog

import logging
import re
import numpy as np
import copy
#import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

reload(logging)
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)


class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.master.title('DRAMSim Memory Footprint')
        
        self.gridRow = 3
        self.gridCol = 5
        for r in xrange(self.gridRow):
            self.master.rowconfigure(r, weight=1)    
        for c in xrange(self.gridCol):
            self.master.columnconfigure(c, weight=1)
            #Button(master, text="Button {0}".format(c)).grid(row=0, column=c, sticky=E+W)

        self.Frame1 = Frame(self.master)
        self.Frame1.grid(row=1, column=0, rowspan=3, columnspan=2, sticky=W+E+N+S, pady=10)
        self._combox()
        self.Frame2 = Frame(self.master)
        self.Frame2.grid(row=2, column=0, rowspan=3, columnspan=5, sticky=W+E+N+S, pady=10)  
        # === for using embedding canvas ====                         
        self.FF = Figure(figsize = (5, 5), dpi = 100)
        
        self.directoryName = None
        self.fileNames = None
        self.totalCHidx = []
        self.totalByteLogs = []
        self.totalFootprint = []
        
               
        Button(self.master, text='open byte logs', command=self.askopenfilenames).grid(row=0, column=0, sticky=E+W)
        Button(self.master, text='plot', command=self.canvasPlot).grid(row=0, column=1, sticky=E+W)
        
        #but_opt = {'fill': Tkconstants.BOTH, 'padx':5, 'pady': 5} 
        #Button(self, text = 'askopenfilenames', command = self.askopenfilenames).pack(**but_opt)
        #Button(self, text = 'Run footprint analysis', command = self.footprint).pack(**but_opt)
        
        
        # ==== 設定 directory options ====
        #self.dir_opt = options = {}
        #options['initialdir'] = 'C:\\'
        #options['mustexist'] = False
        #options['parent'] = root
        #options['title'] = 'This is a title'
    

    def askopenfilenames(self):
        # ==== set File options ====
        file_opt = options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        options['initialdir'] = 'C:\\'
        options['initialfile'] = 'myfile.txt'
        options['parent'] = root
        options['title'] = 'This is a title'
        
        self.fileNames = tkFileDialog.askopenfilenames(**file_opt)
        if len(self.fileNames) > 0:
            self._loadByteLogs()
    
    def canvasPlot(self):
        if self.FF.canvas != None:
            del self.FF
            del self.Frame2
            self.FF = Figure(figsize = (5, 5), dpi = 100)
            self.Frame2 = Frame(self.master)
            self.Frame2.grid(row=2, column=0, rowspan=3, columnspan=5, sticky=W+E+N+S, pady=10)
        
        logging.debug('Var: %s', self.comBoxVar.get())
        clockFrq = 1  # 1GHz
        epoch = 5000  # 5000 clock
        timestamp = (int(self.comBoxVar.get().split(' ')[0]), int(self.comBoxVar.get().split(' ')[0])/5)
        logging.debug('timestamp= %s', timestamp)
        
        totalChFootprint = []
        totalChBW = []
        for ft in self.totalFootprint:
            # === Change epoch to timestamp ===
            timeFootprint = []
            stamp = len(ft)/timestamp[1]
            res = len(ft)%timestamp[1]
            for i in xrange(stamp):
                sumByte = 0.0
                for j in xrange(timestamp[1]):
                    sumByte += ft[(i*timestamp[1])+j]
        
                timeFootprint.append(sumByte/float(timestamp[1]))
            
            if len(totalChFootprint) == 0:
                totalChFootprint = copy.copy(timeFootprint)
            else:    
                for i in xrange(len(timeFootprint)):
                    totalChFootprint[i] = totalChFootprint[i] + timeFootprint[i]
            
            # ==== Bandwidth ====     
            if len(totalChBW) == 0:
                for i in xrange(len(timeFootprint)):
                    totalChBW.append(round(float(timeFootprint[i]*clockFrq*1000)/float(epoch), 3))
            else:
                for i in xrange(len(timeFootprint)):
                    totalChBW[i] = totalChBW[i] + round(float(timeFootprint[i]*clockFrq*1000)/float(epoch), 3)
        
        # ==== plots ====
        p1 = self.FF.add_subplot(211)
        XX = np.linspace(0, len(totalChFootprint)-1, len(totalChFootprint), endpoint=True)
        p1.plot(XX, totalChFootprint)
        p1.set_ylabel('KB', fontsize=14)
        p1.set_title('Sum of total CH')
        
        p2 = self.FF.add_subplot(212)
        p2.plot(XX, totalChBW)
        p2.set_ylabel('BW(GB/s)', fontsize=14)
        p2.set_xlabel(str(timestamp[0])+' us', fontsize=14)
        
        canvas = FigureCanvasTkAgg(self.FF, master=self.Frame2)
        canvas.show()
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True, pady=10)

    
    def _combox(self):
        clockFrq = 1  # 1GHz
        epoch = 5000  # 5000 clock
        #timestamp = [ (5, 1), (10, 2), (50, 10), (100, 20), (200, 40) ] #(5 us, 1 based)
        timestamp = (5000, 1000)
        
        label = Label(self.Frame1, text='5 us per epoch\nEach epoch contains 5000 cycles')
        self.comBoxVar = StringVar()
        comBox = ttk.Combobox(self.Frame1, textvariable = self.comBoxVar, state = 'readonly')
        comBox['value'] = ('5 us', '10 us', '50 us', '100 us', '200 us', '1000 us', '2000 us')
        comBox.current(0)
        label.grid(row=0, column=0)
        comBox.grid(row=1, column=0)
        #comBox.bind('<<ComboboxSelected>>', self._comboxCallback)
    
    '''
    def _comboxCallback(self, event):
        logging.debug('Var: %s', self.comBoxVar.get())
    '''


    def _loadByteLogs(self):
        logging.debug('file name list: %s', self.fileNames)
        if len(self.totalFootprint) > 0:
            del self.totalCHidx, self.totalByteLogs, self.totalFootprint
            self.totalCHidx = []
            self.totalByteLogs = []
            self.totalFootprint = []
            
        
        for fname in self.fileNames:
            try:
                fhead = open(fname)
            except:
                logging.error('File %s cannot be opened', fname)
                exit(1)
            
            byteLog = [0]
            footprint = [0]
            #CH = 0
            for line in fhead:
                line = line.rstrip()
                CH = int(re.findall('Ch\S*=([0-9])', line)[0])
                byteEpoch = re.findall('total\S*= ([0-9]+)', line)
                byteLog.append(int(byteEpoch[0]))
            
            for i in xrange(len(byteLog)-1):
                B = (byteLog[i+1] - byteLog[i])/1000
                footprint.append(B)
            
            self.totalCHidx.append(CH)
            self.totalByteLogs.append(byteLog)
            self.totalFootprint.append(footprint)


if __name__ == '__main__':  
    root = Tk()
    root.geometry("1200x800+100+100")
    app = Application(master=root)    
    app.mainloop()    
    #FileDialogEx(root).pack()
    #root.mainloop()
