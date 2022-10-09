from enum import Enum
from tkinter import *
import tkinter.font as tkfont
from PIL import ImageTk, Image, ImageDraw, ImageChops, ImageFilter
import time
from generate import *
from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio
import functools
import concurrent.futures
import os
from base64 import *
from tkinter.filedialog import *
import pygame
# import inspect
import wavfile
# import pprint
# import palanteer
import copy
import numpy as np
from scipy.spatial.transform import Rotation as R
import sys
import traceback
from math import pi

class OS(Enum):
    XP = "xp"
    UBUNTU = "ubuntu"
    WINDOWS_95 = "95"
    MAC = "macwindow"
    MAC_WINDOW_ID = "macwindoid"
    WINDOWS_7 = "7"
    CUSTOM = "custom"

globalcache = {}
framecache = {}
keyframecache = {}
filledframes = {}
openedimages = {}
generated = {os_type: {} for os_type in OS}
emptyimg = Image.new("RGBA", (100, 100), (255, 0, 255))


def win7bezierapprox(x):
    return 1.08334 * x ** 0.817775 - 0.0822632 * x ** 1.48583


def win7bezierapproxclose(x):
    return 0.922396 * x ** 1.234158 + 0.0768603 * x ** 11.3377


def linear(x):
    return x


def cubiceaseout(x):
    return 1 - (1 - x) ** 3


def smooth(x):
    return 3 * x ** 2 - 2 * x ** 3


def easeout(x):
    return -x * (x - 2)


def openimage(s):
    if s in openedimages:
        return openedimages[s]
    openedimages[s] = Image.open(s)
    return openedimages[s]


def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])

    A = np.matrix(matrix, dtype=np.float)
    B = np.array(pb).reshape(8)

    res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
    return np.array(res).reshape(8)


def rotate(vec, angles):
    angle = np.array(angles / 180 * pi)
    # print(angles)
    rot = R.from_rotvec(angle)
    # print(vec)
    return rot.apply(vec)


def translaterotateproject(width, height, position, rotation, origin, corner, perspective=250):
    vec = np.array((width * corner[0] - (width * origin[0]) / 2, height * corner[1] - (height * origin[1]) / 2, 0))
    rotated = rotate(vec, rotation)
    z = 1 + rotated[2] / perspective + position[2]
    projected = [(rotated[0] - width * (0.5 - origin[0] / 2)) / z + width / 2 + position[0], (rotated[1] - height * (0.5 - origin[1] / 2)) / z + height / 2 + position[1]]
    return projected


def CreateCustomWindowAnimation(image, time=1, startpos=(0, 0, 0), startrotation=(0, 0, 0), origin=(0.5, 0.5, 0)):
    # print("theimage,",image)
    t = min(1, max(0, time))
    startrotation = np.array(startrotation)
    startpos = np.array(startpos)
    NW = translaterotateproject(w(image), h(image), startpos * (1 - t), startrotation * (1 - t), origin, (0, 0, 0))
    NE = translaterotateproject(w(image), h(image), startpos * (1 - t), startrotation * (1 - t), origin, (1, 0, 0))
    SW = translaterotateproject(w(image), h(image), startpos * (1 - t), startrotation * (1 - t), origin, (0, 1, 0))
    SE = translaterotateproject(w(image), h(image), startpos * (1 - t), startrotation * (1 - t), origin, (1, 1, 0))
    coeffs = find_coeffs([NW, NE, SE, SW], [[0, 0], [w(image), 0], [w(image), h(image)], [0, h(image)]])
    return coeffs


def ExecuteCustomWindowAnimation(image, coeffs, time, wallpaper=None, pos=None, align=None):
    t = min(1, max(0, time))
    image = image.transform(image.size, Image.PERSPECTIVE, coeffs, Image.LINEAR);
    no = image.copy()
    no.putalpha(0)
    image = ImageChops.blend(no, image, t)
    if wallpaper:
        image = put(wallpaper.copy(), image.copy(), pos[0], pos[1], align)
    return image


def Composite7(img, GlassMask, time, startpos, startrotation, origin, wallpaper, pos, align):
    wallpaper = wallpaper.copy()
    GlassImg = openimage("7/Glass.png")
    WithBorder = put(Image.new("RGBA", (800, 602), (0, 0, 0, 0)), GlassImg.resize(wallpaper.size, 0), int(-pos[0] + w(img) / 16 - wallpaper.size[0] / 16 + pos[0] / 8), -pos[1])
    GlassMask = put(Image.new("RGBA", img.size, (255, 255, 255, 0)), GlassMask, 14, 14)
    WithBorder = ImageChops.multiply(WithBorder, GlassMask)
    IMAGE = put(WithBorder, img, 0, 0)
    coeffs = CreateCustomWindowAnimation(IMAGE, time, startpos, startrotation, origin)
    IMAGE = ExecuteCustomWindowAnimation(IMAGE, coeffs, time)
    GlassMask = ExecuteCustomWindowAnimation(GlassMask, coeffs, time)
    Blur = wallpaper.filter(ImageFilter.GaussianBlur(radius=12))
    masked = ImageChops.multiply(put(Image.new("RGBA", wallpaper.size, (0, 0, 0, 0)), GlassMask, pos[0] - 14, pos[1] - 14, align), Blur)
    masked = put(masked, IMAGE, pos[0] - 14, pos[1] - 14, align)
    wallpaper.alpha_composite(masked)
    return wallpaper


composites = {
    "xp": (lambda img, mask, time, startpos, startrotation, origin, wallpaper, pos, align: ExecuteCustomWindowAnimation(
        img, CreateCustomWindowAnimation(img, time, startpos, startrotation, origin), time, wallpaper, pos, align
        )),
    OS.WINDOWS_7: (lambda img, mask, time, startpos, startrotation, origin, wallpaper, pos, align: Composite7(img, mask, time, startpos, startrotation, origin, wallpaper, pos, align)),
    "custom": (lambda img, mask, time, startpos, startrotation, origin, wallpaper, pos, align: ExecuteCustomWindowAnimation(
        img, CreateCustomWindowAnimation(img, time, startpos, startrotation, origin), time, wallpaper, pos, align
        ))
}


def CompositeWindow(img, mask, os, time, startpos, startrotation, origin, wallpaper, pos, align, close, closetime, endpos, endrotation, endorigin, closetimingfunction, timingfunction):
    global composites
    if close:
        time = 1 - closetimingfunction(closetime)
        return composites[os](img, mask, time, endpos, endrotation, endorigin, wallpaper, pos, align)
    else:
        time = timingfunction(time)
        return composites[os](img, mask, time, startpos, startrotation, origin, wallpaper, pos, align)


class Window():
    def __getimage(self, composite=False, pos=(0, 0), time=1, align="", close=False, generated=None):
        mask = None
        if generated is None:
            if self.os == OS.XP:
                new = CreateXPWindow(
                    0, 0,
                    captiontext=self.title,
                    active=self.active,
                    erroriconpath=self.icons[OS.XP][self.icon],
                    errortext=self.text,
                    button1=self.buttons[0],
                    button2=self.buttons[1],
                    button3=self.buttons[2],
                    button1style=self.buttonstyles[0],
                    button2style=self.buttonstyles[1],
                    button3style=self.buttonstyles[2]
                    )
            elif self.os == OS.MAC_WINDOW_ID:
                new = CreateMacWindoid(icon=self.icons[OS.MAC_WINDOW_ID][self.icon], text=self.text, collapsed=self.collapsed)
            elif self.os == OS.UBUNTU:
                new = CreateUbuntuWindow(icon=self.icons[OS.UBUNTU][self.icon], bigtext=self.text, text=self.subtext, title=self.title, buttons=self.buttons, active=self.active)
            elif self.os == OS.WINDOWS_95:
                new = Create95Window(icon=self.icons[OS.WINDOWS_95][self.icon], text=self.text, title=self.title, buttons=self.buttons, active=self.active, closebutton=self.closebutton)
            elif self.os == OS.MAC:
                new = CreateMacWindow(
                    0, 0,
                    title=self.title,
                    icon=self.icons[OS.MAC][self.icon],
                    errortext=self.text,
                    button1=self.buttons[0],
                    button2=self.buttons[1],
                    button3=self.buttons[2],
                    button1style=self.buttonstyles[0],
                    button2style=self.buttonstyles[1],
                    button3style=self.buttonstyles[2],
                    button1default=self.buttondefaults[0],
                    button2default=self.buttondefaults[1],
                    button3default=self.buttondefaults[2]
                    )
            elif self.os == OS.WINDOWS_7:
                temp = []
                for i in range(len(self.buttons)):
                    if self.buttons[i] != "":
                        temp.append([self.buttons[i], self.buttonstyles[i]])
                new, mask = Create7Window(icon=self.icons[OS.WINDOWS_7][self.icon], text=self.text, title=self.title, buttons=temp, active=self.active)
            elif self.os == OS.CUSTOM:
                new = self.img
        else:
            new = generated[0].copy()
            mask = generated[1].copy()
            # print("Animate",self.animate)
        # print("new",new)
        if mask is None:
            mask = new.split()[-1]
        # print("timingfucntion:")
        # print(self.closetimingfunction)
        if composite:
            new = CompositeWindow(
                new, mask, self.os, time=min(1, max(0, (time + 0.016666666) / max(0.01, self.animationlength))), startpos=self.startpos, startrotation=self.startrotation, origin=self.origin,
                wallpaper=composite, pos=pos, align=align, close=close, closetime=min(1, max(0, (time + 0.01666666) / max(0.01, self.animationcloselength))), endpos=self.endpos,
                endrotation=self.endrotation, endorigin=self.endorigin, closetimingfunction=self.closetimingfunction, timingfunction=self.timingfunction
                )
        # new = CreateCustomWindowAnimation(new,time/self.animationlength,self.startpos,self.startrotation,self.origin,wallpaper=composite,pos=pos,align=align,close=close)
        return new, mask

    def __init__(
            self, os: OS = OS.XP, text="", subtext="", icon=0, title="", buttons=["", "", ""], buttonstyles=[0, 0, 0], buttondefaults=[False, False, False], bar=True, closebutton=True, active=True,
            collapsed=False, img="", startpos=(0, 0, 0), animate=True, startrotation=(0, 0, 0), animationlength=0.016666666, origin=(0, 0, 0), animationcloselength=0.0166666666,
            timingfunction=win7bezierapprox, endpos=(0, 0, 0), endrotation=(0, 0, 0), endorigin=(0, 0, 0), closetimingfunction=win7bezierapproxclose
            ):
        global emptyimg
        self.os = os
        self.active = active
        self.text = text
        self.subtext = subtext
        self.title = title
        self.icon = icon
        self.buttons = buttons
        self.buttonstyles = buttonstyles
        self.buttondefaults = buttondefaults
        self.bar = bar
        self.closebutton = closebutton
        self.collapsed = collapsed

        self.icons = {
            OS.XP: [
                "xp/Critical Error.png",
                "xp/Exclamation.png",
                "xp/Information.png",
                "xp/Question.png"],
            OS.MAC_WINDOW_ID: ["",
                           "mac/Speech Bubble"],
            OS.UBUNTU: ["ubuntu/Error.png",
                       "ubuntu/Exclamation.png",
                       "ubuntu/Attention.png",
                       "ubuntu/Information.png",
                       "ubuntu/Question Mark.png"],
            OS.WINDOWS_95: ["95/Critical Error.png",
                   "95/Exclamation.png",
                   "95/Information.png",
                   "95/Question.png"],
            OS.MAC: ["mac/hand.png",
                          "mac/Exclamation.png",
                          "mac/Speech Bubble.png"],
            OS.WINDOWS_7: ["7/Critical Error.png",
                  "7/Exclamation.png",
                  "7/Information.png",
                  "7/Question Mark.png"]
        }
        self.cancomposite = self.os in [OS.WINDOWS_7, OS.CUSTOM]
        self.imgstr = img
        if self.imgstr:
            self.img = openimage(self.imgstr)
        else:
            self.img = emptyimg.copy()
        self.startpos = startpos
        self.animate = animate
        self.startrotation = startrotation
        self.animationlength = animationlength
        self.animationcloselength = animationcloselength
        self.origin = origin
        self.hashstring = str(self.os) + "," + str(self.active) + "," + self.text + "," + self.subtext + "," + str(self.icon) + "," + self.title + "," + str(self.buttons) + "," + str(
            self.buttonstyles
            ) + "," + str(self.buttondefaults) + "," + str(self.bar) + "," + str(self.closebutton) + "," + str(self.collapsed) + "," + str(self.imgstr)
        self.timingfunction = timingfunction
        self.endpos = endpos
        self.endrotation = endrotation
        self.endorigin = endorigin
        self.closetimingfunction = closetimingfunction

    def image(self, composite=None, pos=None, time=1, align="00", close=False):
        global generated
        self.hashstring = str(self.os) + "," + str(self.active) + "," + self.text + "," + self.subtext + "," + str(self.icon) + "," + self.title + "," + str(self.buttons) + "," + str(
            self.buttonstyles
            ) + "," + str(self.buttondefaults) + "," + str(self.bar) + "," + str(self.closebutton) + "," + str(self.collapsed) + "," + str(self.imgstr)
        if self.hashstring not in generated[self.os]:
            generated[self.os][self.hashstring] = self.__getimage()
        if composite:
            return self.__getimage(composite, pos, time, align, close, generated[self.os][self.hashstring])[0]
        return generated[self.os][self.hashstring][0]

    def copy(self):
        return Window(
            self.os, self.text, self.subtext, self.icon, self.title, self.buttons, self.buttonstyles, self.buttondefaults, self.bar, self.closebutton, self.active, self.collapsed,
            img=self.imgstr, startpos=self.startpos, animate=self.animate, startrotation=self.startrotation, animationlength=self.animationlength, origin=self.origin,
            animationcloselength=self.animationcloselength, timingfunction=self.timingfunction, endpos=self.endpos, endrotation=self.endrotation, endorigin=self.endorigin,
            closetimingfunction=self.closetimingfunction
            )

    def __str__(self):
        return self.hashstring

    def savestr(self):
        return b64encode(str(self.os).encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.active).encode("ascii")).decode("ascii") + "," + \
               b64encode(self.text.encode("ascii")).decode("ascii") + "," + \
               b64encode(self.subtext.encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.icon).encode("ascii")).decode("ascii") + "," + \
               b64encode(self.title.encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.buttons).encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.buttonstyles).encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.buttondefaults).encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.bar).encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.closebutton).encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.collapsed).encode("ascii")).decode("ascii") + "," + \
               b64encode(self.imgstr.encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.startpos).encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.animate).encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.startrotation).encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.animationlength).encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.origin).encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.endpos).encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.endrotation).encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.endorigin).encode("ascii")).decode("ascii") + "," + \
               b64encode(str(self.animationcloselength).encode("ascii")).decode("ascii") + "," + \
               b64encode(dictindex(timingfunctions, presets[currentpreset].timingfunction).encode("ascii")).decode("ascii") + "," + \
               b64encode(dictindex(timingfunctions, presets[currentpreset].closetimingfunction).encode("ascii")).decode("ascii")


