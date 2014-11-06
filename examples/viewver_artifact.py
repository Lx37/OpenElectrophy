# -*- coding: utf-8 -*-
"""
Visual Artifact viewers
-----------------------------------------------

For long signal you can not compute the whole maps and plot it with
matplotlib, it is too big.

The Qt viewers allow you to diplsay chunk by chunk the timefrequency map
of the signal.


"""

import sys
sys.path.append('..')

if __name__== '__main__':

    
    from OpenElectrophy.gui.viewers.signalviewerartifact import *
    from OpenElectrophy import TryItIO
    from PyQt4.QtGui import QApplication
    app = QApplication([ ])
    
    bl = TryItIO().read(nb_segment=1, duration = 10)[0]
    w = SignalViewerArtifact(analogsignals = bl.segments[0].analogsignals, fname = './test', with_time_seeker = True)
    w.show()
    
    app.exec_()
    