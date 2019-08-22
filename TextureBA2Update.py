import os
import pathlib
import sys
import traceback
import shutil

from pathlib import PurePath
from functools import partial
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QFileSystemModel, QLabel, QListWidget, QListWidgetItem, QMessageBox, QVBoxLayout
from PyQt5.QtWidgets import QPlainTextEdit, QDialog, QHBoxLayout

PLUGIN_NAME = "TextureBA2Update"

# XXX: Not really sure what the proper place for the UI files should be
#      but either way, I had to add the directory I put it in the system path
CWD = os.getcwd()
PLUGIN_DIR = "%s/plugins" % CWD
sys.path.append(PLUGIN_DIR)
import TextureBA2MainDialog

# Suffix to append to texture files and main BA2 files
DISABLE_SUFFIX = ".DISABLED"

# XXX: I'm not sure why this order was in my ini files, but I took it in order as
# loaded so the last loaded BA2 takes priority.
BASE_TEXTURE_FILES = [
    "Fallout4 - Textures1.ba2",
    "Fallout4 - Textures2.ba2",
    "Fallout4 - Textures3.ba2",
    "Fallout4 - Textures4.ba2",
    "Fallout4 - Textures5.ba2",
    "Fallout4 - Textures6.ba2",
    "Fallout4 - Textures7.ba2",
    "Fallout4 - Textures8.ba2",
    "Fallout4 - Textures9.ba2",
    "DLCworkshop01 - Textures.ba2",
    "DLCworkshop03 - Textures.ba2",
    "DLCNukaWorld - Textures.ba2",
    "DLCCoast - Textures.ba2",
    "DLCworkshop02 - Textures.ba2",
    "DLCRobot - Textures.ba2",
    ]

# XXX: Working directories, I need to figure out how to be able to set this in the plugin configs
TEXTURE_WORK_DIR = os.path.join(CWD, "TextureWorkDir")
BA2_WORK_DIR = os.path.join(CWD, "BA2WorkDir")

# Worker thread signals, UI updates happen on the main UI thread, it's safer that way.
class WorkerSignals(QObject):
    error = pyqtSignal(tuple)
    result = pyqtSignal(bool)
    finished = pyqtSignal()
    progress = pyqtSignal(object)
    log = pyqtSignal(object)
    started = pyqtSignal()

# Generic worker thread class to be used with QThreadPool. Operations that take a long
# time are done either in a thread or separate process, this allows the UI to stay
# responsive.
class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['logSignal'] = self.signals.log
        self.kwargs['progressSignal'] = self.signals.progress

    def run(self):
        try:
            self.signals.started.emit()
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

# Because of issues I found with passing a method callback into slots,
# I use signals/slots for to continue operations after asynchronous tasks.
# Currently the asynchronous tasks these are for are for cleaning up the
# texture work directory.
class WorkDialogSignals(QObject):
    archive2Start = pyqtSignal()
    unarchive2Start = pyqtSignal()