def getkeyframeswhosedatais(param, value):
    global keyframes
    returnids = []
    i = 0
    for keyframe in keyframes:
        if param in keyframe.data:
            if keyframe.data[param] == value:
                returnids.append(i)
        i += 1
    return returnids


def getkeyframeswhoseprivatedatais(param, value):
    global keyframes
    returnids = []
    i = 0
    for keyframe in keyframes:
        if param in keyframe.privatedata:
            if keyframe.privatedata[param] == value:
                returnids.append(i)
        i += 1
    return returnids


def getkeyframeswhosedatacontains(param, value):
    global keyframes
    returnids = []
    i = 0
    for keyframe in keyframes:
        if param in keyframe.data:
            if value in keyframe.data[param]:
                returnids.append(i)
        i += 1
    return returnids


class Keyframe():
    def __init__(self, frame, x, y, window, align, keyframetype="error", data={}, privatedata={}):
        global currentdirection
        global keyframeview
        global keyframes
        self.window = window.copy()
        self.type = keyframetype
        self.data = data.copy()
        if self.type == "remove":
            if "remove" not in data:
                self.data["remove"] = [keyframes[i].frame for i in keyframeview.selected]
                # print(keyframeview.selected)
                removedframes = keyframeview.selected
            else:
                removedframes = getkeyframeswhoseframesare(self.data["remove"])
            self.window.animationlength = 0.01666666
            for i in removedframes:
                self.window.animationlength = max(self.window.animationlength, keyframes[i].window.animationcloselength)
                keyframes[i].privatedata["getclosedby"] = frame
        self.windowinactive = window.copy()
        self.windowinactive.active = False
        self.frame = frame
        self.start = frame / 60
        self.x = x
        self.y = y
        self.align = align
        self.close = False
        self.closeframe = 0
        self.privatedata = privatedata.copy()
        if "getclosedby" not in privatedata:
            self.privatedata["getclosedby"] = None

    def __str__(self):
        global keyframeview
        return str(self.window) + "," + str(self.x) + "," + str(self.y) + "," + self.align + "," + str(self.frame) + "," + str(self.close) + "," + str(self.closeframe) + "," + str(
            self.type
            ) + "," + str(self.data)

    def strframe(self, frame):
        return str(self.window) + "," + str(self.x) + "," + str(self.y) + "," + self.align + (
            "," + str(max(0, min(int(self.window.animationlength * 60), frame - self.frame))) if self.window.cancomposite else "") + "," + str(self.close) + "," + (
                   str(max(0, min(int(self.window.animationcloselength * 60), frame - self.closeframe))) if self.window.cancomposite else "") + "," + str(self.type) + "," + str(self.data)


def frametosavestr(frame):
    return frame.window.savestr() + "|" + str(frame.frame) + "|" + str(frame.x) + "|" + str(frame.y) + "|" + frame.align + "|" + str(frame.type) + "|" + str(list(frame.data.items()))


def stringtobool(s):
    return True if s == "True" else False


def stringtolist(s):
    # print("enter string:",s)
    s = s.strip()
    s = s[1:-1]
    # print("clipped string:",s)
    s = s.split(",")
    # print("s",s)
    finallist = []
    k = 0
    while k < len(s):
        i = s[k]
        # print(i)
        i = i.strip()
        if not i:
            k += 1
            continue
        if i[0] == "[":
            innerlist = ""
            while True:
                innerlist += s[k]
                # print("innerlist",innerlist)
                if s[k][-1] == "]":
                    break
                innerlist += ","
                k += 1
            # print("innerlist",innerlist)
            finallist.append(stringtolist(innerlist))
        elif i[0] == "(":
            innerlist = ""
            while True:
                innerlist += s[k]
                if s[k][-1] == ")":
                    break
                innerlist += ","
                k += 1
            # print("innerlist",innerlist)
            finallist.append(stringtolist(innerlist))
        elif i[0] == "'":
            if i == "''":
                finallist.append("")
            else:
                finallist.append(i[1:-1])
        elif i == "True" or i == "False":
            finallist.append(stringtobool(i))
        elif "." in i:
            finallist.append(float(i))
        else:
            finallist.append(int(i))
        k += 1
    return finallist


def savestrtowindow(savestr):
    array = savestr.split(",")
    notcustom = Window(
        os=b64decode(array[0].encode("ascii")).decode("ascii"),
        text=b64decode(array[2].encode("ascii")).decode("ascii"),
        subtext=b64decode(array[3].encode("ascii")).decode("ascii"),
        icon=int(b64decode(array[4].encode("ascii")).decode("ascii")),
        title=b64decode(array[5].encode("ascii")).decode("ascii"),
        buttons=stringtolist(b64decode(array[6].encode("ascii")).decode("ascii")),
        buttonstyles=stringtolist(b64decode(array[7].encode("ascii")).decode("ascii")),
        buttondefaults=stringtolist(b64decode(array[8].encode("ascii")).decode("ascii")),
        bar=stringtobool(b64decode(array[9].encode("ascii")).decode("ascii")),
        closebutton=stringtobool(b64decode(array[10].encode("ascii")).decode("ascii")),
        collapsed=stringtobool(b64decode(array[11].encode("ascii")).decode("ascii"))
    )
    notcustom.imgstr = b64decode(array[12].encode("ascii")).decode("ascii")
    if notcustom.imgstr:
        notcustom.img = Image.open(notcustom.imgstr)
    if len(array) == 18:
        if notcustom.os == OS.CUSTOM:
            notcustom.startpos = tuple(stringtolist(b64decode(array[13].encode("ascii")).decode("ascii")))
            notcustom.animate = stringtobool(b64decode(array[14].encode("ascii")).decode("ascii"))
            notcustom.startrotation = tuple(stringtolist(b64decode(array[15].encode("ascii")).decode("ascii")))
            notcustom.animationlength = float(b64decode(array[16].encode("ascii")).decode("ascii"))
            notcustom.origin = tuple(stringtolist(b64decode(array[17].encode("ascii")).decode("ascii")))
        elif notcustom.os == OS.WINDOWS_7:
            notcustom.startpos = (0, -0.017, 0.1)
            notcustom.animate = True
            notcustom.startrotation = (5, 0, 0)
            notcustom.origin = (0, 1, 0)
            notcustom.animationlength = 0.25
    else:
        notcustom.startpos = tuple(stringtolist(b64decode(array[13].encode("ascii")).decode("ascii")))
        notcustom.animate = stringtobool(b64decode(array[14].encode("ascii")).decode("ascii"))
        notcustom.startrotation = tuple(stringtolist(b64decode(array[15].encode("ascii")).decode("ascii")))
        notcustom.animationlength = float(b64decode(array[16].encode("ascii")).decode("ascii"))
        notcustom.origin = tuple(stringtolist(b64decode(array[17].encode("ascii")).decode("ascii")))
        notcustom.endpos = tuple(stringtolist(b64decode(array[18].encode("ascii")).decode("ascii")))
        notcustom.endrotation = tuple(stringtolist(b64decode(array[19].encode("ascii")).decode("ascii")))
        notcustom.endorigin = tuple(stringtolist(b64decode(array[20].encode("ascii")).decode("ascii")))
        notcustom.animationcloselength = float(b64decode(array[21].encode("ascii")).decode("ascii"))
        notcustom.timingfunction = timingfunctions[b64decode(array[22].encode("ascii")).decode("ascii")]
        notcustom.closetimingfunction = timingfunctions[b64decode(array[23].encode("ascii")).decode("ascii")]
    return notcustom


# print(stringtolist(str([["hi",2,True],True,5,"hello"])))
def savestrtoframe(savestr):
    array = savestr.split("|")
    # frame,x,y,window,align,keyframetype="error",data={}
    if len(array) == 7:
        thedata = stringtolist(array[6])
        return Keyframe(int(array[1]), int(array[2]), int(array[3]), savestrtowindow(array[0]), array[4], array[5], {i: j for i, j in thedata})
    return Keyframe(int(array[1]), int(array[2]), int(array[3]), savestrtowindow(array[0]), array[4])


