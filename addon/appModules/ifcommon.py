﻿# -*- coding: utf-8 -*-
# A part of NonVisual Desktop Access (NVDA)
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2020 Nick Stockton <nstockton@gmail.com>
# Portions of This Work Copyright (C) 2006-2013 NV Access Limited

# Built-in Python modules
try:
	from cStringIO import StringIO
except ImportError:
	# Python3
	from io import StringIO
from decimal import Decimal
import difflib
import os.path
import time

# Built-in NVDA modules
import addonHandler
import api
import appModuleHandler
import config
from configobj import ConfigObj
from logHandler import log
from NVDAObjects.window import DisplayModelLiveText
import ui
import queueHandler
import textInfos
try:
	from validate import Validator
except ImportError:
	# NVDA >= 2019.3.0.
	from configobj.validate import Validator


ADDON_CONFIG = None
ADDON_CONFIG_SPEC = """
[general]
delay = float(default=0.1)
"""


def loadAddonConfig(fileName):
	global ADDON_CONFIG
	if ADDON_CONFIG is None:
		path = os.path.join(addonHandler.getCodeAddon().path, fileName)
		try:
			ADDON_CONFIG = ConfigObj(path, configspec=StringIO(ADDON_CONFIG_SPEC), default_encoding="utf-8", encoding="utf-8", stringify=True)
			ADDON_CONFIG.newlines = "\r\n"
			val = Validator()
			result = ADDON_CONFIG.validate(val, preserve_errors=True, copy=True)
			if not result:
				log.warning("Corrupted add-on configuration file: %s", result)
		except Exception:
			log.warning("Unable to load the add-on configuration file: %s", path)

def saveAddonConfig():
	global ADDON_CONFIG
	if ADDON_CONFIG is None:
		raise RuntimeError("Failed to load configuration file from the add-on folder.")
	val = Validator()
	result = ADDON_CONFIG.validate(val, preserve_errors=True, copy=True)
	if not result:
		log.warning("Corrupted add-on configuration in memory: %s", result)
		ADDON_CONFIG = None
	else:
		ADDON_CONFIG.write()


