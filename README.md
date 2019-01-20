# NVDA For Eclipse
This NVDA Add-on offers an enhanced support while working in the eclipse IDE.

## Add-On Features:

### Before you begin
Make sure that Java Access Bridge is working correctly. You can enable it in a control panel in the Eas of Access Center in Windows 10 - for example.
You can also go to the "bin" directory in the folder where Java is installed, and type the following command:
**jabswitch.exe -enable**
You have to do it for every Java environment your Eclipse installation may use for projects.

### Main Features:
* Automatically announce Eclipse's **ContentAssist** code completion items.
* Announce the **inserted item** without reading the entire line.
* Play different sounds while you use the Eclipse shortcut **CTRL+. (dot)** to identify whether an error or a warning is selected.
* Play different sounds when you press **CTRL+S** to indicate if the saved file contains errors / warnings.
* Announce the breakpoint toggle while pressing **CTRL+SHIFT+B**.
### After you start Eclipse
Eclipse is a rather complex software. It may take a while to update its internal caches or other components when it is launched.
The add-on is tracking the lines, and treats a currently edited line in a different way than when you move around editor up/down, or jump to a location, such as matching brace.
To make sure the add-on is working correctly switch to another window, for example: your desktop - WINDOWS+D will get you there, and bring focus back to Eclipse code editr.
When you start editing code, the add-on logic should work as expected.

### Additional Braille Features:
* Reports braille messages if you save a file that contains errors and / or warnings;
* Fixes an issues while you can't press the braille scroll back key to move on the previous line

### Additional Speech Features:
* Reports the current line while you move through using debugging keys
* Reports the current line while you press CTRL+. and the cursor moves.
* Reports the current line while you press CTRL+SHIFT+UP/DOWN ARROW and jump to previous / jump to next method
* Reports the current line while you press CTRL+SHIFT+P with a bracket selected: jump to the matching closing or opening bracket
* Moves you back and reports the last edit position CTRL+Q

## Eclipse Configuration
In order to take advantages of all the features of this addon, you have to configure Eclipse to highlight errors and warnings instead of underline them.
To do so, proceed as follow:
* Open the Eclipse IDE
* Open the Window Menu (ALT-W)
* Choose the "Preferences" item
* Tab to the tree view
* Navigate to General, then to Editors, Text Editors, Annotations
* Press TAB to move to the list of annotations

For each annotation you can choose:
* Three check boxes (Vertical ruler, Overview ruler and Text As)
* A combo box that indicates how the annotation is presented in the text (Available when the Text check box has been selected).

Set annotations as follow:

* **Breakpoints**: Text As Check Box selected, then TAB and choose "highlighted" from the combo box.
* **Errors**: Text As Check Box selected, then TAB and choose "highlighted" from the combo box.
* **Info**: Text As Check Box Unselected
* **Matching tags**: Text As Check Box Unselected
* **Occurrences**: Text As Check Box Unselected
* **Search Results**: Text As Check Box Unselected
* **Warnings**: Text As Check Box selected, then TAB and choose "highlighted" from the combo box.


## Sounds Copyrights
Sounds used to reports errors and warnings are covered by the Creative Commons License.
* [For the error sound please refer to this page](https://www.freesound.org/people/Autistic%20Lucario/sounds/142608/)
* [For the warning sound please refer to this page](https://www.freesound.org/people/ecfike/sounds/135125/)


## Authors:
* [Pawel Urbanski](https://www.pawelurbanski.com/) (Extended the original add-on)
* Alberto Zanella (The original plugin author)
* Iván Novegil C. 
* Alessandro Albano

