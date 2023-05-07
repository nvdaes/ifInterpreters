# IF Interpreters

* Author: Nick Stockton (maintained by Noelia Ruiz Martínez).

This add-on enables automatic speech output for interactive fiction interpreters.

## Supported Windows interpreters:

* [AdvSys]( http://ifarchive.org/if-archive/programming/advsys/advsys-winglk-20011221.zip) (GLK), for games in AdvSys format.
* [AGiliTy](http://davidkinder.co.uk/agility.html), for games in Adventure Game Toolkit format.
* [Frotz](http://davidkinder.co.uk/frotz.html), for games in Z-Code format.
* [Git and Glulxe](http://davidkinder.co.uk/glulxe.html) (GLK), for games in Glulxe format.
* [HTML Tads Player Kit](http://tads.org/t3dl/pksetup.exe), for games in Tads2 and Tads3 format.
* [Hugo](http://ifarchive.org/if-archive/programming/hugo/executables/hugov31_winglk.zip) (GLK), for games in Hugo format.
* [Level 9](http://davidkinder.co.uk/level9.html), for games in A-Code format.
* [Magnetic](http://davidkinder.co.uk/magnetic.html), for games in Magnetic Scrolls format.
* [Nitfol](http://ifarchive.org/if-archive/infocom/interpreters/nitfol/winnitfol-0_5.zip) (GLK), for games in Z-Code format.
* [Scare](http://ifarchive.org/if-archive/programming/adrift/scare-1.3.10_win.zip) (GLK), for games in Adrift format.
* [WinARun](http://ifarchive.org/if-archive/programming/alan/executables/arun287-5-glk-win32-ix86.zip) (GLK), for games in Alan format.
* [WinARun3](http://www.alanif.se/joomla/index.php/download-v3/windows-jdownloads/viewcategory/7) (GLK), for games in Alan 3 format.

If you have previously installed an Add-On for any of these programs, you will need to remove it before installing this Add-On.

## Some important information:

To configure Magnetic to work best with NVDA, bring up the 'Options' dialog with Control+T, tab to the 'Pictures' ComboBox and select 'None', then hit OK.

If you wish to play a Z-Code game with Windows Frotz, you must first launch Windows Frotz, then select the game you want to play from the file open dialog that appears.  If you try to play a game by opening a game file in Windows Explorer, the resulting instance of Windows Frotz will not be readable with NVDA.

If you find that NVDA is mixing old output lines from the interpreter with new lines, try adjusting the stabilize delay using Windows+NVDA+Left Arrow and Windows+NVDA+right Arrow.  If the interpreter is Windows Frotz, you should also insure the Fast Scrolling check box is checked in the Windows Frotz preferences dialog.  You can bring up the dialog with Control+P from within the program.
