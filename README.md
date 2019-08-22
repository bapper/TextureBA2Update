# TextureBA2Update
Fallout 4 Mod Organizer 2 plugin for updating base BA2 texture files with mod textures, big performance boost.

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
