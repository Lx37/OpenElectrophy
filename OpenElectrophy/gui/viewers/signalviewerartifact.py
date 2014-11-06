# -*- coding: utf-8 -*-
"""
Signal viewers with visual artifact score.
Try to load and show an existing numpy array containing artifact positions
Save a numpy array with the artifact positions when closing the viewver
Show the time cursor position (x) on the viewver

arg : 
    - analogsignals
    - data path
return : nothing but save the artifacts positions on the data folder

User actions: 
    "ctrl + clic" add a new linearRegionItem to define the artifact
            that you can drag and drop 
    "suppr" suppress an artifact designed by the mouse cursor
        (no suppression if the mouse is outside a region)
    "clic" update the artifact positions 

Update artifact position values when :
    -there is a mouse click
    -there is a change on a linearRegionItem
    -user close the window
    

"""


#~ from tools import *
from signalviewer import *
from PyQt4.QtGui import QListWidget
import os, sys
from termcolor import colored, cprint

def debug():
    #QtCore.pyqtRemoveInputHook()
    from ipdb import set_trace
    set_trace()
    
#use it as
#try:
#   ..
#except:
#   debug()


class SignalViewerArtifact(SignalViewer):
    
    def __init__(self, parent = None,
                            analogsignals = [ ],
                            spiketrains_on_signals = None,
                            xsize = 10.,
                            max_point_if_decimate = 2000,
                            with_time_seeker = False,
                            fname = [], #Better way could be to have it from analogsignals?
                            **kargs
                        ):
                            
       
        SignalViewer.__init__(self, analogsignals = analogsignals, with_time_seeker = with_time_seeker)
        
        self.nb_artef = 0
        self.regions = []
        
        self.viewBox.clicked.connect(self.handle_click)
        self.analogsignals = analogsignals
        
        self.lenSig =  np.shape(self.analogsignals)[1]
        self.nb_channel = len(self.analogsignals)
        print self.nb_channel
        
        #cross hair
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.viewBox.addItem(self.vLine, ignoreBounds=True)
        self.viewBox.addItem(self.hLine, ignoreBounds=True)
        self.label = pg.LabelItem(justify='center') #TODO put the text to the right of the graphicsview
        self.graphicsview.addItem(self.label)
        
        self.pos = 0        
        self.proxy = pg.SignalProxy(self.viewBox.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.pos_artef = []
        
        self.size_wartef = 2 #(s) TODO : % de la fenetre
        
        out_path_name = os.path.splitext(fname)[0]
        self.out_file = out_path_name + '_artifact'
        print self.out_file
        if os.path.isfile(self.out_file + '.npy'):
            self.out_file += '.npy'
            print 'Load existing artifact file : ', self.out_file
            self.loadArtifact()
        else:
            print 'No existing artifact file found, a new one will be created here: ',  self.out_file
        
        
    #TODO first visu is wrong (when there is no signal) but becomes clean when signals are plotted on the viewver. why ?
    def loadArtifact(self):
        self.pos_artef = np.load(self.out_file)
        print np.shape(self.pos_artef)
        for i in range(np.shape(self.pos_artef)[0]):
            self.nb_artef += 1
            region = pg.LinearRegionItem(values = self.pos_artef[i])
            region.setZValue(self.nb_artef)
            region.sigRegionChangeFinished.connect(self.setCurentArtefactPos)
            self.regions.append(region)  #Could be a QList.. ?
            self.plot.addItem(region)
        

    def mouseMoved(self, evt):
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        if self.viewBox.sceneBoundingRect().contains(pos):
            mousePoint = self.viewBox.mapSceneToView(pos)
            index = int(mousePoint.x())
            self.pos = mousePoint.x()
            if index > 0 and index < self.lenSig:
                text = "<span style='font-size: 20pt'>x=%0.1f" % (mousePoint.x()) # Could add Y for each channel : + "<span style='color: red'>y1=%0.1f</span>" % self.analogsignals[0][index] 
                self.label.setText(text)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())




    def handle_click(self):
        modifiers = pg.Qt.QtGui.QApplication.keyboardModifiers()
        if modifiers == pg.Qt.QtCore.Qt.ShiftModifier:
            print('Shift+Click')
        elif modifiers == pg.Qt.QtCore.Qt.ControlModifier:
            self.nb_artef +=1
            print 'Nb_artef : ',self.nb_artef 
            artefpos = self.pos  ## On pourrait l avoir directement avec pg.Qt.QtGui.QCursor.pos() (=position absolue de la souris sur l ecran) puis un map2view
            print 'artefpos : ',  artefpos

            region = pg.LinearRegionItem(values = [artefpos, artefpos + self.size_wartef])
            region.setZValue(self.nb_artef)
            region.sigRegionChangeFinished.connect(self.setCurentArtefactPos)
            self.regions.append(region)  #Could be a QList.. ?
            self.plot.addItem(region)
            
        else:
            print('Click')
        self.setCurentArtefactPos()
        

        
    def keyPressEvent(self, event):
        print event.key()
        if event.key() == pg.Qt.QtCore.Qt.Key_Delete:
            print 'suppr'
            if self.regions != []:
                num_region = [i for i,j in enumerate(self.pos_artef) if  self.pos>j[0] and self.pos<j[1]]
                if num_region !=[]:
                    print num_region
                    self.viewBox.removeItem(self.regions[num_region[0]])
                    self.regions.remove(self.regions[num_region[0]])
                    self.setCurentArtefactPos()
                    num_region = []
                else:
                    print 'Please click on the artifact interval to supress'


    def setCurentArtefactPos(self):
        print 'maj artefact pos'
        if self.regions != []:
            self.pos_artef =  [self.regions[i].getRegion() for i,j in enumerate(self.regions)]
        print self.pos_artef
    
    def closeEvent(self, event):
        self.setCurentArtefactPos()
        np.save(self.out_file, np.asarray(self.pos_artef))
