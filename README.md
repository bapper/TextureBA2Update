# TextureBA2Update
Fallout 4 Mod Organizer 2 plugin for updating base BA2 texture files with mod textures, big performance boost.

## Install
Here is how I use this:
* Grab the source for this plugin and copy it to your MO2-install/plugins folder
* Install Creation Kit, google on how to do this if you haven't already. Or, you can copy
  Archive2.exe file and Archive2Interop.dll files from some other location to your MO2 install
  directory. This is also a setting you can set in the MO2 plugins settings dialog tab.

## Usage
* Start MO2, starting before the python files are in the plugins directory will
  cause the plugin to not show up
* create a new MO2 profile that is a copy of your main profile
* Switch to the new profile
* Disable all mods that are not texture update mods, this is easy if you use MO2
  separators, just uncheck all modules not under your texture update separator.
* Pull down the plugins menu (labeled "tools" and looks like puzzle pieces) and
  select the TextureBA2Update tool
* When the dialog window pops up, all you need to do is click the "Update BA2s"
  button and wait for a long time for the work to finish.

If you've already used this before and update your texture files, before
clicking on the "Update BA2s" button, click on the "Enable Textures" button.
This will rename all of the "DISABLED" textures to the original files allowing
their use again during the update process.

## What is does
This is a simple python based plugin that will perform these tasks:

* Back up the base texture BA2 files from the game directory (if they aren't
  already backed up:
  * Fallout4 - Textures1.ba2
  * Fallout4 - Textures2.ba2
  * Fallout4 - Textures3.ba2
  * Fallout4 - Textures4.ba2
  * Fallout4 - Textures5.ba2
  * Fallout4 - Textures6.ba2
  * Fallout4 - Textures7.ba2
  * Fallout4 - Textures8.ba2
  * Fallout4 - Textures9.ba2
  * DLCworkshop01 - Textures.ba2
  * DLCworkshop03 - Textures.ba2
  * DLCNukaWorld - Textures.ba2
  * DLCCoast - Textures.ba2
  * DLCworkshop02 - Textures.ba2
  * DLCRobot - Textures.ba2
* Starting with the last BA2, the one that takes precedence, unpack it to
  a working directory (MO2 install directory/TextureWorkDir)
  * From the last enabled module, compare texture files with that of the
    TextureWorkDir, if the mod has a texture with the same path, copy it to the
    work directory overwriting the one that came from the game BA2 file then
    disable the texture in the module by renaming it with a DISABLED suffix.
  * Repeat this with the remaining plugins, but don't copy the texture, just
    disable it if found in the original BA2. Only the last mod in order should
    overwrite the texture but it still needs to be disabled to prevent it from
    being used instead of the new BA2 update.
  * Create a new BA2 archive file from the updated TextureWorkDir with the same
    name as the BA2 file from the game currently being work on.
  * Clean up the working directory.
* Repeat the last process through the rest of the BA2 texture files, the end
  result will be updated BA2 files in the BA2WorkDir.
* Move the new BA2 files the game data directory

At the end, all of the textures in the enabled mods that have corresponding
texures in the base game files will be replaced with updated BA2 files using
textures from you mod files. BA2 texture archives that are created with the -dds
parameter are much more effiecient for the game engine to use than loose files
so this process can really give us a big boost in performance.

## Files
* TextureBA2MainDialog.ui - This is the user interface file created in
  QtDesigner.
* TextureBA2MainDialog.py - The .ui file is fed through pyuic5 to produce this
  file, it isn't modified by hand, all changes are made in the .ui file.
* TextureBA2Update.py - This is the main plugin logic file. The use of threads
  and asynchronous processes is used to keep the main Qt thread free to update
  the UI.
