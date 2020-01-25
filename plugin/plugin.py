# Edit By RAED to OE2.5 images 10-03-2019
# Edit By RAED Add IRDETO & PowerVU 14-03-2019
# Edit By RAED Fix PowerVU 18-03-2019
# Edit By RAED Edit keyboard 19-03-2019
# Edit By mfaraj57 & RAED Fix tandberg 02-04-2019
# Edit By RAED Fix keyboard 22-05-2019
# Edit By RAED Fix keyboard Add Version number 27-05-2019
# Edit By RAED to openvision image 07-07-2019
# Edit By RAED & mfaraj57 change plugin name to AddKey 12-07-2019
# Edit By RAED Add more site to download softcam files 28-07-2019

from enigma import eConsoleAppContainer, eDVBDB, iServiceInformation, eTimer, loadPNG, getDesktop, RT_WRAP, RT_HALIGN_LEFT, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.config import config,  ConfigText, ConfigSubsection
from Plugins.Plugin import PluginDescriptor
from Tools.BoundFunction import boundFunction
from ServiceReference import ServiceReference
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Console import Console
from Components.ActionMap import ActionMap
from urllib2 import Request
from array import array
from string import hexdigits
from datetime import datetime
from Components.MenuList import MenuList
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
import binascii
import os
from VirtualKeyBoard import VirtualKeyBoard

Ver = "2.5"
reswidth = getDesktop(0).size().width()
resheight = getDesktop(0).size().height()
config.plugins.KeyAdder = ConfigSubsection()
config.plugins.KeyAdder.lastcaid = ConfigText(default='0', fixed_size=False)

def debug(label,data):
    data=str(data)
    open("/tmp/addkey.log","w").write("\n"+label+":>"+data)

def getnewcaid(SoftCamKey):
   ##T 0001
   import os
   caidnumbers=[]
   newkey=1
   if os.path.exists(SoftCamKey):
      try:
          lines=open(SoftCamKey).readlines()
          for line in lines:
              line=line.strip()
              if line.startswith('T'):
                caidnumber=line[2:6]
                try:
                        caidnumbers.append(int(caidnumber))
                except:
                        continue
      except:
          caidnumbers=[]
      try:
              newcaid=max(caidnumbers)+1
      except:
              newcaid=1
      formatter="{:04}"
      newcaid=formatter.format(newcaid)
      saved_caid=int(config.plugins.KeyAdder.lastcaid.value)+1
      if saved_caid>newcaid:
          newcaid=saved_caid
      elif newcaid>saved_caid :                                                    
         config.plugins.KeyAdder.lastcaid.value=newcaid
         config.plugins.KeyAdder.lastcaid.save()
      elif  newcaid==9999:
          config.plugins.KeyAdder.lastcaid.value="1111"
          config.plugins.KeyAdder.lastcaid.save()
          newcaid=="1111"
      return newcaid 

def findSoftCamKey():
	paths = ["/etc/tuxbox/config/oscam-emu", "/etc/tuxbox/config/oscam-trunk", "/etc/tuxbox/config/oscam", "/etc/tuxbox/config/ncam", "/etc/tuxbox/config/gcam", "/etc/tuxbox/config", "/etc", "/var/keys", "/usr/keys"]
	if os.path.exists("/tmp/.oscam/oscam.version"):
		data = open("/tmp/.oscam/oscam.version", "r").readlines()
	if os.path.exists("/tmp/.ncam/ncam.version"):
		data = open("/tmp/.ncam/ncam.version", "r").readlines()
	if os.path.exists("/tmp/.gcam/gcam.version"):
		data = open("/tmp/.gcam/gcam.version", "r").readlines()
		for line in data:
			if "configdir:" in line.lower():
				paths.insert(0, line.split(":")[1].strip())
	for path in paths:
		softcamkey = os.path.join(path, "SoftCam.Key")
		print "[key] the %s exists %d" % (softcamkey, os.path.exists(softcamkey))
		if os.path.exists(softcamkey):
			return softcamkey
	return "/usr/keys/SoftCam.Key"

