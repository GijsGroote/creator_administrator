import glob
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from src.worker import Worker


from global_variables import gv
from laser_job_tracker import LaserJobTracker
from src.button import JobsQPushButton
from src.directory_functions import open_folder


from convert import split_material_name
from src.mail_manager import MailManager
from src.qdialog import SelectOptionsQDialog


from src.directory_functions import copy
from src.app import get_main_window
from src.qmessagebox import TimedQMessageBox, JobFinishedMessageBox, YesOrNoMessageBox
from laser_qlist_widget import MaterialContentQListWidget
from src.app import get_main_window
from requests.exceptions import ConnectionError

class LaserKlaarQPushButton(JobsQPushButton):

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.clicked.connect(self.on_click)
 
    def on_click(self):
        job_name = self.getCurrentItemName()
        
        job_folder_global_path = LaserJobTracker().getJobFolderGlobalPathFromJobName(job_name)
        try:
            self.sendFinishedMail(gv, job_name, job_folder_global_path)
        except ConnectionError as e:
             if not YesOrNoMessageBox(
                    text=f'Job finished mail not send because: {str(e)}\nDo you still want to mark this job as Done?',
                    parent=self).exec_() == QMessageBox.Yes:
                return

        LaserJobTracker().updateJobStatus(job_name, 'VERWERKT')
        self.refreshAllQListWidgets()



            
class MateriaalKlaarQPushButton(JobsQPushButton):

    def __init__(self, *args, **kwargs):
        JobsQPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)
 
    def on_click(self):
        material_name = self.getCurrentItemName()
        material, thickness = split_material_name(material_name)

        job_tracker = LaserJobTracker()

        # todo: not all is always done
        dxfs_names_and_global_paths = job_tracker.getDXFsAndPaths(material, thickness)

        dialog = SelectOptionsQDialog(self, dxfs_names_and_global_paths)

        if dialog.exec_() == QDialog.Accepted:

            files_names = []
            files_global_paths = []
            for item in dialog.optionsQListWidget.selectedItems():
                files_names.append(item.text())
                files_global_paths.append(item.data(1))
        else:
            return

        for file_global_path in files_global_paths:
            # find job_name
            job_name = job_tracker.fileGlobalPathToJobName(file_global_path)

            # material done, mark it done
            job_tracker.markFileIsDone(job_name, file_global_path)

            # if all is done, display message
            if job_tracker.isJobDone(job_name):
                # hey this material is done!


                TimedQMessageBox(text=f"Job finished mail send to {job_name}",
                            parent=get_main_window(self))


                job_tracker.updateJobStatus(job_name, 'VERWERKT')
                job_folder_global_path = job_tracker.getJobFolderGlobalPathFromJobName(job_name)

                try:
                    self.sendFinishedMail(gv, job_name, job_folder_global_path)
                except ConnectionError as e:
                    TimedQMessageBox(
                            text=str(e),
                            parent=self, icon=QMessageBox.Critical)
                    return


                JobFinishedMessageBox(text=f"Job {job_name} is finished, put it the Uitgifterek:\n"\
                        f"{job_tracker.getLaserFilesString(job_name)}",
                            parent=self)

        self.refreshAllQListWidgets()


class AfgekeurdQPushButton(JobsQPushButton):

    def __init__(self, *args, **kwargs):
        JobsQPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)

    def on_click(self):
        job_name = self.getCurrentItemName()
        job_tracker = LaserJobTracker()
        job_tracker.updateJobStatus(job_name, 'AFGEKEURD')
        self.refreshAllQListWidgets()

        job_folder_global_path = job_tracker.getJobFolderGlobalPathFromJobName(job_name)

        try:
            self.sendDeclinedMail(gv, job_name, job_folder_global_path)
        except ConnectionError as e:
            TimedQMessageBox(
                    text=str(e),
                    parent=self, icon=QMessageBox.Critical)
            return

class OverigQPushButton(JobsQPushButton):

    def __init__(self, *args, **kwargs):
        JobsQPushButton.__init__(self, *args, **kwargs)
        self.clicked.connect(self.on_click)


    def on_click(self):
        job_name = self.getCurrentItemName()
        print(f'De overig knop is gedrukt {job_name}')


