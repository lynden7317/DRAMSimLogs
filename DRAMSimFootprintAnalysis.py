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
logging.basicConfig(level = logging.DEBUG)
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
        
        self.inputFrame = None
        self.inputLabels = {}
        
        self.totalInputs = 0
        self.directoryName = None
        self.fileNames = None

        self.totalFootprint = []
        
               
        Button(self.master, text='open byte logs', command = lambda opt='new':self.askopenfilenames(opt)).grid(row=0, column=0, sticky=E+W)        
        Button(self.master, text='add byte logs', command = lambda opt='add':self.askopenfilenames(opt)).grid(row=0, column=1, sticky=E+W)
        Button(self.master, text='plot', command=self.canvasPlot).grid(row=0, column=2, sticky=E+W)
        
        #but_opt = {'fill': Tkconstants.BOTH, 'padx':5, 'pady': 5} 
        #Button(self, text = 'askopenfilenames', command = self.askopenfilenames).pack(**but_opt)
        #Button(self, text = 'Run footprint analysis', command = self.footprint).pack(**but_opt)
        
        
        # ==== 設定 directory options ====
        #self.dir_opt = options = {}
        #options['initialdir'] = 'C:\\'
        #options['mustexist'] = False
        #options['parent'] = root
        #options['title'] = 'This is a title'
    

    def askopenfilenames(self, opt):
        # ==== set File options ====
        file_opt = options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        options['initialdir'] = 'D:\\'
        options['initialfile'] = 'myfile.txt'
        options['parent'] = root
        options['title'] = 'This is a title'
        
        if opt == 'new':            
            self.fileNames = tkFileDialog.askopenfilenames(**file_opt)
            if len(self.fileNames) > 0:
                self._loadByteLogs()
        
        if opt == 'add':            
            self.fileNames = tkFileDialog.askopenfilenames(**file_opt)
            if len(self.fileNames) > 0:
                self._addByteLogs()
        
        self.inputLabels[self.totalInputs] = self.fileNames[0].split('/')[-2]
        self._addLabels()
                
    
    def canvasPlot(self):
        if self.FF.canvas != None:
            del self.FF
            del self.Frame2
            self.FF = Figure(figsize = (5, 5), dpi = 100)
            self.Frame2 = Frame(self.master)
            self.Frame2.grid(row=2, column=0, rowspan=3, columnspan=5, sticky=W+E+N+S, pady=10)
        
        logging.debug('<canvasPlot> Var= %s', self.comBoxVar.get())
        clockFrq = 1  # 1GHz
        epoch = 5000  # 5000 clock
        timestamp = (int(self.comBoxVar.get().split(' ')[0]), int(self.comBoxVar.get().split(' ')[0])/5)
        
        logging.debug('<canvasPlot> timestamp= %s', timestamp)
        logging.debug('<canvasPlot> length of totalInputs= %s', self.totalInputs)        
        logging.debug('<canvasPlot> length of totalFootprint= %s', len(self.totalFootprint))
        
        for ftId in xrange(self.totalInputs):
            totalChFootprint = []
            totalChBW = []
            ft = self.totalFootprint[ftId]
            logging.debug('<canvasPlot> ftId= %s', ftId)
            logging.debug('<canvasPlot> length of ft= %s', len(self.totalFootprint[ftId]))   
            # === Change epoch to timestamp ===
            timeFootprint = []
            stamp = len(ft)/timestamp[1]
            #res = len(ft)%timestamp[1]
            for i in xrange(stamp):
                sumByte = 0.0
                for j in xrange(timestamp[1]):
                    sumByte += ft[(i*timestamp[1])+j]
        
                timeFootprint.append(sumByte/float(timestamp[1]))
            
            totalChFootprint = copy.copy(timeFootprint)
            # ==== Bandwidth ====
            for i in xrange(len(timeFootprint)):
                # === timeFootprint[i] in KB, clock in GHz --> timeFootprint*1000 change to byte ===
                # === BW: (MemoryAccess * ClockFreq)/TotalClock === 
                totalChBW.append(round(float(timeFootprint[i]*clockFrq*1000)/float(epoch), 3))
            
            totalTransfer = np.sum(totalChFootprint)
            avgBW = np.mean(totalChBW)
            logging.info('Total Bytes Transferred= %s KB', totalTransfer)
            logging.info('Average Bandwidth= %s GB/s', avgBW)
        
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
        
        p1.legend([self.inputLabels[t] for t in sorted(self.inputLabels.keys())])
        p2.legend([self.inputLabels[t] for t in sorted(self.inputLabels.keys())])
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
    
    def _addLabels(self):
        if self.inputFrame == None:
            self.inputFrame = Frame(self.Frame1)
            for i in sorted(self.inputLabels.keys()):
                label1 = Label(self.inputFrame, text='*'+str(i)+'. ')
                label1.grid(row=0, column=0)
                label2 = Label(self.inputFrame, text=self.inputLabels[i])
                label2.grid(row=0, column=1)
        else:
            del self.inputFrame
            # ==== renew ====
            self.inputFrame = Frame(self.Frame1)
            index = 0
            for i in sorted(self.inputLabels.keys()):
                label1 = Label(self.inputFrame, text='*'+str(i)+'. ')
                label1.grid(row=index/4, column=index%4)
                index += 1
                label2 = Label(self.inputFrame, text=self.inputLabels[i])
                label2.grid(row=index/4, column=index%4)
                index += 1
            
        self.inputFrame.grid(row=0, column=1, padx=30)                      
            

    def _addByteLogs(self):
        logging.debug('add file name list: %s', self.fileNames)
        self.totalInputs += 1
        
        self.totalFootprint.append([])
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
                byteEpoch = re.findall('total\S*= ([0-9]+)', line)
                byteLog.append(int(byteEpoch[0]))
            
            for i in xrange(len(byteLog)-1):
                # ==== Change to KB ====
                B = round(float((byteLog[i+1] - byteLog[i]))/1000.0, 2)
                footprint.append(B)
            
            if len(self.totalFootprint[self.totalInputs-1]) <= 0:
                self.totalFootprint[self.totalInputs-1] = copy.copy(footprint)
            else:
                for idx in xrange(len(footprint)):
                    self.totalFootprint[self.totalInputs-1][idx] += footprint[idx]
        
        
    def _loadByteLogs(self):
        logging.debug('file name list: %s', self.fileNames)
        self.totalInputs += 1
        if len(self.totalFootprint) > 0:
            del self.totalFootprint
            self.totalFootprint = []
            
        self.totalFootprint.append([])
        for fname in self.fileNames:
            try:
                fhead = open(fname)
            except:
                logging.error('File %s cannot be opened', fname)
                exit(1)
            
            byteLog = [0]
            footprint = [0]

            for line in fhead:
                line = line.rstrip()
                byteEpoch = re.findall('total\S*= ([0-9]+)', line)
                byteLog.append(int(byteEpoch[0]))
            
            for i in xrange(len(byteLog)-1):
                # ==== Change to KB ====
                B = round(float((byteLog[i+1] - byteLog[i]))/1000.0, 2)
                footprint.append(B)
            
            if len(self.totalFootprint[self.totalInputs-1]) <= 0:
                self.totalFootprint[self.totalInputs-1] = copy.copy(footprint)
            else:
                for idx in xrange(len(footprint)):
                    self.totalFootprint[self.totalInputs-1][idx] += footprint[idx]
            


if __name__ == '__main__':  
    root = Tk()
    root.geometry("1200x800+100+100")
    app = Application(master=root)    
    app.mainloop()    
    #FileDialogEx(root).pack()
    #root.mainloop()