class AddKeyUpdate(Screen):
    if reswidth == 1920:
           skin = '''
                <screen name="AddKeyUpdate" position="center,center" size="650,300" backgroundColor="#16000000" transparent="0" title="KeyAdder" >
                       <widget name="menu" position="30,30" size="650,300" backgroundColor="#16000000" transparent = "0" />
                </screen>'''
    else:
           skin = '''
                <screen name="AddKeyUpdate" position="center,center" size="450,180" backgroundColor="#16000000" transparent="0" title="KeyAdder" >
                       <widget name="menu" position="20,20" size="450,180" backgroundColor="#16000000" transparent = "0" />
                </screen>'''

    def __init__(self, session, title='', datalist = []):
        Screen.__init__(self, session)
        self['menu'] = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self['actions'] = ActionMap(['ColorActions', 'WizardActions'], {'back': self.close,
         'ok': self.select,
         'back': self.close}, -1)
        title = "KeyAdder Version %s" % Ver
        menuData = []
        menuData.append((0, 'Add key Manually', 'key'))
        menuData.append((1, 'Update Softcam online', 'update'))
        menuData.append((2, 'Exit', 'exit'))
        self.settitle(title, menuData)

    def settitle(self, title, datalist):
        self.setTitle(title)
        self.showmenulist(datalist)

    def select(self):
        index = self['menu'].getSelectionIndex()
        if index==0:
                keymenu(self.session)
        elif index==1:
                self.siteselect()
        else:
            self.close()

    def siteselect(self):
        list1 = []
        list1.append(("softcam.org", "softcam.org"))
        list1.append(("Serjoga softcam", "Serjoga softcam"))
        list1.append(("enigma1969 softcam", "enigma1969 softcam"))
        from Screens.ChoiceBox import ChoiceBox
        self.session.openWithCallback(self.Downloadkeys, ChoiceBox, _('select site to downloan file'), list1)
           
    def Downloadkeys(self, select, SoftCamKey=None):
        self.list = []
        cmdlist = []
        SoftCamKey = findSoftCamKey()
        from downloader import imagedownloadScreen
        agent='--header="User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/8.0 Safari/600.1.17"'
        crt="--debug --no-check-certificate"
        command=''
        if select: 
            if select[1] == "softcam.org":
                myurl = 'http://www.softcam.org/deneme6.php?file=SoftCam.Key'
                command = 'wget -O %s %s' % (SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,'softcam',SoftCamKey, myurl)
            elif select[1] == "Serjoga softcam":
                myurl = 'https://raw.githubusercontent.com/audi06/SoftCam.Key_Serjoga/master/SoftCam.Key'
                command = 'wget -q %s %s %s %s' % (crt, agent, SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,'softcam',SoftCamKey,myurl)
            elif select[1] == "enigma1969 softcam":
                myurl = 'https://drive.google.com/uc?authuser=0&id=1aujij43w7qAyPHhfBLAN9sE-BZp8_AwI&export=download'
                command = 'wget -O %s %s' % (SoftCamKey, myurl)
                self.session.open(imagedownloadScreen,'softcam',SoftCamKey,myurl)
            else:
                self.close()
            debug("command",command)
            self.close()
      
    def showmenulist(self, datalist):
        cacolor = 16776960
        cbcolor = 16753920
        cccolor = 15657130
        cdcolor = 16711680
        cecolor = 16729344
        cfcolor = 65407
        cgcolor = 11403055
        chcolor = 13047173
        cicolor = 13789470
        scolor = cbcolor
        res = []
        menulist = []
        if reswidth == 1280:
            self['menu'].l.setItemHeight(50)
            self['menu'].l.setFont(0, gFont('Regular', 28))
        else:
            self['menu'].l.setItemHeight(75)
            self['menu'].l.setFont(0, gFont('Regular', 42))
        for i in range(0, len(datalist)):
            txt = datalist[i][1]
            if reswidth == 1280:
                  png = os.path.join(resolveFilename(SCOPE_PLUGINS, 'Extensions/KeyAdder/VirtualKeyBoard_Icons/buttonsHD/%s.png' % datalist[i][2]))
            else:
                  png = os.path.join(resolveFilename(SCOPE_PLUGINS, 'Extensions/KeyAdder/VirtualKeyBoard_Icons/buttonsFHD/%s.png' % datalist[i][2]))
            res.append(MultiContentEntryText(pos=(0, 1), size=(0, 0), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text='', color=scolor, color_sel=cccolor, border_width=3, border_color=806544))
            if reswidth == 1280:
                res.append(MultiContentEntryText(pos=(60, 1), size=(723, 50), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text=str(txt), color=16777215, color_sel=16777215))
                res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(40, 40), png=loadPNG(png)))
            else:
                res.append(MultiContentEntryText(pos=(100, 1), size=(1080, 75), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text=str(txt), color=16777215, color_sel=16777215))
                res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(75, 75), png=loadPNG(png)))
            menulist.append(res)
            res = []
        self['menu'].l.setList(menulist)
        self['menu'].show()