class WorkDialog(QDialog, Ui_TextureBA2MainDialog):
    def __init__(self, parentWidget, organizer):
        super(QDialog, self).__init__(parentWidget)
        super(Ui_TextureBA2MainDialog, self).__init__()
        self.setupUi(self)
        self.organizer = organizer
        # reverse the list to pop the mod at the bottom first, that's the one
        # that gets to use the texture if found
        self.modList = self.organizer.modsSortedByProfilePriority()
        self.modList.reverse()
        self.archiveWorkProcess = None
        self.parentWidget = parentWidget
        self.gameDataDir = self.organizer.managedGame().dataDirectory().absolutePath()
        self.threadPool = QThreadPool()
        self.originalBA2Files = BASE_TEXTURE_FILES[:] # reverse order
        self.canceled = False
        self.updateButton.clicked.connect(self.updateButton_clicked)
        self.cancelButton.clicked.connect(self.cancelButton_clicked)
        self.enableButton.clicked.connect(self.enableButton_clicked)
        self.logTextEdit.setReadOnly(True)
        self.progressTextEdit.setReadOnly(True)
        self.ba2File = None
        self.signals = WorkDialogSignals()
        if (not os.path.exists(BA2_WORK_DIR)):
            os.mkdir(BA2_WORK_DIR)
        self.BackupBaseBA2Files()

    # Disable the base BA2 files if they are not already renamed. Also removes
    # the non-disabled file if it is there. Not sure if I should re-enable the
    # files if the process is canceled.
    def BackupBaseBA2Files(self):
        for ba2 in BASE_TEXTURE_FILES:
            filePath = os.path.join(self.gameDataDir, ba2)
            # Don'te remove the original if both backup and original are there.
            if (self.DisableFile(filePath, remove=False)):
                self.ProgressOutput("Disabled %s" % ba2)

    # Move the new BA2 files into game data dir, will copy if it is a different
    # file system (shutil.move() takes care of this according to the docs).
    def MoveNewBA2Files(self):
        for ba2 in BASE_TEXTURE_FILES:
            filePath = os.path.join(self.gameDataDir, ba2)
            newPath = os.path.join(BA2_WORK_DIR, ba2)
            shutil.move(newPath, filePath)
            self.ProgressOutput("Copied new %s" % ba2)

    # Output to the log text area, keeps the scroll at the bottom.
    # XXX: Need to make this smarter so that it a user scroll event
    # happens then it doesn't move the cursor tot he begining of the
    # last line.
    def LogOutput(self, text):
        self.logTextEdit.append(self.tr(text))
        self.logTextEdit.moveCursor(QTextCursor.End)
        self.logTextEdit.moveCursor(QTextCursor.StartOfLine)
        self.logTextEdit.ensureCursorVisible()

    # Output to the progress text area, keeps the scroll at the bottom.
    def ProgressOutput(self, text):
        self.progressTextEdit.append(self.tr(text))
        self.progressTextEdit.moveCursor(QTextCursor.End)
        self.progressTextEdit.moveCursor(QTextCursor.StartOfLine)
        self.progressTextEdit.ensureCursorVisible()

    # Re-enable a file by removing the old file and renaming the DISABLED file,
    # checks for existance first.
    def EnableFile(self, disablePath, logSignal=None):
        # if disabled file doesn't exist, just return
        # rename disabled file to file without DISABLED_SUFFIX
        if (not disablePath.endswith(DISABLE_SUFFIX)):
            return False
        if (os.path.exists(disablePath)):
            filePath = disablePath.replace(DISABLE_SUFFIX, "")
            if (os.path.exists(filePath)):
                os.remove(filePath)
            os.rename(disablePath, filePath)
        else:
            return False
        return True

    # The thread that worked to re-enable texture files finished slot.
    def EnableTextureWorkerFinished(self):
        self.enableButton.setEnabled(True)
        self.updateButton.setEnabled(True)

    # The worker thread to rename disabled textures so they are usable again.
    def EnableTextureWorker(self, logSignal, progressSignal):
        progressSignal.emit("EnableTextureWorker Started")
        for modName in self.modList:
            if (self.organizer.modList().state(modName) & 0x2) != 0:
                mod = self.organizer.getMod(modName)
                modDir = mod.absolutePath()
                modDir = os.path.join(modDir, "textures")
                for root, dirs, files in os.walk(modDir):
                    for f in files:
                        relPath = os.path.join(root, f)
                        full = os.path.join(modDir, relPath)
                        if (self.EnableFile(full, logSignal)):
                            progressSignal.emit("Enabled %s" % full)
                        else:
                            logSignal.emit("--- %s" % full)
        return True

    # When the enableButton is clicked this is called to start the worker thread.
    def StartEnableTextureWork(self):
        self.enableButton.setEnabled(False)
        self.updateButton.setEnabled(False)
        worker = Worker(self.EnableTextureWorker)
        worker.signals.started.connect(self.TextureWorkerStarted)
        worker.signals.progress.connect(self.WorkerProgress)
        worker.signals.log.connect(self.WorkerLog)
        worker.signals.finished.connect(self.EnableTextureWorkerFinished)
        worker.signals.result.connect(self.TextureWorkerResult)
        self.threadPool.start(worker)

    # Rename the given file with the DISABLE_SUFFIX, only if
    # it doesn't already have the suffix.
    def DisableFile(self, filePath, logSignal=None, remove=True):
        # if disabled file exists, remove remaining file if it's there
        # else rename file to disabled file
        if (filePath.endswith(DISABLE_SUFFIX)):
            path = filePath.replace(DISABLE_SUFFIX, "")
            if (remove and os.path.exists(path)):
                os.remove(path)
            return False
        disablePath = filePath + DISABLE_SUFFIX
        if (os.path.exists(disablePath)):
            if (remove and os.path.exists(filePath)):
                os.remove(filePath)
            return False
        else:
            if (os.path.exists(filePath)):
                os.rename(filePath, disablePath)
            else:
                return False
        return True

    # Worker started slot, doesn't do anything for now.
    def TextureWorkerStarted(self):
        self.LogOutput("****** Worker thread started *********")

    # Worker results slot, doesn't do anything for now.
    def TextureWorkerResult(self, result):
        self.LogOutput("****** WorkerResult %r *********" % result)

    # The worker thread that copied textures from mods to the texture work directory
    # finished. The next state is to start the Archive2 process to create the new BA2 file.
    def TextureWorkerFinished(self):
        if (self.canceled):
            return
        self.LogOutput("**************** Start Archiver work here ****************")
        self.StartArchiveWork()

    # WorkerProgress slot, outputs to the progress text area
    def WorkerProgress(self, output):
        self.ProgressOutput(output)

    # WorkerLog slot, outputs to the log text area
    def WorkerLog(self, output):
        self.LogOutput(output)

    # This is the check for each mod (in reverse order so the mod at the bottom of
    # the list takes priority) to see if the texture file in the texture work directory
    # has a corresponding texture file. If it does, copy the file from the first mod (last loaded)
    # and disable the file in all mods.
    def TextureCheckMods(self, relPath, logSignal):
        mods = []
        used = False
        for modName in self.modList:
            if (self.organizer.modList().state(modName) & 0x2) != 0:
                mod = self.organizer.getMod(modName)
                modDir = mod.absolutePath()
                full = os.path.join(modDir, relPath)
                if (os.path.exists(full)):
                    if (not used):
                        logSignal.emit("Using '%s' for '%s'" % (modName, relPath))
                        workFull = os.path.join(TEXTURE_WORK_DIR, relPath)
                        shutil.copy2(full, workFull)
                        used = True
                    result = self.DisableFile(full, logSignal)
                    if (not result):
                        logSignal.emit("*** Error disabling: %s" % full)
                    mods.append(modName)
        if (len(mods) == 0):
            # This represents a texture file that has no replacement texture, could be
            # useful info for people looking for non-upgraded files to update.
            logSignal.emit("No replacement texture %s" % relPath)

    # The thread work method for walking the unpacked BA2 file textures and checking
    # the mods for replacement textures.
    def TextureWorker(self, logSignal, progressSignal):
        progressSignal.emit("TextureWorker Started")
        for root, dirs, files in os.walk(TEXTURE_WORK_DIR):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, TEXTURE_WORK_DIR)
                self.TextureCheckMods(rel, logSignal)
        return True

    # The slot for reading output from the Archive2 process, outputs to the log pane.
    def ArchiveProcessReadOutput(self, p):
        try:
            while (p.canReadLine() == True):
                line = p.readLine().data().rstrip()
                if (line != None and line != ""):
                    self.LogOutput(line)
        except:
            QMessageBox.information(self, self.tr(PLUGIN_NAME), self.tr("readline exception"))
            pass

    # The Archive2 packing is finished, call StartWork again to pick up the next BA2 file.
    def ArchiveProcessFinished(self):
        self.archiveWorkProcess = None
        self.StartWork()

    # Start the Archive2 process to pack up the new BA2 file.
    def StartArchiveWork(self):
        if (self.ba2File == None):
            self.ProgressOutput("ERROR: Archive2 ba2File empty")
            return

        if (self.canceled):
            return

        self.archiveWorkProcess = QProcess()
        self.archiveWorkProcess.readyReadStandardOutput.connect(partial(self.ArchiveProcessReadOutput, self.archiveWorkProcess))
        self.archiveWorkProcess.finished.connect(self.ArchiveProcessFinished)
        self.archiveWorkProcess.setProcessChannelMode(QProcess.MergedChannels)
        ba2Path = os.path.join(BA2_WORK_DIR, self.ba2File)
        self.ProgressOutput("Archive2 compress: %s " % ba2Path)
        if (os.path.exists(ba2Path)):
            os.remove(ba2Path)
        texturePath = os.path.join(TEXTURE_WORK_DIR, "textures")
        archive2path = self.organizer.pluginSetting(PLUGIN_NAME, "Archive2.exe-path")
        self.archiveWorkProcess.setProgram(archive2path)
        self.archiveWorkProcess.setArguments([texturePath, "-f=DDS", "-c=%s" % ba2Path, "-r=%s" % TEXTURE_WORK_DIR])
        self.archiveWorkProcess.start()

    # Unpacking of the BA2 process finished slot, start the TextureWorker thread for copying textures.
    def UnArchiveProcessFinished(self):
        self.archiveWorkProcess = None
        if (not self.canceled):
            self.ProgressOutput("Copy newer textures to BA2 work directory")
            worker = Worker(self.TextureWorker)
            worker.signals.started.connect(self.TextureWorkerStarted)
            worker.signals.progress.connect(self.WorkerProgress)
            worker.signals.log.connect(self.WorkerLog)
            worker.signals.finished.connect(self.TextureWorkerFinished)
            worker.signals.result.connect(self.TextureWorkerResult)
            self.threadPool.start(worker)

    # This is the finished slot for the final cleanup thread after the BA2
    # files were all processed. Moves the new BA2 files into place.
    def WorkDone(self):
        self.signals.unarchive2Start.disconnect()
        self.enableButton.setEnabled(True)
        self.MoveNewBA2Files()
        self.ProgressOutput("**************** All Done ****************")

    # Entry point to do work, called repeatedly for each BA2 file popping them off
    # the list in last loaded to first loaded order.
    def StartWork(self):
        if (len(self.originalBA2Files) == 0):
            self.signals.unarchive2Start.connect(self.WorkDone)
            self.CleanWorkDir(TEXTURE_WORK_DIR, self.signals.unarchive2Start)
            return

        if (self.archiveWorkProcess != None):
            self.LogOutput("**************** Work already started ****************")
            return

        # CleanWorkDir might take a while, so it is asynchronous in a thread,
        # __StartWork2 is the callback when the work is done
        self.signals.unarchive2Start.connect(self.__StartWork2)
        self.CleanWorkDir(TEXTURE_WORK_DIR, self.signals.unarchive2Start)

    # The finished slot for the cleaning of the work directory to continue where
    # StartWork left off.
    def __StartWork2(self):
        self.signals.unarchive2Start.disconnect()
        self.updateButton.setEnabled(False)
        self.enableButton.setEnabled(False)
        self.ba2File = self.originalBA2Files.pop()
        self.archiveWorkProcess = QProcess()
        self.archiveWorkProcess.readyReadStandardOutput.connect(partial(self.ArchiveProcessReadOutput, self.archiveWorkProcess))
        self.archiveWorkProcess.finished.connect(self.UnArchiveProcessFinished)
        self.archiveWorkProcess.setProcessChannelMode(QProcess.MergedChannels)
        # take the backup ba2 files, not any new ones that might be there
        ba2Path = os.path.join(self.gameDataDir, self.ba2File) + DISABLE_SUFFIX
        self.ProgressOutput("Archive2 extract: %s " % ba2Path)
        self.logTextEdit.clear()
        self.archiveWorkProcess.setProgram("Archive2.exe")
        self.archiveWorkProcess.setArguments([ba2Path, '-e=%s' % TEXTURE_WORK_DIR])
        self.archiveWorkProcess.start()

    # Cleanup the texture work directory, traverses in reverse order to remove from leaves first.
    def CleanDirectory(self, directory, logSignal=None):
        for root, dirs, files in reversed(list(os.walk(directory))):
            for f in files:
                full = os.path.join(root, f)
                if (logSignal != None):
                    logSignal.emit("rm %s" % full)
                else:
                    self.LogOutput("rm %s" % full)
                os.remove(full)
            for d in dirs:
                full = os.path.join(root, d)
                if (logSignal != None):
                    logSignal.emit("rmdir %s" % full)
                else:
                    self.LogOutput("rmdir %s" % full)
                os.rmdir(full)

    # Worker thread method for the cleanup of the TEXTURE_WORK_DIR.
    def CleanWorkDirWorker(self, directory, logSignal, progressSignal):
        if (not os.path.exists(directory)):
            if (logSignal != None):
                logSignal.emit("mkdir %s" % directory)
            else:
                self.LogOutput("mkdir %s" % directory)
            os.mkdir(TEXTURE_WORK_DIR)
        else:
            self.CleanDirectory(directory, logSignal)
        return True

    # Cleanup is finished, emit the finished signal to continue work in the UI thread.
    def CleanWorkDirFinished(self, finishedSignal=None):
        if (finishedSignal != None):
            finishedSignal.emit()

    # Start up the cleanup thread for the texture work directory.
    def CleanWorkDir(self, directory, finishedSignal):
        if (not os.path.exists(directory)):
            # Driectory doesn't exist, create it
            os.mkdir(directory)

        if (not os.path.isdir(directory)):
            #XXX: Maybe this isn't a good idea? Still, shouldn't be there as a file.
            os.remove(directory)

        if (not os.listdir(directory)):
            # Driectory is empty, just emit the signal and return
            if (finishedSignal != None):
                finishedSignal.emit()
            return

        self.ProgressOutput("Cleaning directory %s" % directory)
        worker = Worker(self.CleanWorkDirWorker, directory)
        worker.signals.progress.connect(self.WorkerProgress)
        worker.signals.log.connect(self.WorkerLog)
        worker.signals.finished.connect(partial(self.CleanWorkDirFinished, finishedSignal))
        self.threadPool.start(worker)

    # XXX: Need to think about the kind of cleanup that should be done if cancel is hit.
    def cancelButton_clicked(self):
        if (self.archiveWorkProcess != None):
            self.canceled = True
            QMessageBox.information(self, self.tr(PLUGIN_NAME), self.tr("Kill the process"))
        self.done(QDialog.Rejected)

    # Update BA2s button was clicked, start stuff up.
    def updateButton_clicked(self):
        if (self.archiveWorkProcess != None):
            QMessageBox.information(self, self.tr(PLUGIN_NAME), self.tr("Already processing"))
        try:
            self.StartWork()
        except:
            QMessageBox.information(self, self.tr(PLUGIN_NAME), self.tr("ERROR: StartWork"))

    # Enable button was clicked, start the thread to re-enable any disabled texture files
    # in each mod.
    def enableButton_clicked(self):
        self.StartEnableTextureWork()