class GameDisplayModelLiveText(DisplayModelLiveText):
	prompts = [">"]
	informStyleHelp = False

	def gotoPrompt(self):
		"""Set the review cursor to the last line of text"""
		info = api.getReviewPosition().obj.makeTextInfo(textInfos.POSITION_LAST)
		api.setReviewPosition(info)

	def myGetTextLines(self, obj):
		outLines = []
		for line in obj.makeTextInfo(textInfos.POSITION_ALL).getTextInChunks(textInfos.UNIT_LINE):
			line = line.lstrip()
			if not line:
				continue
			if line.startswith(">") and line.rstrip() != ">":
				line = ">" + line[1:].lstrip()
			outLines.append(line)
		return outLines

	def _getTextLines(self):
		return (self.myGetTextLines(self), [])

	def getInformHelpItem(self, outLines, oldOutLines):
		lines = []
		for line in outLines:
			if line.strip() == ">":
				break
			elif line.startswith(">") and (not lines or not lines[0].startswith(">")):
				lines.insert(0, line)
			elif not line.startswith(">") and (not lines or lines[-1].startswith(">")):
				lines.append(line)
		if len(lines) == 2 and lines[0][1:] in oldOutLines and ">" + lines[1] in oldOutLines:
			outLines = [lines[0][1:]]
		return outLines

	def _monitor(self):
		try:
			oldMainLines, oldOtherLines = self._getTextLines()
		except:
			oldMainLines = []
			oldOtherLines = []
		while self._keepMonitoring:
			self._event.wait()
			if not self._keepMonitoring:
				break
			try:
				self.STABILIZE_DELAY = ADDON_CONFIG["general"]["delay"]
			except:
				self.STABILIZE_DELAY = 0
			if self.STABILIZE_DELAY > 0:
				# Wait for the text to stabilise.
				time.sleep(self.STABILIZE_DELAY)
				if not self._keepMonitoring:
					# Monitoring was stopped while waiting for the text to stabilise.
					break
			self._event.clear()
			try:
				newMainLines, newOtherLines = self._getTextLines()
				if config.conf["presentation"]["reportDynamicContentChanges"]:
					mainLines = []
					if newMainLines:
						mainLines = self._calculateNewText(newMainLines, oldMainLines)
						if len(mainLines) == 1 and not mainLines[0].strip() in self.prompts and (len(mainLines[0].strip()) == 1 or [prompt for prompt in self.prompts if mainLines[0].startswith(prompt)]):
							# This is only a single character,
							# which probably means it is just a typed character,
							# so ignore it.
							del mainLines[0]
						elif self.informStyleHelp and len(mainLines) == 2:
							mainLines = self.getInformHelpItem(mainLines, oldMainLines)
						oldMainLines = newMainLines
					otherLines = []
					if newOtherLines:
						otherLines = self._calculateNewText(newOtherLines, oldOtherLines)
						if self.informStyleHelp and len(otherLines) == 2:
							otherLines = self.getInformHelpItem(otherLines, oldOtherLines)
						oldOtherLines = newOtherLines
					outLines = []
					for line in mainLines+otherLines:
						if line.startswith(">"):
							line = "Grater " + line[1:]
						outLines.append(line)
					if outLines:
						queueHandler.queueFunction(queueHandler.eventQueue, self._reportNewText, " ".join(outLines))
			except:
				continue

	def _calculateNewText(self, newLines, oldLines):
		outLines = []
		prevLine = None
		for line in difflib.ndiff(oldLines, newLines):
			if line[0] == "?":
				# We're never interested in these.
				continue
			if line[0] != "+":
				# We're only interested in new lines.
				prevLine = line
				continue
			text = line[2:]
			if not text or text.isspace():
				prevLine = line
				continue
			if prevLine and prevLine[0] == "-" and len(prevLine) > 2:
				# It's possible that only a few characters have changed in this line.
				# If so, we want to speak just the changed section, rather than the entire line.
				prevText = prevLine[2:]
				textLen = len(text)
				prevTextLen = len(prevText)
				# Find the first character that differs between the two lines.
				for pos in range(min(textLen, prevTextLen)):
					if text[pos] != prevText[pos]:
						start = pos
						break
				else:
					# We haven't found a differing character so far and we've hit the end of one of the lines.
					# This means that the differing text starts here.
					start = pos + 1
				# Find the end of the differing text.
				if textLen != prevTextLen:
					# The lines are different lengths, so assume the rest of the line changed.
					end = textLen
				else:
					for pos in range(textLen - 1, start - 1, -1):
						if text[pos] != prevText[pos]:
							end = pos + 1
							break
				if end - start < 2:
					# Less than 2 characters have changed, so only speak the changed chunk.
					# Was originally 15
					text = text[start:end]
			if text and not text.isspace():
				outLines.append(text)
			prevLine = line
		return outLines


class GameAppModule(appModuleHandler.AppModule):
	scriptCategory = "ifInterpreters"
	def script_decrease_delay(self,gesture):
		global ADDON_CONFIG
		delay = Decimal(str(ADDON_CONFIG["general"]["delay"]))
		if delay <= Decimal(str(0.1)):
			delay = ADDON_CONFIG["general"]["delay"] = 0.0
		else:
			delay = ADDON_CONFIG["general"]["delay"] = float(delay - Decimal(str(0.1)))
		# Translators: Message reporting the delay to stabilize text.
		ui.message(_("Stabilize delay: %s.") % str(delay))
	# Translators: Message presented in input help mode.
	script_decrease_delay.__doc__=_("Decrease the Stabilize Delay for the game output.")

	def script_increase_delay(self,gesture):
		global ADDON_CONFIG
		delay = Decimal(str(ADDON_CONFIG["general"]["delay"]))
		if delay >= Decimal(str(0.9)):
			delay = ADDON_CONFIG["general"]["delay"] = 1.0
		else:
			delay = ADDON_CONFIG["general"]["delay"] = float(delay + Decimal(str(0.1)))
		# Translators: Message reporting the delay to stabilize text.
		ui.message(_("Stabilize delay: %s.") % str(delay))
	# Translators: Message presented in input help mode.
	script_increase_delay.__doc__=_("Increase the Stabilize Delay for the game output.")

	__gestures = {
		"kb:windows+NVDA+leftArrow": "decrease_delay",
		"kb:windows+NVDA+rightArrow": "increase_delay",
	}