class HexKeyBoard(VirtualKeyBoard):
	def __init__(self, session, title="", **kwargs):
		VirtualKeyBoard.__init__(self, session, title, **kwargs)
		self.skinName = "VirtualKeyBoard"
		self.keys_list = [[[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
					[u"OK", u"A", u"B", u"C", u"D", u"E", u"F", u"OK", u"LEFT", u"RIGHT", u"ALL", u"CLEAR"]]]
		self.locales = { "hex" : [_("HEX"), _("HEX"), self.keys_list] }
		self.lang = "hex"
		try:
		     self.setLocale()
		except:
                     self.max_key = all
		     self.setLang()
		self.buildVirtualKeyBoard()

	def setLang(self):
                self.keys_list = [[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
					[u"OK", u"A", u"B", u"C", u"D", u"E", u"F", u"OK", u"LEFT", u"RIGHT", u"ALL", u"CLEAR"]]

table = array('L')
for byte in range(256):
	crc = 0
	for bit in range(8):
		if (byte ^ crc) & 1:
			crc = (crc >> 1) ^ 0xEDB88320
		else:
			crc >>= 1
		byte >>= 1
	table.append(crc)

def crc32(string):
	value = 0x2600 ^ 0xffffffffL
	for ch in string:
		value = table[(ord(ch) ^ value) & 0xff] ^ (value >> 8)
	return value ^ 0xffffffffL

def crc323(string):
	value = 0xe00 ^ 0xffffffffL
	for ch in string:
		value = table[(ord(ch) ^ value) & 0xff] ^ (value >> 8)
	return value ^ 0xffffffffL

def hasCAID(session):
	service = session.nav.getCurrentService()
	info = service and service.info()
	caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
	if caids and 0xe00 in caids: return True
	if caids and 0x2600 in caids: return True
	if caids and 0x604 in caids: return True
	if caids and 0x1010 in caids: return True
	try:
		return eDVBDB.getInstance().hasCAID(ref, 0xe00)	# PowerVU
	except:
		pass
	try:
		return eDVBDB.getInstance().hasCAID(ref, 0x2600) # BISS	
	except:
		pass
	try:
		return eDVBDB.getInstance().hasCAID(ref, 0x604) # IRDETO
	except:
		pass
	try:
		return eDVBDB.getInstance().hasCAID(ref, 0x1010) # Tandberg
	except:
		pass
	return False

def getCAIDS(session):
	service = session.nav.getCurrentService()
	info = service and service.info()
	caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
	caidstr = "None"
	if caids: caidstr = " ".join(["%04X (%d)" % (x,x) for x in sorted(caids)])
	return caidstr

def keymenu(session, service=None):
	service = session.nav.getCurrentService()
	info = service and service.info()
	caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
	SoftCamKey = findSoftCamKey()
	ref = session.nav.getCurrentlyPlayingServiceReference()
	if not os.path.exists(SoftCamKey):
		session.open(MessageBox, _("Emu misses SoftCam.Key (%s)" % SoftCamKey), MessageBox.TYPE_ERROR)
	elif not hasCAID(session):
		session.open(MessageBox, _("CAID is missing for service (%s) CAIDS: %s" % (ref.toString(), getCAIDS(session))), MessageBox.TYPE_ERROR)
	else:
	     if caids and 0xe00 in caids:
		   session.openWithCallback(boundFunction(setKeyCallback, session, SoftCamKey), HexKeyBoard,
			title=_("Please enter new key:"), text=findKeyPowerVU(session, SoftCamKey))
	     elif caids and 0x2600 in caids:
		   session.openWithCallback(boundFunction(setKeyCallback, session, SoftCamKey), HexKeyBoard,
			title=_("Please enter new key:"), text=findKeyBISS(session, SoftCamKey))
	     elif caids and 0x604 in caids:
		   session.openWithCallback(boundFunction(setKeyCallback, session, SoftCamKey), HexKeyBoard,
			title=_("Please enter new key:"), text=findKeyIRDETO(session, SoftCamKey))
	     elif caids and 0x1010 in caids:
                   newcaid=getnewcaid(SoftCamKey)
		   session.openWithCallback(boundFunction(setKeyCallback, session, SoftCamKey), HexKeyBoard,
			title=_("Please enter new key for caid:"+newcaid), text=findKeyTandberg(session, SoftCamKey))

def setKeyCallback(session, SoftCamKey, key):
        global newcaid
	service = session.nav.getCurrentService()
	info = service and service.info()
	caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
	SoftCamKey = findSoftCamKey()
	ref = session.nav.getCurrentlyPlayingServiceReference()
	if key: key = "".join(c for c in key if c in hexdigits).upper()
	if key and len(key) == 14:
		if key != findKeyPowerVU(session, SoftCamKey, ""): # no change was made ## PowerVU
			keystr = "P %s 00 %s" % (getonidsid(session), key)
			name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
			datastr = "\n%s ; Added on %s for %s at %s\n" % (keystr, datetime.now(), name, getOrb(session))
			restartmess = "\n*** Need to Restart emu TO Active new key ***\n"
			open(SoftCamKey, "a").write(datastr)
			eConsoleAppContainer().execute("/etc/init.d/softcam restart")
			session.open(MessageBox, _("PowerVU key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
	elif key and len(key) == 16:
             if 0x2600 in caids:
		if key != findKeyBISS(session, SoftCamKey, ""): # no change was made ## BISS
			keystr = "F %08X 00 %s" % (getHash(session), key)
			name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
			datastr = "\n%s ; Added on %s for %s at %s\n" % (keystr, datetime.now(), name, getOrb(session))
			restartmess = "\n*** Need to Restart emu TO Active new key ***\n"
			open(SoftCamKey, "a").write(datastr)
			eConsoleAppContainer().execute("/etc/init.d/softcam restart")
			session.open(MessageBox, _("BISS key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
             else:
		if key != findKeyTandberg(session, SoftCamKey, ""): # no change was made ## Tandberg
                        newcaid=getnewcaid(SoftCamKey)
                        keystr = "T %s 01 %s" % (newcaid, key) 
			name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
			datastr = "\n%s ; Added on %s for %s at %s\n" % (keystr, datetime.now(), name, getOrb(session))
			restartmess = "\n*** Need to Restart emu TO Active new key ***\n"		
			open(SoftCamKey, "a").write(datastr)
			eConsoleAppContainer().execute("/etc/init.d/softcam restart")
			session.open(MessageBox, _("Tandberg key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
	elif key and len(key) == 32:
		if key != findKeyIRDETO(session, SoftCamKey, ""): # no change was made ## IRDETO
			keystr = "I 0604 M1 %s" % key
			name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
			datastr = "\n%s ; Added on %s for %s at %s\n" % (keystr, datetime.now(), name, getOrb(session))
			restartmess = "\n*** Need to Restart emu TO Active new key ***\n"
			open(SoftCamKey, "a").write(datastr)
			eConsoleAppContainer().execute("/etc/init.d/softcam restart")
			session.open(MessageBox, _("Irdeto key saved sucessfuly!%s %s" % (datastr, restartmess)), MessageBox.TYPE_INFO, timeout=10)
	elif key:
		   session.openWithCallback(boundFunction(setKeyCallback, session,SoftCamKey), HexKeyBoard,
			title=_("Invalid key, length is %d" % len(key)), text=key.ljust(16,'*'))
			#title=_("Invalid key, length is %d expecting 16." % len(key)), text=key.ljust(16,'*'))

def getHash(session):
	ref = session.nav.getCurrentlyPlayingServiceReference()
	sid = ref.getUnsignedData(1)
	tsid = ref.getUnsignedData(2)
	onid = ref.getUnsignedData(3)
	namespace = ref.getUnsignedData(4) | 0xA0000000

	# check if we have stripped or full namespace
	if namespace & 0xFFFF == 0:
		# Namespace without frequency - Calculate hash with srvid, tsid, onid and namespace
		data = "%04X%04X%04X%08X" % (sid, tsid, onid, namespace)
	else:
		# Full namespace - Calculate hash with srvid and namespace only
		data = "%04X%08X" % (sid, namespace)
	return crc32(binascii.unhexlify(data))

def getonidsid(session):
	ref = session.nav.getCurrentlyPlayingServiceReference()
	sid = ref.getUnsignedData(1)
	onid = ref.getUnsignedData(3)
	return "%04X%04X" % (onid, sid)

def getOrb(session):
	ref = session.nav.getCurrentlyPlayingServiceReference()
	orbpos = ref.getUnsignedData(4) >> 16
	if orbpos == 0xFFFF:
		desc = "C"
	elif orbpos == 0xEEEE:
		desc = "T"
	else:
		if orbpos > 1800: # west
			orbpos = 3600 - orbpos
			h = "W"
		else:
			h = "E"
		desc = ("%d.%d%s") % (orbpos / 10, orbpos % 10, h)
	return desc

def findKeyPowerVU(session, SoftCamKey, key="00000000000000"):
	keystart = "P %s" % getonidsid(session)
	keyline = ""
	with open(SoftCamKey, 'rU') as f:
		for line in f:
			if line.startswith(keystart):
				keyline = line
	if keyline:
		return keyline.split()[3]
	else:
		return key

def findKeyBISS(session, SoftCamKey, key="0000000000000000"):
	keystart = "F %08X" % getHash(session)
	keyline = ""
	with open(SoftCamKey, 'rU') as f:
		for line in f:
			if line.startswith(keystart):
				keyline = line
	if keyline:
		return keyline.split()[3]
	else:
		return key

def findKeyTandberg(session, SoftCamKey, key="0000000000000000"):
	keystart = "T 0001"
	keyline = ""
	with open(SoftCamKey, 'rU') as f:
		for line in f:
			if line.startswith(keystart):
				keyline = line
	if keyline:
		return keyline.split()[3]
	else:
		return key

def findKeyIRDETO(session, SoftCamKey, key="00000000000000000000000000000000"):
	keystart = "I 0604"
	keyline = ""
	with open(SoftCamKey, 'rU') as f:
		for line in f:
			if line.startswith(keystart):
				keyline = line
	if keyline:
		return keyline.split()[3]
	else:
		return key

def main(session, **kwargs):
    session.open(AddKeyUpdate)

def Plugins(**kwargs):
	return [PluginDescriptor(name = "Key Adder" , description = "Add BISS, PowerVU, Irdeto and Tandberg keys to current service", icon="plugin.png",
		where = [PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU],
		fnc = main, needsRestart = False)]

