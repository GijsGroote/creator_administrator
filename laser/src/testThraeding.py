import os, sys
import threading
import time

import pythoncom
import win32com.client

class Work (threading.Thread):
  
  def __init__ (self, marshalled_ie):
    threading.Thread.__init__ (self)
    self.marshalled_ie = marshalled_ie
  
  def run (self):
    pythoncom.CoInitialize ()
    ie = win32com.client.Dispatch (
      pythoncom.CoGetInterfaceAndReleaseStream (
        self.marshalled_ie, 
        pythoncom.IID_IDispatch
      )
    )
    print(f"Threaded LocationURL:{ie.LocationURL}")
    pythoncom.CoUninitialize ()

ie = win32com.client.Dispatch ("InternetExplorer.Application")
ie.Visible = 1
ie.Navigate ("http://python.org")
while ie.Busy: 
  time.sleep (1)
print("LocationURL:", ie.LocationURL)

marshalled_ie = pythoncom.CoMarshalInterThreadInterfaceInStream (
  pythoncom.IID_IDispatch, ie
)
work = Work (marshalled_ie)
work.start ()
work.join ()

ie.Quit ()