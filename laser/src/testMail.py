import win32com.client
import pythoncom

import os, sys
import threading
import time


class Work (threading.Thread):
  
  def __init__ (self, fn,  marshalled_ol):
    threading.Thread.__init__ (self)
    # self.marshalled_ol = marshalled_ol
    self.fn = fn
  
  def run (self):
    pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
    # pythoncom.CoInitialize(pythoncom.COINIT_MULTITHREADED)
    # ol = win32com.client.Dispatch (
    #   pythoncom.CoGetInterfaceAndReleaseStream (
    #     self.marshalled_ol, 
    #     pythoncom.IID_IDispatch
    #   )
    # )

# 
    print('start functino please')
    self.fn()
    print(f"Threaded LocationURL:{ol.LocationURL}")
    
    
    win32com.CoUninitialize ()


class MailClass():
     
    def __init__(self) -> None:
        # pythoncom.CoInitialize()

        self.ol =  win32com.client.Dispatch("Outlook.Application").GetNamespace('MAPI')

        # Create id
        # self.marshalled_ol = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch, self.ol)

        print("Threaded LocationURL:", self.ol)

        # print("Threaded marshalled LocationURL:", self.marshalled_ol)

        self.inbox = self.ol.GetDefaultFolder(6)

        print('do some in the class')
        
        for message in self.inbox.Items:
            if message.UnRead:
                print(f'append message now {message}')



    def getNewMail(self) -> list:
        print('now in the getNewMail functions')
        msgs = []

        for message in self.inbox.Items:
            if message.UnRead:
                msgs.append(message)

        return msgs
                        
                    

def main():
    mail_class = MailClass()

    work = Work(mail_class.getNewMail, 3)
    work.start ()
    work.join ()

    # mail_class.ol.Quit ()

  


if __name__ == '__main__':
    main()