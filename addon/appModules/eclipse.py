# NVDA Addon that improves access to the Eclipse IDE
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Last update 2019-01-20 - Added Eclipse ContentAssist support.
# Based on the code by  Alberto Zanella and contributors
# Copyright (C) by Pawel Urbanski <pawel@pawelurbanski.com> https://www.pawelurbanski.com/

#from nvdaBuiltin.appModules import eclipse as base_eclipse
import appModuleHandler
import addonHandler
import eventHandler
import controlTypes
from comtypes import COMError
import nvwave
import tones
import api
import textInfos
import braille
import speech
from NVDAObjects.behaviors import EditableTextWithAutoSelectDetection as Edit
import globalCommands
import globalVars
import ui
import os.path

# The required call to add-on translation function
addonHandler.initTranslation()

# Addon constants
ADDON_NAME = "nvda-for-eclipse"
PLUGIN_DIR = os.path.abspath(os.path.join(globalVars.appArgs.configPath, "addons",ADDON_NAME))

# Global constants for Eclipse editor background colors
RGB_ERROR = 'rgb(2550128)'
RGB_WARN = 'rgb(24420045)'
RGB_BP = 'rgb(00255)'
RGB_DBG = 'rgb(198219174)'
# The main class implementing custom code editor

class EclipseTextArea(Edit):

	def event_gainFocus(self) :
		super(EclipseTextArea,self).event_gainFocus()
		tx = self.makeTextInfo(textInfos.POSITION_SELECTION)
		tx.collapse()
		tx.expand(textInfos.UNIT_LINE)

		self.processLine(tx)
# The caret movement / change possition loop
	def event_caret(self) :
		super(Edit, self).event_caret()
		if self is api.getFocusObject() and not eventHandler.isPendingEvents('gainFocus'):
			self.detectPossibleSelectionChange()
			tx = self.makeTextInfo(textInfos.POSITION_SELECTION)
			tx.collapse()
			tx.expand(textInfos.UNIT_LINE)

		# We check if the loop is not processing the same line.
		# Eclipse seems to fire events even if both start and end carets has not changed
		if self.appModule.PrevStartOffset == tx.bookmark.startOffset and self.appModule.PrevEndOffset == tx.bookmark.endOffset:
			return

		self.processLine(tx)

	# Implementation of the class function that processes line after change.
	# This is called after scroling up or dow
	def processLine(self,tx) :

		# Global variables to help control the loop and line processing
		self.appModule.PrevStartOffset == tx.bookmark.startOffset
		self.appModule.PrevEndOffset = tx.bookmark.endOffset

		# Get the textInfo object for a current line
		curr = self.makeTextInfo(textInfos.POSITION_SELECTION)
		curr.collapse()
		curr.expand(textInfos.UNIT_LINE)

		# Assign short variables for later conditions
		cs = curr.bookmark.startOffset # Current line startOffset
		ce = curr.bookmark.endOffset # Current line endOffset
		os = self.appModule.PrevStartOffset # startOffset from previous invocation
		oe = self.appModule.PrevEndOffset # endOffset from previous invocation

		# Expand line into individual characters with offsets from the caret event
		tx.collapse()
		tx.expand(textInfos.UNIT_CHARACTER)

		# Expand the current line to characters for checking background colors
		curr.collapse()
		curr.expand(textInfos.UNIT_CHARACTER)

		# If old and current startOffsets are different we moved to a new line
		# We additionally check the endOffsets changes
		if not os == cs or not oe == ce:

			# Process characters to check background colors.
			colors = self._hasBackground([RGB_BP,RGB_DBG],curr)
			if colors[RGB_BP] : 
				tones.beep(610,80)
			if colors[RGB_DBG] :
				tones.beep(310,160)

			# Update OldStartOffset variable to the current line's startOffset
			self.appModule.PrevStartOffset = curr.bookmark.startOffset
		elif os == cs:

			# We are in the same line, so read only suggested items.
			# Do not read the line from the beginning.
			# Read back what was inserted by the user
			line = self.makeTextInfo(textInfos.POSITION_SELECTION)
			line.collapse()
			line.expand(textInfos.UNIT_WORD)
			insertedItem = line.text
			speech.cancelSpeech()
			speech.speakText(insertedItem)

	def _caretScriptPostMovedHelper(self, speakUnit, gesture, info=None):

		if not info:
			try:
				info = self.makeTextInfo(textInfos.POSITION_CARET)
			except:
				return
		info.expand(textInfos.UNIT_CHARACTER)
		if (speakUnit == textInfos.UNIT_WORD) and (info.text == "\r\n") :
			super(EclipseTextArea,self)._caretScriptPostMovedHelper(textInfos.UNIT_CHARACTER, gesture, info)
		else :
			super(EclipseTextArea,self)._caretScriptPostMovedHelper(speakUnit, gesture, info)
	
	def script_breakpointToggle(self,gesture) :
		colors = self._hasBackground([RGB_BP])
		if(colors[RGB_BP]) : 
			ui.message(_("Breakpoint off"))
		else :
			ui.message(_("Breakpoint on"))
		gesture.send()
	
	def script_errorReport(self,gesture) :
		gesture.send()
		colors = self._hasBackground([RGB_ERROR,RGB_WARN])
		if(colors[RGB_ERROR]) : 
			braille.handler.message(_("\t\t error %% error"))
			self.appModule.play_error()
		elif(colors[RGB_WARN]) :
			braille.handler.message(_("\t\t warning %% warning"))
			self.appModule.play_warning()
		globalCommands.commands.script_reportCurrentLine(gesture)
	
	def script_checkAndSave(self,gesture) :
		gesture.send()
		colors = self._hasBackground([RGB_ERROR,RGB_WARN],ti=self.makeTextInfo(textInfos.POSITION_ALL))
		if colors[RGB_ERROR] : 
			braille.handler.message(_("\t\t saved with errors %% saved with errors"))
			self.appModule.play_error()
		elif colors[RGB_WARN] : 
			braille.handler.message(_("\t\t saved with warnings %% saved with warnings"))
			self.appModule.play_warning()
			
	def _hasBackground(self,colors,ti=None) :
		cfg = {
			"detectFormatAfterCursor":False,
			"reportFontName":False,"reportFontSize":False,"reportFontAttributes":False,"reportColor":True,"reportRevisions":False,
			"reportStyle":False,"reportAlignment":False,"reportSpellingErrors":False,
			"reportPage":False,"reportLineNumber":False,"reportTables":False,
			"reportLinks":False,"reportHeadings":False,"reportLists":False,
			"reportBlockQuotes":False,"reportComments":False,
		}
		retval = dict((color,False) for color in colors)
		if not ti :
			ti = self.makeTextInfo(textInfos.POSITION_SELECTION)
			ti.bookmark.endOffset = ti.bookmark.startOffset
			ti.collapse()
			ti.expand(textInfos.UNIT_CHARACTER)
		formatField=textInfos.FormatField()
		for field in ti.getTextWithFields(cfg):
			if isinstance(field,textInfos.FieldCommand) and isinstance(field.field,textInfos.FormatField):
				if field.field.has_key('background-color') :
					formatField.update(field.field)
					rgb = formatField['background-color']
					if rgb in retval :
						retval[rgb] = True
		return retval

	__gestures = {
		"kb:control+.": "errorReport",
		"kb:control+s": "checkAndSave",
		"KB:control+shift+b":"breakpointToggle",
		"kb:control+shift+downArrow": "caret_moveByLine",
		"kb:control+shift+upArrow": "caret_moveByLine",
		"kb:control+shift+p": "caret_moveByLine",
		"kb:f5": "caret_moveByLine",
		"kb:f6": "caret_moveByLine",
		"kb:f7": "caret_moveByLine",
		"kb:f8": "caret_moveByLine",
		"kb:control+q": "caret_moveByLine",
	}
	
	