def savekeyframes(path):
    global keyframes
    global audiopath
    global wallpaperpath
    savestr = b64encode(audiopath.encode("ascii")).decode("ascii") + "," + b64encode(wallpaperpath.encode("ascii")).decode("ascii")
    keyframeslen = len(keyframes)
    for frame in keyframes:
        savestr += "\n" + frametosavestr(frame)
    with open(path, "w") as file:
        file.write(savestr)


def loadkeyframes(path):
    global keyframes
    global keyframecache
    global closed
    global executor
    global executor2
    global workersamount
    global audiopath
    global wallpaperpath
    global filledframes
    keyframes = []

    with open(path, "r") as file:
        savestr = file.read()
    savestr = savestr.split("\n")
    metadata = savestr[0].split(',')
    audiopath = b64decode(metadata[0].encode("ascii")).decode("ascii")
    wallpaperpath = b64decode(metadata[1].encode("ascii")).decode("ascii")
    savestr.pop(0)
    for i in savestr:
        keyframes.append(savestrtoframe(i))
    keyframecache = {}
    filledframes = {}
    # closed = True
    # executor.shutdown()
    # closed = False
    # executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    # executor.submit(cacheframesmanager)
    # executor.submit(cachevisualizationjob)
    # cachestart([i.frame for i in keyframes])
    updatesound()
    updatewallpaper()
    updatekeyframeview()


markerfont = ImageFont.truetype("tahoma.ttf", 8)


class Keyframeview():
    def __init__(self):
        self.min = 0
        self.max = 10
        self.cursor = 2
        self.cursorimg = Image.open("Cursor.png").convert("RGBA")
        self.keyframeimg = Image.open("Keyframe.png").convert("RGBA")
        self.keyframeghostimg = Image.open("KeyframeGhost.png").convert("RGBA")
        self.keyframeActiveimg = Image.open("KeyframeActive.png").convert("RGBA")
        self.keyframeSelectedimg = Image.open("KeyframeSelected.png").convert("RGBA")
        self.grid = Image.open("grid.png").convert("RGBA")
        self.minorgrid = Image.open("minorgrid.png").convert("RGBA")
        self.width = 800
        self.lastclickpos = 0
        self.zoom = self.max - self.min
        self.m1pressed = False
        self.keyframeimage = None
        self.holdingframe = None
        self.movedpos = None
        self.active = None
        self.selected = []
        self.blank = Image.new("RGBA", (self.width, 50), (255, 192, 192))
        self.currentimg = self.blank.copy()
        self.gridimg = self.blank.copy()

    def getcoord(self, x):
        return floor(((x - self.min) / (self.zoom)) * self.width)

    def gettime(self, x):
        return (x / self.width) * (self.max - self.min) + self.min

    def image(self):
        global keyframes
        global temposnap
        global playing
        if temposnap:
            keyview = self.gridimg.copy()
        else:
            keyview = self.blank.copy()
        keyview.alpha_composite(self.cursorimg, (self.getcoord(self.cursor), 0))
        # print(self.active,self.selected)
        j = 0
        for i in keyframes:
            if i.start > self.min and i.start < self.max:
                keyview.alpha_composite(self.keyframeActiveimg if j == self.active else (self.keyframeSelectedimg if j in self.selected else self.keyframeimg), (self.getcoord(i.start) - 4, 19))
            j += 1
        self.currentimg = keyview.copy()
        return keyview

    def changecursorpos(self, event):
        global keyframepanel
        global starttime
        global tempovalue
        global temposnap
        global holdingshift
        if self.holdingframe is not None and self.movingcursor:
            movekeyframes(self.selected, round(self.movedpos - self.starthold))
            self.active = None
            self.selected = []
        clickpos = self.gettime(event.x)
        # print(event)
        self.cursor = clickpos
        if temposnap.get() == 1:
            self.cursor = round(clickpos * int(tempovalue.get()) / 60 * 4) / int(tempovalue.get()) * 60 / 4
        self.cursor = round(self.cursor * 60) / 60
        # print(self.cursor)
        # keyframepanel.image = self.image()
        nearframes = []
        if (self.lastclickpos == clickpos):
            nextkeyframe = getnextkeyframe(int(self.cursor * 60))
            if not checkcache(nextkeyframe)[4]:
                cachestart(nextkeyframe)
            if not holdingshift:
                self.active = None
            for i in keyframes:
                if i.start > self.min and i.start < self.max:
                    if abs(self.getcoord(i.start) - event.x) < 60:
                        nearframes.append(i.start)
            if nearframes:
                closestdistance = 9999
                closest = 999
                for i in nearframes:
                    if abs(self.getcoord(i) - event.x) < closestdistance:
                        closestdistance = abs(self.getcoord(i) - event.x)
                        closest = i
                self.cursor = closest

        starttime = time.time() - keyframeview.cursor
        self.lastclickpos = clickpos
        self.keyframeimage = self.image()
        self.m1pressed = False
        self.holdingframe = None
        self.movingcursor = False
        if (self.getkeyframeundercursor(event) is None and not holdingshift):
            self.selected = [self.active]
        updatekeyframeview()
        updatescreen()
        playaudiofromtimestamp(self.cursor)

    def updategrid(self):
        global tempovalue
        global temposnap
        global playing
        global markers
        global hertz
        global markerfont
        keyview = Image.new("RGBA", (self.width, 50), (255, 192, 192))
        keypix = ImageDraw.Draw(keyview)
        if temposnap.get() == 1 and not playing:
            # print(int((self.max-self.min)/60*int(tempovalue.get())*4))
            value = 0
            i = 0
            mult = 60 / int(tempovalue.get()) / 4
            while value < self.width:
                value = i * mult
                getcord = self.getcoord(value)
                # keyview.paste(self.grid if i&3 == 0 else self.minorgrid,(self.getcoord(value),0))
                keypix.line([getcord, 0, getcord, 49], fill=(245, 165, 165) if i & 3 == 0 else (250, 180, 180))
                i += 1
        if markers:
            i = 0
            drawn = 0
            for marker in markers:
                i += 1
                if marker["position"] / hertz < self.min - self.zoom / 6:
                    continue
                if marker["position"] / hertz > self.max:
                    break
                if drawn > 200:
                    break
                getcord = self.getcoord(marker["position"] / hertz)
                keypix.line([getcord, 0, getcord, 49], fill=(192, 192, 96))
                labeltext = marker["label"].decode("ascii")
                bbox = keypix.multiline_textbbox([getcord, 40], labeltext, font=markerfont)
                bbox = (bbox[0], bbox[1], bbox[2], min(bbox[3], 49))
                lightness = (i * 111) % 255
                keypix.rectangle(bbox, fill=(255, lightness, lightness), outline=(255, 64, 64))
                keypix.text([getcord, 40], labeltext, font=markerfont, fill=(0, 0, 0, 255))
                drawn += 1
        self.gridimg = keyview

    def changezoom(self, event):
        self.zoom = max(0.5, self.zoom - event.delta / 240)
        self.min, self.max = [self.cursor - (self.max - self.min) / 2, self.cursor + (self.max - self.min) / 2]
        self.min = max(0, self.cursor - self.zoom / 2)
        self.max = self.zoom + self.min
        self.updategrid()
        updatekeyframeview()

    # def update(self):
    #    global czepanel
    #    global keyframes
    #    currentframe = geterrors(self.cursor)
    #    fsf = ImageTk.PhotoImage(currentframe)
    #    czepanel.configure(image=fsf)
    #    czepanel.image = fsf
    def moveby(self, value):
        global tempovalue
        global temposnap
        if temposnap.get() == 1:
            mult = 15 / int(tempovalue.get())
            curbeat = round(self.cursor / mult) + value
            # print(curbeat)
            self.cursor = round(curbeat * mult * 60) / 60
        else:
            self.cursor = round(60 * self.cursor + value) / 60

    def motion(self, event):
        global tempovalue
        global temposnap
        if self.m1pressed and self.holdingframe is not None:
            clickpos = round(self.gettime(event.x) * 60) / 60
            self.movingcursor = True
            if temposnap.get() == 1:
                self.movedpos = round(clickpos * int(tempovalue.get()) / 15) / int(tempovalue.get()) * 15 * 60
            else:
                self.movedpos = clickpos * 60
            temp = self.keyframeimage.copy()
            temp.alpha_composite(self.keyframeghostimg, (self.getcoord(self.movedpos / 60) - 4, 19))
            keyframeimage = ImageTk.PhotoImage(temp)
            keyframepanel.configure(image=keyframeimage)
            keyframepanel.image = keyframeimage

    def button1pressed(self, event):
        global keyframes
        self.movingcursor = False
        self.m1pressed = True
        # frame = round(self.gettime(event.x)*60)
        i = self.getkeyframeundercursor(event)
        if i is not None:
            self.starthold = keyframes[i].frame
            self.holdingframe = i
            self.active = i
            if holdingshift:
                if i not in self.selected:
                    self.selected.append(i)
            else:
                self.selected = [i]

    def getkeyframeundercursor(self, pos):
        global keyframes
        if abs(pos.y - 25) < 5:
            for i in range(len(keyframes)):
                if abs(self.getcoord(keyframes[i].frame / 60) - pos.x) < 5:
                    # print(i)
                    return i


def getnextkeyframe(startframe):
    global keyframes
    lastgood = 0
    for i in keyframes:
        lastgood = i.frame
        if i.frame > startframe:
            break
    return lastgood


errors = []
currentframeimg = Image.new("RGBA", (1280, 720), (8, 8, 8, 255))
currentwallpaper = Image.new("RGBA", (1280, 720), (8, 8, 8, 255))


def geterrors(time):
    global keyframes
    global currentframeimg
    global currentwallpaper
    global keyframecache
    i = 0
    frames, cachestr, notimportant, last, success, cacheimg = checkcache(round(time * 60))
    if success:
        currentframeimg = notimportant[0]
        return cacheimg[0]

    fillcache(notimportant, frames, cachestr, round(time * 60))
    returnimg = keyframecache[cachestr][0]
    currentframeimg = keyframecache[cachestr][1]
    # print(returnimg)
    return returnimg


playing = False
framestart = time.time()
currentframe = time.time() - framestart
framenumber = 0
starttime = time.time()
curtime = time.time() - starttime
lastframe = 0
stats = None
pygame.init()
windowgame = pygame.display.set_mode((1280, 720))
clockgame = pygame.time.Clock()
chosewindow = None