# The IPluginTool cleass from MO2
class TextureBA2Update(mobase.IPluginTool):
    def __init__(self):
        super(TextureBA2Update, self).__init__()
        self.__parentWidget = None
        self.__organizer = None

    def init(self, organizer):
        self.__organizer = organizer
        if sys.version_info < (3, 0):
            qCritical(self.__tr("TexureBA2Update plugin requires a Python 3 interpreter, but is running on a Python 2 interpreter."))
            QMessageBox.critical(self.__parentWidget, self.__tr("Incompatible Python version."),
            self.__tr("This version of the TextureBA2Update plugin requires a Python 3 interpreter, "
                    + "but Mod Organizer has provided a Python 2 interpreter. You should check for an updated version, "
                    + "including in the Mod Organizer 2 Development Discord Server."))
            return False
        return True

    def name(self):
        return PLUGIN_NAME

    def author(self):
        return "BAPper"

    def description(self):
        return self.__tr("Update textures from enabled mods into default BA2 files")

    def version(self):
        return mobase.VersionInfo(1, 0, 0, mobase.ReleaseType.final)

    def isActive(self):
        return True

    def settings(self):
        path = ""
        if (os.path.exists("%s/Archive2.exe" % CWD)):
            path = "%s/Archive2.exe" % CWD
        elif (os.path.exists("%s/Archive2.exe" % PLUGIN_DIR)):
            path = "%s/Archive2.exe" % PLUGIN_DIR
        return [
            mobase.PluginSetting("Archive2.exe-path", self.__tr("Path to Archive2.exe"), path),
            ]

    def displayName(self):
        return self.__tr(PLUGIN_NAME)

    def tooltip(self):
        return self.__tr("Update textures from enabled mods into default BA2 files")

    def icon(self):
        return QIcon()

    def setParentWidget(self, widget):
        self.__parentWidget = widget

    def display(self):
        dialog = WorkDialog(self.__parentWidget, self.__organizer)
        result = dialog.exec()

    def __tr(self, str):
        return QCoreApplication.translate(PLUGIN_NAME, str)

def createPlugin():
        return TextureBA2Update()