class OptionsQPushButton(JobsQPushButton):

    def __init__(self, *args, **kwargs):
        JobsQPushButton.__init__(self, *args, **kwargs)

        self.menu = QMenu()

        self.object_name = self.objectName()
        self.menu.addAction('Open in File Explorer', self.openInFileExplorer)
        self.menu.addAction('Delete Job', self.deleteJob)

        # initialize  
        self.objectNameChanged.connect(self.storeObjectNameInit)

    def storeObjectNameInit(self):
        ''' store the object name and initialize. '''
        self.object_name = self.objectName()

        if self.object_name == 'allJobsOptionsQPushButton':
            self.menu.addAction('Move to Wachtrij', self.moveJobToWachtrij)
                        
        elif self.object_name == 'wachtrijOptionsQPushButton':
            self.menu.addAction('Copy Files to ..', self.copyLaserFilesTo)

        elif self.object_name == 'wachtrijMateriaalOptionsQPushButton':
            self.menu.addAction('Copy Files to ..', self.copyMaterialWachtrijFilesTo)

        elif self.object_name == 'verwerktOptionsQPushButton':
            self.menu.addAction('Copy Laser Files to ..', self.copyLaserFilesTo)
            self.menu.addAction('Move to Wachtrij', self.moveJobToWachtrij)
            self.menu.addAction('Move to Afgekeurd', self.moveJobToAfgekeurd)

        elif self.object_name == 'afgekeurdOptionsQPushButton':
            self.menu.addAction('Copy Laser Files to ..', self.copyLaserFilesTo)
            self.menu.addAction('Move to Wachtrij', self.moveJobToWachtrij)
            self.menu.addAction('Move to Verwerkt', self.moveJobToVerwerkt)


        else:
            raise ValueError(f'could not identify {self.object_name}')

        self.setMenu(self.menu)

    def moveJobToWachtrij(self):
        self.moveJobTo('WACHTRIJ')

    def moveJobToAfgekeurd(self):
        self.moveJobTo('AFGEKEURD')

    def moveJobToVerwerkt(self):
        self.moveJobTo('VERWERKT')

    def moveJobTo(self, new_status):
        job_name = self.getCurrentItemName()
        LaserJobTracker().updateJobStatus(job_name, new_status)
        self.refreshAllQListWidgets()

    def openInFileExplorer(self):
        job_folder_global_path = self.getJobFolderGlobalPath()
        open_folder(job_folder_global_path)

    def deleteJob(self):
        job_name = self.getCurrentItemName()
        LaserJobTracker().deleteJob(job_name)
        self.refreshAllQListWidgets()

    def getJobFolderGlobalPath(self):
        job_name = self.getCurrentItemName()
        return LaserJobTracker().getJobDict(job_name)['job_folder_global_path']
    
    def copyLaserFilesTo(self):
        '''Copy the laser files from a job to a specified folder. '''

        job_name = self.getCurrentItemName()
        laser_file_dict =  LaserJobTracker().getLaserFilesDict(job_name)
        target_folder_global_path = os.path.abspath(r'C:\\Users\\PMMA laser\\Desktop\\Laser TODO')

        for file_key, file_dict in laser_file_dict.items():

            # TODO: you could copy all unwanted stuff better

            source_item_global_path = file_dict['file_global_path']
            target_item_global_path = os.path.join(target_folder_global_path,
                file_dict['material']+"_"+file_dict['thickness']+'mm_'+file_dict['amount']+"x_"+file_key)

            copy(source_item_global_path, target_item_global_path)


        open_folder(target_folder_global_path)



    def copyMaterialWachtrijFilesTo(self):
        ''' Copy the dxf files in wachtrij to a specified folder. '''
        # get dxf files path

        material_name = get_main_window(self).findChild(
                MaterialContentQListWidget).current_item_name
        print(f"material_name {material_name}")

        material, thickness = split_material_name(material_name)

        dxfs_names_and_global_paths = LaserJobTracker().getDXFsAndPaths(material, thickness)

        target_folder_global_path = os.path.abspath(r'C:\\Users\\PMMA laser\\Desktop\\Laser TODO')

        for file_name, file_global_path in dxfs_names_and_global_paths:
            copy(file_global_path, os.path.join(target_folder_global_path, file_name))

        open_folder(target_folder_global_path)