class AppModule(appModuleHandler.AppModule):

	# A module variable to track previous line start offset position.
	PrevStartOffset = 0 # Initial value.
	# A module variable to track previous line end offset position.
	PrevEndOffset = 1 # Initial value>
	# Manually provide product name and version - not detected by NVDA
	productName = "Eclipse"
	productVersion = "Not Detected"

	# A function to find and click terminate buffer
	terminateButton = None
	
	def get_terminate_button(self) :
		if self.terminateButton != None : return
		obj = api.getFocusObject()
		while (obj.parent is not None) :
			if (obj.role == controlTypes.ROLE_TABCONTROL) and (obj.name == 'Console') :
				break
			obj = obj.parent
		if obj.name != "Console" : return
		while obj.role is not controlTypes.ROLE_TOOLBAR :
			obj = obj.firstChild
		for i in xrange(1,obj.childCount) :
			if obj.IAccessibleObject.accName(i) == "Terminate" : 
				self.terminateButton = obj.children[i-1]
				return
			
	
	def event_NVDAObject_init(self, obj):
		#super(AppModule, self).event_NVDAObject_init(obj)
		if obj.role == controlTypes.ROLE_DIALOG and "show Template Proposals" in obj.description :
			# Remove annoying tooltips
			obj.description = ""

		# Automatically speak current item in the ContentAssist pop-up.
		if obj.windowClassName == "SysListView32" and obj.role == controlTypes.ROLE_LISTITEM:
			speech.cancelSpeech()
			ui.message(obj.name)

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		super(AppModule, self).chooseNVDAObjectOverlayClasses(obj, clsList)
		if obj.windowClassName == "SWT_Window0" and obj.role == controlTypes.ROLE_EDITABLETEXT:
			clsList.insert(0, EclipseTextArea)


	def play_error(self) :
		wfile  = os.path.join(PLUGIN_DIR, "sounds", "error.wav")
		nvwave.playWaveFile(wfile)
	
	def play_warning(self) :
		wfile  = os.path.join(PLUGIN_DIR, "sounds", "warn.wav")
		nvwave.playWaveFile(wfile)
	
	def script_clickTerminateButton(self, gesture):
		self.get_terminate_button()
		if self.terminateButton != None :
			try :
				self.terminateButton.doAction()
				ui.message(_("Terminated"))
			except:
				pass
	

	def script_braille_scrollBack(self, gesture):
		try :
			globalCommands.commands.script_braille_scrollBack(gesture)
		except COMError :
			globalCommands.commands.script_braille_previousLine(gesture)
		
	__gestures = {
		"kb:nvda+shift+t": "clickTerminateButton",
	}