def getalignedpos(pos, align, size):
    return (int(pos[0]) - (size[0] * int(align[0]) // 2), int(pos[1]) - (size[1] * int(align[1]) // 2))


def playback():
    global playing
    global keyframeview
    global keyframepanel
    global currentframe
    global framestart
    global framenumber
    global curtime
    global starttime
    global timestampvar
    global stats
    global closed
    global windowgame
    global clockgame
    global currentframeimg
    global chosewindow
    global snap
    global currentdirection
    global currentpreset
    try:
        pygame.fastevent.init()
        starttime = time.time() - keyframeview.cursor
        curtime = time.time() - starttime
        pygameSurface = None
        chosenwindowimageSurface = None
        lastpos = None
        while not closed:
            clockgame.tick(60)
            prevcurtime = curtime
            if playing:
                curtime = time.time() - starttime
                keyframeview.cursor = round(curtime * 60) / 60
                pygameSurface = geterrors(curtime)
            else:
                starttime = time.time() - keyframeview.cursor
                curtime = time.time() - starttime
                if curtime != prevcurtime:
                    pygameSurface = geterrors(curtime)
            if not pygameSurface:
                pygameSurface = geterrors(curtime)
            windowgame.blit(pygameSurface, (0, 0))
            for event in pygame.fastevent.get():
                if event.type == pygame.QUIT:
                    closed = True
                elif event.type == 1024 and not playing:  # MouseMotion
                    chosenwindow = presets[currentpreset]
                    if chosenwindow != chosewindow:
                        chosenwindowimage = chosenwindow.image()
                        chosenwindowimageSurface = pygame.image.fromstring(chosenwindowimage.tobytes(), chosenwindowimage.size, "RGBA").convert_alpha()
                    lastpos = getalignedpos((round(event.pos[0] / snap) * snap, round(event.pos[1] / snap) * snap), currentdirection, chosenwindowimage.size)
                elif event.type == 1025 and pygame.mouse.get_pressed(num_buttons=3)[0]:  # MouseDown
                    createkeyframe(event.pos[0], event.pos[1])
                    updatekeyframeview()
                elif event.type == 32785 and pygame.mouse.get_pressed(num_buttons=5)[0]:  # FocusGained, basically MouseDown
                    createkeyframe(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                    updatekeyframeview()
                elif event.type == 1027:  # scroll
                    cascade(event.y)
                elif event.type == 768:  # keyboard
                    keyboard(event.scancode)
            if chosenwindowimageSurface and not playing:
                windowgame.blit(chosenwindowimageSurface, lastpos)
            pygame.display.update()

            # print("douing")
    except Exception:
        print("PYGAME ERROR:", sys.exc_info()[0](traceback.format_exc()))
    print("end pygame")


def updatekeyframeviewduringplayback():
    global playing
    if playing:
        updatekeyframeview()
    timelineroot.after(30, updatekeyframeviewduringplayback)


holdingshift = True


def keyboard(event):
    global playing
    global keyframeview
    global holdingshift
    if event == 44:  # space
        play()
        # print(playing)
    elif event == 80:
        keyframeview.moveby(-1)
        updatescreen()
        updatekeyframeview()
    elif event == 79:
        keyframeview.moveby(1)
        updatescreen()
        updatekeyframeview()


def keyboardtk(event):
    global holdingshift
    # print(event.keycode)
    if event.keycode == 16:
        holdingshift = True
    elif event.keycode == 46:  # delete
        deletekeyframesparam(keyframeview.selected)
        updatescreen()
        updatekeyframeview()
    elif event.keycode == 32:  # space
        play()
    elif event.keycode == 37:
        keyframeview.moveby(-1)
        updatescreen()
        updatekeyframeview()
    elif event.keycode == 39:
        keyframeview.moveby(1)
        updatescreen()
        updatekeyframeview()


def keyboardrelease(event):
    global holdingshift
    if event.keycode == 16:
        holdingshift = False


def createkeyframeparam(frame, x, y, window, align, keyframetype, data, privatedata):
    global keyframeview
    global keyframes
    global selected
    global presets
    global lastframe
    # frame = round(keyframeview.cursor*60)
    lastgoodi = -1
    # chosenwindow = presets[int(selected.get().split(":")[0])]
    if keyframes:
        for i in range(len(keyframes)):
            if keyframes[i].frame <= frame:
                lastgoodi = i
            else:
                break
        if (keyframes[lastgoodi].frame != frame):
            lastgoodi += 1
            keyframes.insert(lastgoodi, Keyframe(frame, x, y, window, align, keyframetype, data, privatedata))
        else:
            keyframes[lastgoodi] = Keyframe(frame, x, y, window, align, keyframetype, data, privatedata)
        return lastgoodi
    else:
        keyframes.append(Keyframe(frame, x, y, window, align, keyframetype, data, privatedata))
        return len(keyframes) - 1
    # cachestart(frame)
    # print([i.frame for i in keyframes])


def deletekeyframeparam(frame):
    global keyframeview
    global keyframes
    # frame = round(keyframeview.cursor*60)
    for i in range(len(keyframes)):
        if keyframes[i].frame == frame:
            keyframes.pop(i)
            cachestart(frame)
            break


cascading = 0


def createkeyframe(x, y, keyframetype="error", data={}):
    global keyframeview
    global keyframes
    global selected
    global presets
    global lastframe
    global cascading
    global keyframecache
    global wallpaperpath
    global czepanel
    global currentframeimg
    global snap
    global currentdirection
    global currentpreset
    event = Pos(round(x / snap) * snap, round(y / snap) * snap)
    frame = round(keyframeview.cursor * 60)
    lastgoodi = -1
    chosenwindow = presets[currentpreset]
    if cascading > 0 and keyframeview.active is not None:
        event = Pos(keyframes[keyframeview.active].x, keyframes[keyframeview.active].y) + Pos(cascading * (1 - int(currentdirection[0])), cascading * (1 - int(currentdirection[1])))
    # print(keyframeview.active)
    if keyframes:
        curframes = []

        for i in range(len(keyframes)):
            if keyframes[i].frame <= frame:
                lastgoodi = i
                # curframes.append(keyframes[i])
            else:
                break
        # strcurframes = str(curframes)+","+wallpaperpath.get()
        if (keyframes[lastgoodi].frame != frame):
            # print(lastgoodi,keyframes[lastgoodi].frame,frame)
            lastgoodi += 1
            keyframes.insert(lastgoodi, Keyframe(frame, event.x, event.y, chosenwindow, currentdirection, keyframetype, data))
            keyframeview.active = lastgoodi
            keyframeview.selected = [lastgoodi]
        else:
            keyframes[lastgoodi] = Keyframe(frame, event.x, event.y, chosenwindow, currentdirection, keyframetype, data)
            keyframeview.active = lastgoodi
            keyframeview.selected = [lastgoodi]
            # curframes[lastgoodi] = Keyframe(frame,event.x,event.y,chosenwindow)
        # print("== ADDING:",str(keyframes[lastgoodi]))
    else:
        keyframes.append(Keyframe(frame, event.x, event.y, chosenwindow, currentdirection, keyframetype, data))
        keyframeview.active = len(keyframes) - 1
        keyframeview.selected = [len(keyframes) - 1]
        # print("== ADDING:",str(keyframes[len(keyframes)-1]))
    cachestart(frame)
    # cacheframes(frame)
    # print([i.frame for i in keyframes])
    updatescreen()
    updatekeyframeview()
    lastframe = Pos(event.x, event.y)


def deletekeyframe():
    global keyframeview
    global keyframes
    frame = round(keyframeview.cursor * 60)
    for i in range(len(keyframes)):
        if keyframes[i].frame == frame:
            keyframes.pop(i)
            cachestart(frame)
            break
    updatekeyframeview()
    updatescreen()


def deletekeyframesparam(keyframesdelete):
    global keyframes
    global keyframeview
    # print(keyframesdelete)
    cachestart([keyframes[i].frame for i in keyframesdelete])
    temp = []
    for i in range(len(keyframes)):
        if i not in keyframesdelete:
            temp.append(keyframes[i])
    keyframes = temp.copy()
    temp = []
    for i in range(len(keyframeview.selected)):
        if i not in keyframesdelete:
            temp.append(keyframes[i])
    keyframeview.selected = [i for i in range(len(temp.copy()))]
    # executor.submit(cacheframes,keyframeview.selected[0].frame if keyframeview.selected else 0)
    keyframeview.active = None if keyframeview.active in keyframesdelete else keyframeview.active
    keyframeview.holdingframe = None if keyframeview.holdingframe in keyframesdelete else keyframeview.holdingframe


def updatescreen():
    global czepanel
    global keyframeview
    global previewmousepos
    currentframe = geterrors(keyframeview.cursor)
    # fsf = ImageTk.PhotoImage(currentframe)
    # czepanel.configure(image=fsf)
    # czepanel.image = fsf
    # placementpreview(previewmousepos)


def updatekeyframeview():
    global keyframeview
    global timestampvar
    keyframeview.keyframeimage = keyframeview.image()
    keyframeimage = ImageTk.PhotoImage(keyframeview.keyframeimage)
    keyframepanel.configure(image=keyframeimage)
    keyframepanel.image = keyframeimage
    timestampvar.set(
        f"{floor(keyframeview.cursor * 600) % 10}{floor(keyframeview.cursor / 60) % 10}:{floor(keyframeview.cursor / 10) % 10}{str(keyframeview.cursor % 10)[:5]}   frame: {round(keyframeview.cursor * 60)}"
        )


def dictindex(dictionary, value):
    return list(dictionary.keys())[list(dictionary.values()).index(value)]


def updateentries(a=None, b=None, c=None):
    global entrytext
    global entrytitlevar
    global entrybutton1var
    global entrybutton2var
    global entrybutton3var
    global presets
    global selected
    global selectedicon
    global iconlist
    global currentpreset
    global customdurationvar
    global customoriginzvar
    global customoriginyvar
    global customoriginxvar
    global customrotationzvar
    global customrotationyvar
    global customrotationxvar
    global custompositionzvar
    global custompositionyvar
    global custompositionxvar
    global customclosedurationvar
    global customcloseoriginzvar
    global customcloseoriginyvar
    global customcloseoriginxvar
    global customcloserotationzvar
    global customcloserotationyvar
    global customcloserotationxvar
    global customclosepositionzvar
    global customclosepositionyvar
    global customclosepositionxvar
    global currentcustomimg
    global selectedtimingfunction
    entrytext.delete(1.0, END)
    entrytext.insert(END, presets[currentpreset].text)
    entrytitlevar.set(presets[currentpreset].title)
    # print(presets[presetid].buttons)
    entrybutton1var.set(presets[currentpreset].buttons[0])
    entrybutton2var.set(presets[currentpreset].buttons[1])
    entrybutton3var.set(presets[currentpreset].buttons[2])
    selectedicon.set(iconlist[presets[currentpreset].icon])
    selectedos.set(presets[currentpreset].os.value)
    custompositionxvar.set(presets[currentpreset].startpos[0])
    custompositionyvar.set(presets[currentpreset].startpos[1])
    custompositionzvar.set(presets[currentpreset].startpos[2])
    customrotationxvar.set(presets[currentpreset].startrotation[0])
    customrotationyvar.set(presets[currentpreset].startrotation[1])
    customrotationzvar.set(presets[currentpreset].startrotation[2])
    customoriginxvar.set(presets[currentpreset].origin[0])
    customoriginyvar.set(presets[currentpreset].origin[1])
    customoriginzvar.set(presets[currentpreset].origin[2])
    customdurationvar.set(presets[currentpreset].animationlength)
    customclosepositionxvar.set(presets[currentpreset].endpos[0])
    customclosepositionyvar.set(presets[currentpreset].endpos[1])
    customclosepositionzvar.set(presets[currentpreset].endpos[2])
    customcloserotationxvar.set(presets[currentpreset].endrotation[0])
    customcloserotationyvar.set(presets[currentpreset].endrotation[1])
    customcloserotationzvar.set(presets[currentpreset].endrotation[2])
    customcloseoriginxvar.set(presets[currentpreset].endorigin[0])
    customcloseoriginyvar.set(presets[currentpreset].endorigin[1])
    customcloseoriginzvar.set(presets[currentpreset].endorigin[2])
    customclosedurationvar.set(presets[currentpreset].animationcloselength)
    currentcustomimg = presets[currentpreset].imgstr
    selectedtimingfunction.set(dictindex(timingfunctions, presets[currentpreset].timingfunction))
    selectedclosetimingfunction.set(dictindex(timingfunctions, presets[currentpreset].closetimingfunction))
    # timingfunctions[selectedtimingfunction.get()]
    # print(presets[currentpreset].animationlength)


def updatepreset(a=None, b=None, c=None):
    global entrytext
    global entrytitlevar
    global entrybutton1var
    global entrybutton2var
    global entrybutton3var
    global presets
    global selected
    global selectedicon
    global currentpreset
    global selectedos
    global customdurationvar
    global customoriginzvar
    global customoriginyvar
    global customoriginxvar
    global customrotationzvar
    global customrotationyvar
    global customrotationxvar
    global custompositionzvar
    global custompositionyvar
    global custompositionxvar
    global customclosedurationvar
    global customcloseoriginzvar
    global customcloseoriginyvar
    global customcloseoriginxvar
    global customcloserotationzvar
    global customcloserotationyvar
    global customcloserotationxvar
    global customclosepositionzvar
    global customclosepositionyvar
    global customclosepositionxvar
    global currentcustomimg
    global selectedtimingfunction
    presetid = currentpreset
    presets[presetid].text = entrytext.get(1.0, END).strip().replace("\\n", "\n")
    # print(entrytext.get(1.0,END).strip())
    presets[presetid].title = entrytitlevar.get()
    # print(presets[presetid].buttons)
    presets[presetid].buttons = [entrybutton1var.get(), entrybutton2var.get(), entrybutton3var.get()]
    presets[presetid].icon = int(selectedicon.get()[0])
    presets[presetid].os = OS(selectedos.get())
    presets[currentpreset].startpos = (float(custompositionxvar.get()), float(custompositionyvar.get()), float(custompositionzvar.get()))
    presets[currentpreset].startrotation = (float(customrotationxvar.get()), float(customrotationyvar.get()), float(customrotationzvar.get()))
    presets[currentpreset].origin = (float(customoriginxvar.get()), float(customoriginyvar.get()), float(customoriginzvar.get()))
    presets[currentpreset].animationlength = float(customdurationvar.get())
    presets[currentpreset].endpos = (float(customclosepositionxvar.get()), float(customclosepositionyvar.get()), float(customclosepositionzvar.get()))
    presets[currentpreset].endrotation = (float(customcloserotationxvar.get()), float(customcloserotationyvar.get()), float(customcloserotationzvar.get()))
    presets[currentpreset].endorigin = (float(customcloseoriginxvar.get()), float(customcloseoriginyvar.get()), float(customcloseoriginzvar.get()))
    presets[currentpreset].animationcloselength = float(customclosedurationvar.get())
    if currentcustomimg:
        presets[currentpreset].imgstr = currentcustomimg
        presets[currentpreset].img = Image.open(currentcustomimg)
    presets[currentpreset].timingfunction = timingfunctions[selectedtimingfunction.get()]
    presets[currentpreset].closetimingfunction = timingfunctions[selectedclosetimingfunction.get()]
    updatepresetview()
    # updatescreen()


sound = None
audioplayback = None


def play():
    global playing
    global keyframeview
    playing = not playing
    playaudiofromtimestamp(keyframeview.cursor)
    updatekeyframeview()


def playaudiofromtimestamp(timestamp):
    global sound
    global audioplayback
    # print(timestamp)
    if playing:
        if audioplayback:
            audioplayback.stop()
        if sound:
            splice = sound[int(timestamp * 1000):]
            audioplayback = _play_with_simpleaudio(splice)
    else:
        if audioplayback is not None:
            audioplayback.stop()


def set_focus(event):
    global timelineroot
    x, y = timelineroot.winfo_pointerxy()
    timelineroot.winfo_containing(x, y).focus()


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, b):
        return Pos(self.x + b.x, self.y + b.y)

    def __mul__(self, b):
        if isinstance(b, int):
            return Pos(self.x * b, self.y * b)


# previewmousepos = Pos(0,0)
# def placementpreview(event):
#    global playing
#    global currentframeimg
#    if not playing:
#        global placementpreviewpanel
#        global currentframeimg
#        global previewmousepos

markers = []
hertz = 44100


def updatesound():
    global sound
    global audiopath
    global markers
    global hertz
    # print(audiopath)
    if audiopath:
        try:
            sound = AudioSegment.from_file(audiopath)
            if audiopath[-4:] == ".wav":
                try:
                    wav = wavfile.read(audiopath, readmarkers=True, readmarkerlabels=True, readmarkerslist=True)
                    markers = wav[5]
                    hertz = wav[0]
                except:
                    print("Error in updatesound(): WAV file is invalid")
        except FileNotFoundError:
            print("Error in updatesound(): BGM path not found")
        except Exception as e:
            print(f"Error in updatesound(): {e}")


def cascade(y):
    global cascading
    global cascadingvar
    if y > 0:
        cascading += 1
    else:
        cascading = max(0, cascading - 1)
    cascadingvar.set(f"Cascading distance: {cascading}")


"""def moveerrorkeyframe(keyframeid,delta):
    return
def moveremovekeyframe(keyframeid,delta):
    return

movekeyframeslist = {"error":lambda keyframeid,delta: moveerrorkeyframe(keyframeid,delta),
                     "remove":lambda keyframeid,delta: moveremovekeyframe(keyframeid,delta)}

movekeyframeslist[keyframe.type](keyframeid,delta)"""


def movekeyframe(keyframeid, delta):
    global keyframes
    if keyframes[keyframeid].type == "error":
        copyframe = keyframes[keyframeid]
        keyframes.pop(keyframeid)
        theid = createkeyframeparam(copyframe.frame + delta, copyframe.x, copyframe.y, copyframe.window, copyframe.align, copyframe.type, copyframe.data, copyframe.privatedata)
        theremoves = getkeyframeswhosedatacontains("remove", copyframe.frame)
        for remove in theremoves:
            keyframes[remove].data["remove"][keyframes[remove].data["remove"].index(copyframe.frame)] = copyframe.frame + delta
    elif keyframes[keyframeid].type == "remove":
        copyframe = keyframes[keyframeid]
        keyframes.pop(keyframeid)
        theid = createkeyframeparam(copyframe.frame + delta, copyframe.x, copyframe.y, copyframe.window, copyframe.align, copyframe.type, copyframe.data, copyframe.privatedata)
        theremoves = getkeyframeswhoseprivatedatais("getclosedby", keyframeid)
        for remove in theremoves:
            keyframes[remove].privatedata["getclosedby"] = theid


def movekeyframes(keyframesmove, to):
    global keyframes
    keyframesmove = [keyframes[i] for i in keyframesmove]
    earliest = 99999999999
    print(keyframesmove)
    for i in keyframesmove:
        keyframeid = keyframes.index(i)
        earliest = min(earliest, keyframes[keyframeid].frame, keyframes[keyframeid].frame + to)
        movekeyframe(keyframeid, to)
    cachestart(earliest)


def updatewallpaper():
    global currentwallpaper
    global wallpaperpath

    if wallpaperpath:
        try:
            currentwallpaper = Image.open(wallpaperpath).convert("RGBA").resize((1280, 720), 0)
        except FileNotFoundError:
            print("Error in updatewallpaper(): Wallpaper path not found")
    else:
        currentwallpaper = Image.new("RGBA", (1280, 720), (8, 8, 8, 255))
    if keyframes:
        cachestart([i.frame for i in keyframes])
    updatescreen()


def dontclose():
    return


workersamount = 3
cacherefresh = False
cachestartpos = []
cacherunning = False
framestocache = []


def fillcache(startimg, fillin, fillstring, frame):
    global keyframecache
    returnimg = startimg[0]
    stillinactive = startimg[1]
    lenerrors = len(fillin) - 1
    i = 0
    time = frame / 60
    if fillin:
        returnimg = startimg[1]
    for error in fillin:
        lenerrors = len(fillin) - 1
        if i == lenerrors:
            if error.window.cancomposite:
                if not error.close:
                    stillinactive = returnimg.copy()
                    stillinactive = error.windowinactive.image(stillinactive, (error.x, error.y), time - error.start, error.align)
                    returnimg = error.window.image(returnimg, (error.x, error.y), time - error.start, error.align)
                else:
                    stillinactive = returnimg.copy()
                    stillinactive = error.windowinactive.image(stillinactive, (error.x, error.y), time - error.closeframe / 60, error.align, True)
                    returnimg = error.window.image(returnimg, (error.x, error.y), time - error.closeframe / 60, error.align, True)
                    # print(time-error.closeframe/60)
            else:
                stillinactive = returnimg.copy()
                temp = error.windowinactive.image()
                stillinactive.alpha_composite(temp, getalignedpos((error.x, error.y), error.align, temp.size))
                returnimg.alpha_composite(error.window.image(), getalignedpos((error.x, error.y), error.align, temp.size))

            i += 1
            continue
        if error.window.cancomposite:
            if error.close:
                returnimg = error.windowinactive.image(returnimg, (error.x, error.y), time - error.closeframe / 60, error.align, True)
            else:
                returnimg = error.windowinactive.image(returnimg, (error.x, error.y), time - error.start, error.align)
        else:
            temp = error.windowinactive.image()
            returnimg.alpha_composite(temp, getalignedpos((error.x, error.y), error.align, temp.size))
        i += 1
    if len(keyframecache) > 500:
        del keyframecache[list(keyframecache.keys())[0]]
    global keyframeview
    keyframecache[fillstring] = [pygame.image.fromstring(returnimg.tobytes(), returnimg.size, returnimg.mode).convert(), returnimg, stillinactive]
    filledframes[frame] = True


class Emptylast():
    def __init__(self):
        self.frame = 0


def errorgetcache(frame, appended, timekeyframes, returnimg, lastcalculatedkeyframes, keyframesstr, keyframe):
    global keyframecache
    appended = keyframesstr + "," + keyframe.strframe(frame)
    success = False
    if appended in keyframecache:
        timekeyframes.append(keyframe)
        lastcalculatedkeyframes = timekeyframes.copy()
        returnimg = keyframecache[appended]
        success = True
    else:
        timekeyframes.append(keyframe)
    return appended, success, returnimg, lastcalculatedkeyframes


def getkeyframeswhoseframesare(frame):
    global keyframes
    theframes = []
    i = 0
    for keyframe in keyframes:
        if keyframe.frame in frame:
            theframes.append(i)
        i += 1
    return theframes


def removegetcache(frame, appended, timekeyframes, returnimg, lastcalculatedkeyframes, keyframesstr, keyframe):
    global keyframecache
    lastcalculatedkeyframes = []
    removedkeyframes = getkeyframeswhoseframesare(keyframe.data["remove"])
    for remove in removedkeyframes:
        if keyframes[remove] in timekeyframes:
            ind = timekeyframes.index(keyframes[remove])
            if frame - keyframe.frame >= keyframe.window.animationlength * 60:
                timekeyframes.pop(ind)
            else:
                timekeyframes[ind] = copy.deepcopy(timekeyframes[ind])
                timekeyframes[ind].close = True
                timekeyframes[ind].closeframe = keyframe.frame
    keyframesstr = wallpaperpath
    appended = wallpaperpath
    for timekeyframe in timekeyframes:
        appended = keyframesstr + "," + timekeyframe.strframe(frame)
        keyframesstr = appended
    success = False
    # print("DICTIONARY: ")
    # print("\n".join(keyframecache.keys()))
    # print("WANTED: ")
    # print(appended)
    if appended in keyframecache:
        # print("ITS IN!")
        lastcalculatedkeyframes = timekeyframes.copy()
        returnimg = keyframecache[appended]
        success = True
    else:
        # print("its not")
        newcalculatedkeyframes = []
        refillkeyframes = []
        theappend = wallpaperpath
        successappend = wallpaperpath
        returnimg = [pygame.image.fromstring(currentwallpaper.tobytes(), currentwallpaper.size, currentwallpaper.mode).convert(), currentwallpaper.copy(), currentwallpaper.copy()]
        for refillframe in timekeyframes:
            theappend = theappend + "," + refillframe.strframe(frame)
            refillkeyframes.append(refillframe)
            if theappend in keyframecache:
                newcalculatedkeyframes = refillkeyframes.copy()
                successappend = theappend
        if successappend in keyframecache:
            returnimg = keyframecache[successappend]
        lastcalculatedkeyframes = newcalculatedkeyframes
    return appended, success, returnimg, lastcalculatedkeyframes


keyframecachetypes = {
    "error": (lambda frame, appended, timekeyframes, returnimg, lastcalculatedkeyframes, keyframesstr, keyframe: errorgetcache(
        frame, appended, timekeyframes, returnimg, lastcalculatedkeyframes, keyframesstr, keyframe
        )),
    "remove": (lambda frame, appended, timekeyframes, returnimg, lastcalculatedkeyframes, keyframesstr, keyframe: removegetcache(
        frame, appended, timekeyframes, returnimg, lastcalculatedkeyframes, keyframesstr, keyframe
        ))
}


def checkcache(frame):
    global keyframes
    global wallpaperpath
    global keyframecache
    global currentwallpaper
    global keyframecachetypes
    lastcalculatedkeyframes = []
    keyframesstr = wallpaperpath
    timekeyframes = []
    returnimg = [pygame.image.fromstring(currentwallpaper.tobytes(), currentwallpaper.size, currentwallpaper.mode).convert(), currentwallpaper.copy(), currentwallpaper.copy()]
    last = Emptylast()
    success = True
    appended = wallpaperpath
    try:
        for keyframe in keyframes:
            if keyframe.frame > frame:
                break
            appended, success, returnimg, lastcalculatedkeyframes = keyframecachetypes[keyframe.type](frame, appended, timekeyframes, returnimg, lastcalculatedkeyframes, keyframesstr, keyframe)
            keyframesstr = appended
            last = keyframe
        return timekeyframes[len(lastcalculatedkeyframes):], keyframesstr, [returnimg[1].copy(), returnimg[2].copy()], last, success, returnimg[:1]
    except Exception as e:
        print("ERROR in checkcache():", e)
    # print(keyframesstr)


# {keyframe.strframe(100): [pygameimage,PILActiveImage,PILInactiveImage]}
cachevisualizationdict = {}
closed = False
theressomethingtoconfigure = False
configuringimage = None


def updatevisualization():
    global theressomethingtoconfigure
    global configuringimage
    global keyframepanel
    global debugvar
    global keyframecache
    global cachestartpos
    global framestocache
    if theressomethingtoconfigure:
        configuringimagetk = ImageTk.PhotoImage(configuringimage)
        keyframepanel.configure(image=configuringimagetk)
        keyframepanel.image = configuringimagetk
        theressomethingtoconfigure = False
    debugvar.set(f"cache size: {len(keyframecache)}, queue size: {len(cachestartpos)}, frames to cache: {len(framestocache)}")
    timelineroot.after(100, updatevisualization)


def cachevisualizationjob():
    global cachevisualizationdict
    global keyframeview
    global keyframepanel
    global closed
    global theressomethingtoconfigure
    global configuringimage
    while not closed:

        # print(cachevisualizationdict)
        temp = cachevisualizationdict.copy()
        if temp:
            keyframeimage = keyframeview.currentimg
            for i in temp:
                keyframeimage.paste(Image.new("RGBA", (1, 50), cachevisualizationdict[i]), (keyframeview.getcoord(i / 60), 0))
                del cachevisualizationdict[i]
            configuringimage = keyframeimage.copy()
            theressomethingtoconfigure = True
            # keyframeimagetk = ImageTk.PhotoImage(keyframeimage)
            # keyframepanel.configure(image=keyframeimagetk)
            # keyframepanel.image = keyframeimagetk
        # cachevisualizationdict = {}
        time.sleep(0.5)
    # print("visualization:",closed)


def optimizecache():
    global keyframes
    global keyframecache
    doing = True
    l = keyframes[0]
    theframe = l.frame
    original = keyframes[0]
    cur = 1
    try:
        nextkeyframe = keyframes[1]
    except:
        nextkeyframe = None
    allstr = []
    while doing:
        keyframesstr = checkcache(theframe)[1]
        allstr.append(keyframesstr)
        theframe += 1

        if theframe - original.frame > original.window.animationlength * 60:
            l = nextkeyframe

            # print(nextkeyframe)
            original = nextkeyframe
            if nextkeyframe is not None:
                cur += 1
                theframe = l.frame
                try:
                    nextkeyframe = keyframes[cur]
                except:
                    nextkeyframe = None
            else:
                doing = False
    newcache = {}
    for thestr in allstr:
        if thestr in keyframecache:
            newcache[thestr] = keyframecache[thestr]
    keyframecache = newcache
    # print(allstr)


def cachejob(startframe):
    global keyframeview
    global closed
    global cachevisualizationdict
    global keyframes
    i = 0
    while True:

        if closed:
            break
        try:
            frames, cachestr, returnimg, last, success, notimportant = checkcache(startframe + i)
            if last.frame > startframe:
                # print(last.frame)
                return
            if last.window.animationlength * 60 < i:
                return
            if not success:
                fillcache(returnimg, frames, cachestr, startframe + i)
            cachevisualizationdict[startframe + i] = ((startframe * 913) % 255, (startframe * 701) % 255, (startframe * 863) % 255)
            # print(i)
            i += 1

        except Exception:
            print("ERROR in cachejob():", sys.exc_info()[0](traceback.format_exc()))
            break


def cachestart(start):
    global cacherefresh
    global cachestartpos
    global framestocache
    global cacherunning
    global keyframes
    # print(start)
    if isinstance(start, list):
        smallest = start[0]
        for i in start:
            smallest = min(smallest, i)
        cachestartpos.append(smallest)
        # framestocache = start.copy()
    # print("start:",framestocache)
    else:
        cachestartpos.append(start)
        # framestocache = []
    print("cachestart() starting to cache:", start)
    cacherefresh = True
    cacherunning = True


def cacheframesmanager():
    global framestocache
    global cacherunning
    global cacherefresh
    global keyframes
    global executor2
    global keyframecache
    global workersamount
    global closed
    global cachestartpos
    while not closed:
        if cacherunning:
            if cacherefresh:
                print("cacheframesmanager() got cache:", cachestartpos)
                cacherefresh = False
                i = 0
                for keyframe in keyframes:
                    if keyframe.frame >= cachestartpos[0] and keyframe.frame not in framestocache:
                        framestocache.append(keyframe.frame)
                    i += 1
                if cachestartpos[0] not in framestocache:
                    framestocache.insert(0, cachestartpos[0])
                cachestartpos.pop(0)
                executor2.shutdown()
                updatekeyframeview()
                executor2 = concurrent.futures.ThreadPoolExecutor()
            if framestocache:
                executor2.submit(cachejob, framestocache[0])
                print("cacheframesmanager() submitting job:", framestocache[0])
                framestocache.pop(0)
            elif cachestartpos:
                cacherefresh = True
            else:
                # print("\n".join(keyframecache.keys()))
                cacherunning = False
        else:
            time.sleep(0.2)
    # print("manager:",closed)


def geterrorsrender(time):
    global keyframes
    global currentframeimg
    global currentwallpaper
    global keyframecache
    i = 0
    frames, cachestr, notimportant, last, success, cacheimg = checkcache(round(time * 60))
    if success:
        currentframeimg = notimportant[0]
        return notimportant[0]

    fillcache(notimportant, frames, cachestr, round(time * 60))
    returnimg = keyframecache[cachestr][1]
    currentframeimg = keyframecache[cachestr][1]
    # print(returnimg)
    return returnimg


def render():
    global keyframes
    if not os.path.exists("./render/"):
        os.makedirs("./render")
    lastframe = keyframes[-1].frame + int(keyframes[-1].window.animationlength * 60)
    for i in range(lastframe):
        geterrorsrender(i / 60).save(f"./render/output{i}.png")


def close():
    global closed
    global timelineroot
    global executor
    global executor2
    global executing
    if closed:
        print("shutting down")
        executor.shutdown(wait=False)
        print("executor 1 shut down")
        executor.shutdown(wait=True, cancel_futures=True)
        # for i in executing:
        #    print("cancelling",i,"result:",i.cancel())
        # print(executing)
        executor2.shutdown(wait=True, cancel_futures=True)
        print("executor 2 shut down")
        timelineroot.destroy()
        pygame.display.quit()
        pygame.quit()
    else:
        timelineroot.after(100, close)


currentdirection = "00"


def updatedirection(a, b, c):
    global directionvar
    global currentdirection
    currentdirection = directionvar.get()[:2]


def selectpreset(thepreset):
    global currentpreset
    currentpreset = thepreset
    print(thepreset)
    updateentries()


def _selectpreset(thepreset):
    return lambda: selectpreset(thepreset)


def resizewithaspect(image, w, h):
    image = image.copy()
    resized = image.resize((int(min(w, h / image.size[1] * image.size[0])), int(min(h, w / image.size[0] * image.size[1]))))
    letterbox = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    letterbox.paste(resized, ((w - resized.size[0]) // 2, (h - resized.size[1]) // 2))
    return letterbox


def updatepresetview():
    global presetbuttons
    global presets
    global presetcanvas
    global presetimages
    for i in presetbuttons:
        i.destroy()
    presetbuttons = []
    for i in range(len(presets)):
        presetimg = resizewithaspect(presets[i].image(), 100, 100)
        # presetimg.show()
        presetimagetk = ImageTk.PhotoImage(presetimg)
        presetimages.append(presetimagetk)
        presetbuttons.append(Button(presetcanvas, bg="#000000", image=presetimagetk, command=_selectpreset(i)))
        presetbuttons[i].grid(row=floor(i / 3), column=i % 3, sticky="news")
    presetcanvas.update_idletasks()
    presetcanvas.config(width=300, height=floor(i / 3 + 1) * 100)
    # print(floor(i/3+1)*100)


def addpreset():
    global entrytext
    global entrytitlevar
    global entrybutton1var
    global entrybutton2var
    global entrybutton3var
    global presets
    global selectedicon
    global selectedos
    global currentcustomimg
    global selectedtimingfunction
    global customclosedurationvar
    global customcloseoriginzvar
    global customcloseoriginyvar
    global customcloseoriginxvar
    global customcloserotationzvar
    global customcloserotationyvar
    global customcloserotationxvar
    global customclosepositionzvar
    global customclosepositionyvar
    global customclosepositionxvar
    presetwindow = Window()
    presetwindow.text = entrytext.get(1.0, END).strip().replace("\\n", "\n")
    presetwindow.title = entrytitlevar.get()
    # print(presets[presetid].buttons)
    presetwindow.buttons = [entrybutton1var.get(), entrybutton2var.get(), entrybutton3var.get()]
    presetwindow.icon = int(selectedicon.get()[0])
    presetwindow.os = OS(selectedos.get())
    presetwindow.startpos = (float(custompositionxvar.get()), float(custompositionyvar.get()), float(custompositionzvar.get()))
    presetwindow.startrotation = (float(customrotationxvar.get()), float(customrotationyvar.get()), float(customrotationzvar.get()))
    presetwindow.origin = (float(customoriginxvar.get()), float(customoriginyvar.get()), float(customoriginzvar.get()))
    presetwindow.animationlength = float(customdurationvar.get())
    presetwindow.endpos = (float(customclosepositionxvar.get()), float(customclosepositionyvar.get()), float(customclosepositionzvar.get()))
    presetwindow.endrotation = (float(customcloserotationxvar.get()), float(customcloserotationyvar.get()), float(customcloserotationzvar.get()))
    presetwindow.endorigin = (float(customcloseoriginxvar.get()), float(customcloseoriginyvar.get()), float(customcloseoriginzvar.get()))
    presetwindow.closeanimationlength = float(customclosedurationvar.get())
    if currentcustomimg:
        presetwindow.imgstr = currentcustomimg
        presetwindow.img = Image.open(currentcustomimg)
    presetwindow.timingfunction = timingfunctions[selectedtimingfunction.get()]
    presetwindow.closetimingfunction = timingfunctions[selectedclosetimingfunction.get()]
    presets.append(presetwindow)
    updatepresetview()


presetbuttons = []
presetimages = []
keyframeview = Keyframeview()

# print(executor)
keyframes = []
currentpreset = 0
presets = [Window(
    text="Setup detected that the operating system in use is not\nWindows 2000 or XP. This setup program and its associated\ndrivers are designed to run only on Windows 2000 or XP. The\ninstallation will be terminated.",
    buttons=["OK", "", ""], os=OS.WINDOWS_7, title="NVIDIA Setup Error"
    )]

directionlist = ["00: 🡾", "10: 🡻", "20: 🡿", "01: 🡺", "11: ⭕", "21: 🡸", "02: 🡽", "12: 🡹", "22: 🡼"]

oslist = [OS.WINDOWS_7.value, OS.XP.value, OS.CUSTOM.value]
oslist = [ops.value for ops in OS]
iconlist = ["0: Critical Error", "1: Exclamation", "2: Information", "3: Question"]
timelineroot = Tk()
timelineroot.title("czeditor")
timelineroot.configure(bg="#1A1A1A")
timelineroot.maxsize(1296, 736)
timelineroot.geometry("1013x141")
timelineroot.resizable(False, False)
timelineroot.attributes('-topmost', True)
timelineroot.protocol("WM_DELETE_WINDOW", dontclose)
# canvas = Image.new("RGBA",(1280,720),(8,8,8))
# canvastk = ImageTk.PhotoImage(canvas)
# czepanel = Label(root, image = canvastk,bd=3,highlightthickness=1,relief="raised",bg="#000000",fg="#AAAAAA",highlightcolor="#111111",activeforeground="#CCCCCC",activebackground="#111111",highlightbackground="#111111")
# czepanel.image = canvastk
# czepanel.place(x=16,y=16)

errorroot = Toplevel()
errorroot.title("error options")
errorroot.geometry("512x684")
errorroot.configure(bg="#1A1A1A")
errorroot.resizable(False, False)
errorroot.attributes('-topmost', True)
errorroot.protocol("WM_DELETE_WINDOW", dontclose)

presetroot = Toplevel()
presetroot.title("presets")
presetroot.geometry("330x200")
presetroot.configure(bg="#1A1A1A", highlightcolor="#1A1A1A", highlightbackground="#1A1A1A")
presetroot.resizable(False, True)
presetroot.attributes('-topmost', True)
presetroot.protocol("WM_DELETE_WINDOW", dontclose)
presetroot.grid_rowconfigure(0, weight=1)
presetroot.columnconfigure(0, weight=1)
# presetroot = Frame(presetroot2)
# presetroot.grid(row=0, column=0, sticky='news')
# presetroot.grid_rowconfigure(0, weight=1)
# presetroot.grid_columnconfigure(0, weight=1)
# presetroot.grid_propagate(False)


presetenclosingcavnas = Canvas(presetroot, bg="#1A1A1A", highlightcolor="#1A1A1A", highlightbackground="#1A1A1A")
presetenclosingcavnas.grid(row=0, column=0, sticky='news')

presetscrollbar = Scrollbar(
    presetroot, orient="vertical", command=presetenclosingcavnas.yview, bg="#000000", activebackground="#000000", highlightcolor="#1A1A1A", highlightbackground="#1A1A1A", troughcolor="#AAAAAA"
    )
presetscrollbar.grid(row=0, column=1, sticky='ns')
presetenclosingcavnas.config(yscrollcommand=presetscrollbar.set)

presetcanvas = Frame(presetenclosingcavnas, bg="#1A1A1A")
presetenclosingcavnas.create_window((0, 0), window=presetcanvas, anchor='nw')

presetscrollbar.config(command=presetenclosingcavnas.yview)
updatepresetview()
# print([[i,presetscrollbar[i]] for i in presetscrollbar.keys()])
presetenclosingcavnas.config(scrollregion=presetenclosingcavnas.bbox("all"))

selectedos = StringVar()
chooseerroros = OptionMenu(errorroot, selectedos, *oslist)
chooseerroros.config(bg="#000000", fg="#AAAAAA", highlightcolor="#111111", activeforeground="#CCCCCC", activebackground="#111111", highlightbackground="#111111")
chooseerroros.grid(row=3, column=0, sticky="we", pady=4, padx=4)
selectedos.set(oslist[0])

directionvar = StringVar()
choosedirection = OptionMenu(timelineroot, directionvar, *directionlist)
choosedirection.config(bg="#000000", fg="#AAAAAA", highlightcolor="#111111", activeforeground="#CCCCCC", activebackground="#111111", highlightbackground="#111111")
choosedirection.place(x=700, y=108)
directionvar.trace("w", updatedirection)
directionvar.set("00: ↘️")

# entrytextvar.trace("w",updatepreset)
entrytext = Text(errorroot, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, height=6, width=60)
entrytext.grid(row=1, column=0, columnspan=9, sticky="we", pady=4, padx=4)
entrytitlevar = StringVar()
# entrytitlevar.trace("w",updatepreset)
entrytitle = Entry(errorroot, textvariable=entrytitlevar, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1)
entrytitle.grid(row=0, column=0, columnspan=9, sticky="we", pady=4, padx=4)

entrybutton1var = StringVar()
# entrybutton1var.trace("w",updatepreset)
entrybutton1 = Entry(errorroot, textvariable=entrybutton1var, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
entrybutton1.grid(row=2, column=1, sticky="we", pady=4, padx=4)
entrybutton2var = StringVar()
# entrybutton2var.trace("w",updatepreset)
entrybutton2 = Entry(errorroot, textvariable=entrybutton2var, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
entrybutton2.grid(row=2, column=2, sticky="we", pady=4, padx=4)
entrybutton3var = StringVar()
# entrybutton3var.trace("w",updatepreset)
entrybutton3 = Entry(errorroot, textvariable=entrybutton3var, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
entrybutton3.grid(row=2, column=3, sticky="we", pady=4, padx=4)

selectedicon = StringVar()
chooseicon = OptionMenu(errorroot, selectedicon, *iconlist)
chooseicon.config(bg="#000000", fg="#AAAAAA", highlightcolor="#111111", activeforeground="#CCCCCC", activebackground="#111111", highlightbackground="#111111")
chooseicon.grid(row=2, column=0, sticky="we", pady=4, padx=4)
# pprint.pprint(chooseicon.config())
addpresetbutton = Button(
    errorroot, text="ADD!", bg="#000000", fg="#AAAAAA", highlightcolor="#111111", activeforeground="#CCCCCC", activebackground="#222222", highlightbackground="#222222", command=addpreset
    )
addpresetbutton.grid(row=4, column=0, sticky="we", pady=4, padx=4)
updatepresetbutton = Button(errorroot, text="update", command=updatepreset, bg="#000000", fg="#AAAAAA")
updatepresetbutton.grid(row=4, column=1, sticky="we", pady=4, padx=4)

customlabel = Label(errorroot, text="custom parameters", bg="#1A1A1A", fg="#AAAAAA")
customlabel.grid(row=5, column=0, pady=4, padx=4)
customposlabel = Label(errorroot, text="start position", bg="#1A1A1A", fg="#AAAAAA")
customposlabel.grid(row=6, column=0, pady=4, padx=4)
custompositionxvar = StringVar()
custompositionx = Entry(errorroot, textvariable=custompositionxvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
custompositionx.grid(row=6, column=1, sticky="we", pady=4, padx=4)
custompositionyvar = StringVar()
custompositiony = Entry(errorroot, textvariable=custompositionyvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
custompositiony.grid(row=6, column=2, sticky="we", pady=4, padx=4)
custompositionzvar = StringVar()
custompositionz = Entry(errorroot, textvariable=custompositionzvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
custompositionz.grid(row=6, column=3, sticky="we", pady=4, padx=4)

customrotlabel = Label(errorroot, text="start rotation", bg="#1A1A1A", fg="#AAAAAA")
customrotlabel.grid(row=7, column=0, pady=4, padx=4)
customrotationxvar = StringVar()
customrotationx = Entry(errorroot, textvariable=customrotationxvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
customrotationx.grid(row=7, column=1, sticky="we", pady=4, padx=4)
customrotationyvar = StringVar()
customrotationy = Entry(errorroot, textvariable=customrotationyvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
customrotationy.grid(row=7, column=2, sticky="we", pady=4, padx=4)
customrotationzvar = StringVar()
customrotationz = Entry(errorroot, textvariable=customrotationzvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
customrotationz.grid(row=7, column=3, sticky="we", pady=4, padx=4)

customorglabel = Label(errorroot, text="start rotation origin", bg="#1A1A1A", fg="#AAAAAA")
customorglabel.grid(row=8, column=0, pady=4, padx=4)
customoriginxvar = StringVar()
customoriginx = Entry(errorroot, textvariable=customoriginxvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
customoriginx.grid(row=8, column=1, sticky="we", pady=4, padx=4)
customoriginyvar = StringVar()
customoriginy = Entry(errorroot, textvariable=customoriginyvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
customoriginy.grid(row=8, column=2, sticky="we", pady=4, padx=4)
customoriginzvar = StringVar()
customoriginz = Entry(errorroot, textvariable=customoriginzvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
customoriginz.grid(row=8, column=3, sticky="we", pady=4, padx=4)

customdurlabel = Label(errorroot, text="animation duration", bg="#1A1A1A", fg="#AAAAAA")
customdurlabel.grid(row=9, column=0, pady=4, padx=4)
customdurationvar = StringVar()
customduration = Entry(errorroot, textvariable=customdurationvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
customduration.grid(row=9, column=1, sticky="we", pady=4, padx=4)

currentcustomimg = ""


def getcustomimage():
    global currentcustomimg
    file = askopenfilename(filetypes=[("PNG image files", ".png")])
    currentcustomimg = file
    # updatepresetview()
    # print(currentcustomimg)


customimagebutton = Button(errorroot, text="browse image", command=getcustomimage, bg="#000000", fg="#FFFFFF", pady="-2p")
customimagebutton.grid(row=10, column=0, sticky="we", pady=4, padx=4)

timingfunctions = {
    "Linear": linear,
    "Windows 7 Cubic Opening": win7bezierapprox,
    "Windows 7 Cubic Closing": win7bezierapproxclose,
    "Cubic ease out": cubiceaseout,
    "Smooth": smooth
}

timingfunctionoptions = ["Linear", "Windows 7 Cubic Opening", "Windows 7 Cubic Closing", "Cubic ease out", "Smooth"]

selectedtimingfunction = StringVar()
choosetimingfunction = OptionMenu(errorroot, selectedtimingfunction, *timingfunctionoptions)
choosetimingfunction.config(bg="#000000", fg="#AAAAAA", highlightcolor="#111111", activeforeground="#CCCCCC", activebackground="#111111", highlightbackground="#111111", width=5)
choosetimingfunction.grid(row=10, column=1, sticky="we", pady=4, padx=4)

customcloseposlabel = Label(errorroot, text="close position", bg="#1A1A1A", fg="#AAAAAA")
customcloseposlabel.grid(row=11, column=0, pady=4, padx=4)
customclosepositionxvar = StringVar()
customclosepositionx = Entry(
    errorroot, textvariable=customclosepositionxvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3
    )
customclosepositionx.grid(row=11, column=1, sticky="we", pady=4, padx=4)
customclosepositionyvar = StringVar()
customclosepositiony = Entry(
    errorroot, textvariable=customclosepositionyvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3
    )
customclosepositiony.grid(row=11, column=2, sticky="we", pady=4, padx=4)
customclosepositionzvar = StringVar()
customclosepositionz = Entry(
    errorroot, textvariable=customclosepositionzvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3
    )
customclosepositionz.grid(row=11, column=3, sticky="we", pady=4, padx=4)

customcloserotlabel = Label(errorroot, text="close rotation", bg="#1A1A1A", fg="#AAAAAA")
customcloserotlabel.grid(row=12, column=0, pady=4, padx=4)
customcloserotationxvar = StringVar()
customcloserotationx = Entry(
    errorroot, textvariable=customcloserotationxvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3
    )
customcloserotationx.grid(row=12, column=1, sticky="we", pady=4, padx=4)
customcloserotationyvar = StringVar()
customcloserotationy = Entry(
    errorroot, textvariable=customcloserotationyvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3
    )
customcloserotationy.grid(row=12, column=2, sticky="we", pady=4, padx=4)
customcloserotationzvar = StringVar()
customcloserotationz = Entry(
    errorroot, textvariable=customcloserotationzvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3
    )
customcloserotationz.grid(row=12, column=3, sticky="we", pady=4, padx=4)

customcloseorglabel = Label(errorroot, text="close rotation origin", bg="#1A1A1A", fg="#AAAAAA")
customcloseorglabel.grid(row=13, column=0, pady=4, padx=4)
customcloseoriginxvar = StringVar()
customcloseoriginx = Entry(errorroot, textvariable=customcloseoriginxvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
customcloseoriginx.grid(row=13, column=1, sticky="we", pady=4, padx=4)
customcloseoriginyvar = StringVar()
customcloseoriginy = Entry(errorroot, textvariable=customcloseoriginyvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
customcloseoriginy.grid(row=13, column=2, sticky="we", pady=4, padx=4)
customcloseoriginzvar = StringVar()
customcloseoriginz = Entry(errorroot, textvariable=customcloseoriginzvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
customcloseoriginz.grid(row=13, column=3, sticky="we", pady=4, padx=4)

customclosedurlabel = Label(errorroot, text="close animation duration", bg="#1A1A1A", fg="#AAAAAA")
customclosedurlabel.grid(row=14, column=0, pady=4, padx=4)
customclosedurationvar = StringVar()
customcloseduration = Entry(errorroot, textvariable=customclosedurationvar, width=6, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1, justify=CENTER, relief="raised", bd=3)
customcloseduration.grid(row=14, column=1, sticky="we", pady=4, padx=4)

selectedclosetimingfunction = StringVar()
chooseclosetimingfunction = OptionMenu(errorroot, selectedclosetimingfunction, *timingfunctionoptions)
chooseclosetimingfunction.config(bg="#000000", fg="#AAAAAA", highlightcolor="#111111", activeforeground="#CCCCCC", activebackground="#111111", highlightbackground="#111111", width=5)
chooseclosetimingfunction.grid(row=15, column=1, sticky="we", pady=4, padx=4)

bigfont = tkfont.Font(family="Helvetica", size="20")
playpausebutton = Button(timelineroot, text="Play/Pause", height=1, width=10, command=play, bg="#000000", fg="#FFFFFF", pady="-2p", font=bigfont)
playpausebutton.place(x=4, y=78 + 6)

midfont = tkfont.Font(family="Helvetica", size="15")
renderbutton = Button(timelineroot, text="Render", height=1, width=10, command=render, bg="#000000", fg="#FFFFFF", pady="-2p", font=midfont)
renderbutton.place(x=178, y=78 + 6)
currentsave = None


def saveas():
    file = asksaveasfilename(filetypes=[("CZE project files", ".cze")])
    if not file.endswith(".cze"):
        file += ".cze"
    currentsave = file
    savekeyframes(file)


def save():
    global currentsave
    if currentsave == None:
        saveas()
    else:
        savekeyframes(currentsave)


def load():
    file = askopenfilename(filetypes=[("CZE project files", ".cze")])
    loadkeyframes(file)


saveasbutton = Button(timelineroot, text="        Save as        ", command=save, bg="#000000", fg="#FFFFFF", pady="-2p")
saveasbutton.place(x=812, y=4)
savebutton = Button(timelineroot, text="Save", height=3, width=8, command=save, bg="#000000", fg="#FFFFFF", pady="-2p", font=midfont)
savebutton.place(x=812, y=29)
loadbutton = Button(timelineroot, text="           load          ", command=load, bg="#000000", fg="#FFFFFF", pady="-2p")
loadbutton.place(x=812, y=113)

savebutton = Button(timelineroot, text="Optimize\ncache", height=5, width=8, command=optimizecache, bg="#000000", fg="#FFFFFF", pady="-2p", font=midfont)
savebutton.place(x=912, y=2)

temposnap = IntVar()
tempocheck = Checkbutton(
    timelineroot, variable=temposnap, text="snap to tempo", bg="#1A1A1A", fg="#AAAAAA", highlightcolor="#111111", activeforeground="#CCCCCC", activebackground="#111111",
    highlightbackground="#111111"
    )
tempocheck.place(x=320 - 12, y=78 + 6)
tempovalue = StringVar()
tempoentry = Entry(timelineroot, textvariable=tempovalue, width=4, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1)
tempoentry.place(x=320 - 12, y=108 + 6)
bpmlabel = Label(timelineroot, text="<- BPM", bg="#1A1A1A", fg="#AAAAAA")
bpmlabel.place(x=320 + 18, y=108 + 6)


def loadaudio():
    global audiopath
    file = askopenfilename(filetypes=[("wav files", ".wav"), ("mp3 files", ".mp3"), ("All files", ".*")])
    audiopath = file
    updatesound()


audiopath = ""
audiobutton = Button(timelineroot, text="Load BGM", command=loadaudio, bg="#000000", fg="#FFFFFF", pady="-2p")
# audiopath.trace("w",updatesound)
audiobutton.place(x=455 - 42, y=78 + 6)


def updatekeyframetype(a, b, c):
    global placekeyframe
    global keyframetypevar
    placekeyframevar.set(f"Place {keyframetypevar.get()} keyframe")
    return


keyframetypes = ["remove"]
keyframetypevar = StringVar()
choosekeyframetype = OptionMenu(timelineroot, keyframetypevar, *keyframetypes)
choosekeyframetype.config(bg="#000000", fg="#AAAAAA", highlightcolor="#111111", activeforeground="#CCCCCC", activebackground="#111111", highlightbackground="#111111")
choosekeyframetype.place(x=554, y=78 + 4)
keyframetypevar.set("remove")
keyframetypevar.trace("w", updatekeyframetype)


def placesecondarykeyframe():
    global keyframetypevar
    createkeyframe(0, 0, keyframetypevar.get())


placekeyframevar = StringVar()
placekeyframe = Button(timelineroot, textvariable=placekeyframevar, command=placesecondarykeyframe, bg="#000000", fg="#FFFFFF", pady="-2p")
placekeyframe.place(x=670, y=78 + 6)
placekeyframevar.set(f"Place {keyframetypevar.get()} keyframe")

placementpreviewimage = Image.new("RGBA", (1280, 720))
placementpreviewtk = ImageTk.PhotoImage(placementpreviewimage)
# czepanel.bind("<Motion>",placementpreview)
# czepanel.bind("<Button-1>",createkeyframe)

timestampvar = StringVar()
timestamplabel = Label(timelineroot, textvariable=timestampvar, bg="#1A1A1A", fg="#AAAAAA")
timestamplabel.place(x=4, y=2)

cascadingvar = StringVar()
cascadinglabel = Label(timelineroot, textvariable=cascadingvar, bg="#1A1A1A", fg="#AAAAAA")
cascadinglabel.place(x=680, y=2)
cascadingvar.set("Cascading distance: 0")


def loadwallpaper():
    global wallpaperpath
    file = askopenfilename(filetypes=[("PNG files", ".png"), ("JPG files", ".jpg,.jpeg"), ("All files", ".*")])
    wallpaperpath = file
    updatewallpaper()


wallpaperpath = ""
wallpaperbutton = Button(timelineroot, text="Load wallpaper", command=loadwallpaper, bg="#000000", fg="#FFFFFF", pady="-2p")
# audiopath.trace("w",updatesound)
wallpaperbutton.place(x=455 - 42, y=112)

snap = 1


def changesnap(event):
    global snapvalue
    global snap
    try:
        snap = min(max(int(snapvalue.get()), 1), 512)
        snapvalue.set(str(snap))
    except:
        snap = 1
        snapvalue.set("1")


snapvalue = StringVar()
snapvalue.set("1")
snapentry = Entry(timelineroot, textvariable=snapvalue, width=4, bg="#000000", fg="#AAAAAA", insertbackground="#CCCCCC", insertwidth=1)
snapentry.place(x=555, y=108 + 6)
snaplabel = Label(timelineroot, text="<- snap distance", bg="#1A1A1A", fg="#AAAAAA")
snaplabel.place(x=555 + 30, y=108 + 6)
snapentry.bind("<FocusOut>", changesnap)

debugvar = StringVar()
debuglabel = Label(timelineroot, textvariable=debugvar, bg="#1A1A1A", fg="#AAAAAA")
debuglabel.place(x=400, y=2)

keyframeviewimage = ImageTk.PhotoImage(keyframeview.image())
keyframepanel = Label(
    timelineroot, image=keyframeviewimage, bd=1, highlightthickness=1, takefocus=True, relief="raised", bg="#1A1A1A", fg="#AAAAAA", highlightcolor="#111111", activeforeground="#CCCCCC",
    activebackground="#111111", highlightbackground="#111111"
    )
keyframepanel.place(x=4, y=16 + 6)
keyframepanel.bind("<Button-1>", keyframeview.button1pressed)
keyframepanel.bind("<Motion>", keyframeview.motion)
keyframepanel.bind("<ButtonRelease-1>", keyframeview.changecursorpos)
keyframepanel.bind("<MouseWheel>", keyframeview.changezoom)
keyframepanel.bind("<Key>", keyboardtk)
keyframepanel.bind("<KeyRelease>", keyboardrelease)
updateentries()
# timelineroot.bind("<Key>",keyboard)
# timelineroot.bind("<MouseWheel>",cascade)
# root.bind("<1>",set_focus)
timelineroot.bind("<1>", set_focus)
errorroot.bind("<1>", set_focus)
# selected.set(presetlist[0])
# czepanel.place(relx=0.5, rely=0.5, anchor=CENTER)
timelineroot.focus()
# root.after(16,playback)
timelineroot.after(30, updatekeyframeviewduringplayback)
timelineroot.after(100, updatevisualization)
executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
executor.submit(cachevisualizationjob)
executor.submit(cacheframesmanager)
executor.submit(playback)
timelineroot.after(100, close)
executor2 = concurrent.futures.ThreadPoolExecutor()
timelineroot.mainloop()
