from PIL import Image, ImageFont, ImageDraw, ImageMath,ImageChops, ImageOps, ImageFilter
from math import ceil,floor,cos,sin
import numpy as np #this is JUST for the 98/2000 gradient


#_IMAGE = Image.new("RGBA", (200,100), (255,255,255,255))

#  the put() command pastes an image onto a canvas where the given x,y coordinates dictate where the (0,0) point of the image should go.
#  alignment is a 2 character string that holds two numbers ranging from 0 to 2 (inclusive)
#  it dictates what point on the image should be (0,0) and put exactly where the coordinates given say
#
#     "00"--------"10"--------"20"
#      |           |            |
#      |           |            |
#      |           |            |
#     "01"--------"11"--------"21"
#      |           |            |
#      |           |            |
#      |           |            |
#     "02"--------"12"--------"22"
#
#   here is a diagram showing a rectangular image and its alignment points
#   if we chose "11" as the alignment point, it would become the (0,0) of the image. and if the x,y coordinates were width/2,height/2 of the canvas, the image would be put exactly in the center of the canvas
#   this would not work if the alignment point would be "00"
#
#
#     +-----------------------------------CANVAS-----------------------------------+
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                    "00"---IMAGE----+                       |       using "00"(default) as the alignment point
#     |                                     |              |                       |
#     |                                     |              |                       |
#     |                                     |              |                       |
#     |                                     |              |                       |
#     |                                     |              |                       |
#     |                                     +--------------+                       |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     +----------------------------------------------------------------------------+
#
#
#
#
#
#
#     +-----------------------------------CANVAS-----------------------------------+
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                              +----IMAGE-----+                              |
#     |                              |              |                              |
#     |                              |              |                              |
#     |                              |     "11"     |                              |       using "11" as the alignment point
#     |                              |              |                              |
#     |                              |              |                              |
#     |                              +--------------+                              |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     |                                                                            |
#     +----------------------------------------------------------------------------+
#
#     notice how the alignment point stays in the same place on the canvas, but the whole image doesnt.
#
#
def put(canvas, image,a,b,alignment="00"):
    canvas.alpha_composite(image,(int(a)-( image.size[0] * int(alignment[0]) // 2 ),int(b)-( image.size[1] * int(alignment[1]) // 2) ) )
    return canvas
def put7(canvas, image, a, b, alignment = "00"):  #this is the same as put(), but using windows's weird transparency algorithm. ImageRGB+(BackgroundRGB*ImageAlpha).   this assumes that background alpha is 1(fully opaque), i haven't figured out what it does on a transparent background
    x = int(a)-( image.size[0] * int(alignment[0]) // 2 )
    y = int(b)-( image.size[1] * int(alignment[1]) // 2 )
    cr, cg, cb, ca = canvas.crop((x,y,x+w(image),y+h(image))).split()
    ir, ig, ib, ia = image.split()
    r = ImageMath.eval("convert(  c+(b*(255-a)/255) ,'L')",c=ir,b=cr,a=ia)
    g = ImageMath.eval("convert(  c+(b*(255-a)/255) ,'L')",c=ig,b=cg,a=ia)
    b = ImageMath.eval("convert(  c+(b*(255-a)/255) ,'L')",c=ib,b=cb,a=ia)
    canvas.paste(Image.merge("RGBA",(r,g,b,ca)),(x,y))
    return canvas
#def ApplyRules(rules,width,height,
def h(img):  #get the height
    return img.size[1]
def w(img):  #get the width
    return img.size[0]
def cropx(img,a,b):  #crop but only x
    return img.crop((a,0,b,h(img)))
def cropy(img,a,b):  #crop but only y
    return img.crop((0,a,x(img),b))
def gradient(width,height,colora,colorb):
    r = Image.frombytes("L",(width,1),np.uint8(np.linspace(colora[0],colorb[0],width)))
    g = Image.frombytes("L",(width,1),np.uint8(np.linspace(colora[1],colorb[1],width)))
    b = Image.frombytes("L",(width,1),np.uint8(np.linspace(colora[2],colorb[2],width)))
    final = Image.merge("RGB",(r,g,b)).convert("RGBA")
    return final.resize((width,height))
def split(img,n):
    W = w(img)
    H = h(img)
    return [img.crop((0,H/n*i,W,H/n*(i+1))) for i in range(n)]
def take(img,n,i):
    W = w(img)
    H = h(img)
    return img.crop((0,H/n*i,W,H/n*(i+1)))
def createtext(text,fontdirectory,color=(255,255,255,255), buffersize=(3000,3000),underline=False,underlineoffset=0,kerningadjust=0):
    drawntext = Image.new("RGBA",buffersize,(255,127,127,0))
    width = 0
    height = 0
    line = 0
    cursorpos = 0
    newlinesizefile = open(fontdirectory+"newlinesize.txt")
    newlinesize = int(newlinesizefile.read())
    newlinesizefile.close()
    if(underline):
        i = text[0]
        if(i=="\n"):
            height += newlinesize
            line += newlinesize
            cursorpos = 0
        else:
            char = Image.open(fontdirectory+str(ord(i))+".png").convert("RGBA")
            whitechar = Image.open(fontdirectory+"white"+str(ord(i))+".png").convert("RGBA")
            char = put(char, Image.new("RGBA",(w(char),1),(255,255,255,255)),0,h(char)-2+underlineoffset)
            whitechar = put(whitechar, Image.new("RGBA",(w(char),1),(255,255,255,255)),0,h(char)-2+underlineoffset)
            cred, cgreen, wcblue, calpha = char.split()
            wcred, wcgreen, cblue, wcalpha = whitechar.split()
            alpha2 = ImageMath.eval("convert( int( (r1-r2+255+g1-g2+255+b1-b2+255)/3*alp/255 ), 'L')",r1 = cred,r2 = wcred,b1 = cblue,b2 = wcblue,g1 = cgreen,g2 = wcgreen, alp = (color[3]))
            r = Image.new("L",(w(char),h(char)),color[0])
            g = Image.new("L",(w(char),h(char)),color[1])
            b = Image.new("L",(w(char),h(char)),color[2])
            char = Image.merge("RGBA",(r,g,b,alpha2))
            drawntext.paste(char,(cursorpos,line))
            cursorpos +=w(char)+kerningadjust
            width = max(width,cursorpos)
            height = max(height,h(char))
        text = text[1:]
    for i in text:
        if(i=="\n"):
            height += newlinesize
            line += newlinesize
            cursorpos = 0
            continue
        char = Image.open(fontdirectory+str(ord(i))+".png").convert("RGBA")
        whitechar = Image.open(fontdirectory+"white"+str(ord(i))+".png").convert("RGBA")
        cred, cgreen, wcblue, calpha = char.split()
        wcred, wcgreen, cblue, wcalpha = whitechar.split()
        alpha2 = ImageMath.eval("convert( int( (r1-r2+255+g1-g2+255+b1-b2+255)/3*alp/255 ), 'L')",r1 = cred,r2 = wcred,b1 = cblue,b2 = wcblue,g1 = cgreen,g2 = wcgreen, alp = (color[3]))
        r = Image.new("L",(w(char),h(char)),color[0])
        g = Image.new("L",(w(char),h(char)),color[1])
        b = Image.new("L",(w(char),h(char)),color[2])
        char = Image.merge("RGBA",(r,g,b,alpha2))
        drawntext.paste(char,(cursorpos,line))
        cursorpos +=w(char)+kerningadjust
        width = max(width,cursorpos)
        height = max(height,h(char))
    return drawntext.crop((0,0,width,height))
def createtextmac(text,fontdirectory,color=(0,0,0,255), buffersize=(3000,3000),underline=False,underlineoffset=0,kerningadjust=0):
    drawntext = Image.new("RGBA",buffersize,(255,127,127,0))
    width = 0
    height = 0
    line = 0
    cursorpos = 0
    newlinesizefile = open(fontdirectory+"newlinesize.txt")
    newlinesize = int(newlinesizefile.read())
    newlinesizefile.close()
    if(underline):
        i = text[0]
        if(i=="\n"):
            height += newlinesize
            line += newlinesize
            cursorpos = 0
        else:
            char = Image.open(fontdirectory+str(ord(i))+".png").convert("RGBA")
            char = put(char, Image.new("RGBA",(w(char),1),(255,255,255,255)),0,h(char)-2+underlineoffset)
            colorimg = Image.new("RGBA",(w(char),h(char)),(color[0],color[1],color[2],255))
            char = ImageChops.multiply(char,colorimg)
            drawntext.paste(char,(cursorpos,line))
            cursorpos +=w(char)+kerningadjust
            width = max(width,cursorpos)
            height = max(height,h(char))
        text = text[1:]
    for i in text:
        if(i=="\n"):
            height += newlinesize
            line += newlinesize
            cursorpos = 0
            continue
        char = Image.open(fontdirectory+str(ord(i))+".png").convert("RGBA")
        colorimg = Image.new("RGBA",(w(char),h(char)),(color[0],color[1],color[2],255))
        char = ImageChops.multiply(char,colorimg)
        drawntext.paste(char,(cursorpos,line))
        cursorpos +=w(char)+kerningadjust
        width = max(width,cursorpos)
        height = max(height,h(char))
    return drawntext.crop((0,0,width,height))
buffercache = {}
def getfromcache(cache,hash,default):
    if hash in buffercache:
        return buffercache[hash]
    temp = default()
    buffercache[hash] = temp
    return temp
def createtext7(im,x,y,text,fontdirectory,color=(0,0,0,255), buffersize=(3000,3000),align="00", kerningadjust=0, fit=9999999):
    global buffercache
    drawntext = getfromcache(buffercache,str(buffersize)+",0",lambda: Image.new("RGBA",buffersize,(255,255,0,0))).copy()
    whitedrawntext = getfromcache(buffercache,str(buffersize)+",1",lambda: Image.new("RGBA",buffersize,(0,0,255,0))).copy()
    width = 0
    height = 0
    line = 0
    cursorpos = 0
    newlinesizefile = open(fontdirectory+"newlinesize.txt")
    newlinesize = int(newlinesizefile.read())
    newlinesizefile.close()
    for i in text:
        if(i=="\n"):
            height += newlinesize
            line += newlinesize
            cursorpos = 0
            continue
        char = Image.open(fontdirectory+str(ord(i))+".png").convert("RGBA")
        if(cursorpos+w(char)+kerningadjust > fit):
            height += newlinesize
            line += newlinesize
            cursorpos = 0
            continue
        whitechar = Image.open(fontdirectory+"white"+str(ord(i))+".png").convert("RGBA")
        #colorimg = Image.new("RGBA",(w(char),h(char)),(color[0],color[1],color[2],255))
        #char = ImageChops.multiply(char,colorimg)
        drawntext.paste(char,(cursorpos,line))
        whitedrawntext.paste(whitechar,(cursorpos,line))
        cursorpos +=w(char)+kerningadjust
        width = max(width,cursorpos)
        height = max(height,h(char))
    drawntext = drawntext.crop((0,0,width,height))
    drawntext = put(Image.new("RGBA",(w(im),h(im)),(0,0,0,0)),drawntext,x,y,align)
    whitedrawntext = whitedrawntext.crop((0,0,width,height))
    whitedrawntext = put(Image.new("RGBA",(w(im),h(im)),(0,0,0,0)),whitedrawntext,x,y,align)
    imgcolor = Image.new("RGBA",(w(im),h(im)),color)
    c = imgcolor.split()
    ir,ig,ib,ia = im.split()
    r,g,b,a = drawntext.split()
    wr,wg,wb,wa = whitedrawntext.split()
    r = ImageMath.eval("convert( b*c/255+(255-w)*(255-c)/255 ,'L')",w=r,b=wr,c=c[0])
    g = ImageMath.eval("convert( b*c/255+(255-w)*(255-c)/255 ,'L')",w=g,b=wg,c=c[1])
    b = ImageMath.eval("convert( b*c/255+(255-w)*(255-c)/255 ,'L')",w=wb,b=b,c=c[2])
    #imgcolor.show()
    #drawntext.show()
    red = ImageMath.eval("convert( int(((i*(255-t)/255+(c*t)/255)*a/255+i*(255-a)/255)*o/255+(i*(255-o))/255) , 'L')",i=ir,t=r,c=c[0],a=a,o=c[3])   #i is the image RGB,  t is the text RGB,  c is the RGB color variable,  a is the text alpha,  o is the alpha color variable
    #ImageMath.eval("convert( int((255-t)*255/255),'L')",i=ir,t=r,c=c[0]).show()
    green = ImageMath.eval("convert( int(((i*(255-t)/255+(c*t)/255)*a/255+i*(255-a)/255)*o/255+(i*(255-o))/255) , 'L')",i=ig,t=g,c=c[1],a=a,o=c[3])
    blue = ImageMath.eval("convert( int(((i*(255-t)/255+(c*t)/255)*a/255+i*(255-a)/255)*o/255+(i*(255-o))/255) , 'L')",i=ib,t=b,c=c[2],a=a,o=c[3])
    alpha = ImageMath.eval("convert( int(((((r+g+b)/3+(255-(r+g+b)/3)*i/255))*t/255+(i*(255-t))/255)*o/255+(i*(255-o))/255) , 'L')",i=ia,r=r,g=g,b=b,t=a,o=c[3]) #i is the image alpha,  r,g,b are RGB values of the text,  t is text alpha,  o is color alpha
    result = Image.merge("RGBA",(red,green,blue,alpha))
    return result

def measuretext7(text,fontdirectory, buffersize=(3000,3000), kerningadjust=0, fit=9999999): #this gives width and height of text using windows 7 rendering
    #drawntext = Image.new("RGBA",buffersize,(255,127,127,0))
    width = 0
    height = 0
    line = 0
    cursorpos = 0
    newlinesizefile = open(fontdirectory+"newlinesize.txt")
    newlinesize = int(newlinesizefile.read())
    newlinesizefile.close()
    for i in text:
        if(i=="\n"):
            height += newlinesize
            line += newlinesize
            cursorpos = 0
            continue
        char = Image.open(fontdirectory+str(ord(i))+".png").convert("RGBA")
        if(cursorpos+w(char)+kerningadjust > fit):
            height += newlinesize
            line += newlinesize
            cursorpos = 0
            continue
        #colorimg = Image.new("RGBA",(w(char),h(char)),(color[0],color[1],color[2],255))
        #char = ImageChops.multiply(char,colorimg)
        #drawntext.paste(char,(cursorpos,line))
        cursorpos +=w(char)+kerningadjust
        width = max(width,cursorpos)
        height = max(height,h(char))
    return [width,height]

def createtextubuntu(im,x,y,text,fontdirectory,color=(0,0,0,255), buffersize=(3000,3000),align="00"):
    drawntext = Image.new("RGBA",buffersize,(255,255,0,0))
    width = 0
    height = 0
    line = 0
    cursorpos = 0
    newlinesizefile = open(fontdirectory+"newlinesize.txt")
    newlinesize = int(newlinesizefile.read())
    newlinesizefile.close()
    for i in text:
        if(i=="\n"):
            height += newlinesize
            line += newlinesize
            cursorpos = 0
            continue
        char = Image.open(fontdirectory+str(ord(i))+".png").convert("RGBA")
        #colorimg = Image.new("RGBA",(w(char),h(char)),(color[0],color[1],color[2],255))
        #char = ImageChops.multiply(char,colorimg)
        drawntext.paste(char,(cursorpos,line))
        cursorpos +=w(char)
        width = max(width,cursorpos)
        height = max(height,h(char))
    drawntext = drawntext.crop((0,0,width,height))
    drawntext = put(Image.new("RGBA",(w(im),h(im)),(0,0,0,0)),drawntext,x,y,align)
    imgcolor = Image.new("RGBA",(w(im),h(im)),color)
    c = imgcolor.split()
    ir,ig,ib,ia = im.split()
    r,g,b,a = drawntext.split()
    #imgcolor.show()
    red = ImageMath.eval("convert( int(((i*(255-t)/255+(c*t)/255)*a/255+i*(255-a)/255)*o/255+(i*(255-o))/255) , 'L')",i=ir,t=r,c=c[0],a=a,o=c[3])   #i is the image RGB,  t is the text RGB,  c is the RGB color variable,  a is the text alpha,  o is the alpha color variable
    #ImageMath.eval("convert( int((255-t)*255/255),'L')",i=ir,t=r,c=c[0]).show()
    green = ImageMath.eval("convert( int(((i*(255-t)/255+(c*t)/255)*a/255+i*(255-a)/255)*o/255+(i*(255-o))/255) , 'L')",i=ig,t=g,c=c[1],a=a,o=c[3])
    blue = ImageMath.eval("convert( int(((i*(255-t)/255+(c*t)/255)*a/255+i*(255-a)/255)*o/255+(i*(255-o))/255) , 'L')",i=ib,t=b,c=c[2],a=a,o=c[3])
    alpha = ImageMath.eval("convert( int(((((r+g+b)/3+(255-(r+g+b)/3)*i/255))*t/255+(i*(255-t))/255)*o/255+(i*(255-o))/255) , 'L')",i=ia,r=r,g=g,b=b,t=a,o=c[3]) #i is the image alpha,  r,g,b are RGB values of the text,  t is text alpha,  o is color alpha
    result = Image.merge("RGBA",(red,green,blue,alpha))
    return result

def resize(im,width,height,left,right,up,down,scalingmethod=Image.NEAREST):  #this resizes image but keeps margins intact. think of Unity GUI elements
    if width < w(im):
        im = im.resize((width,h(im)),scalingmethod)
        left = 1
        right = 1
    if height < h(im):
        im = im.resize((w(im),height),scalingmethod)
        up = 1
        down = 1
    result = Image.new("RGBA",(width,height),(0,0,0,0))
    tl = im.crop((0,0,left,up))
    tm = im.crop((left,0,w(im)-right,up))
    tr = im.crop((w(im)-right,0,w(im),up))
    ml = im.crop((0,up,left,h(im)-down))
    mm = im.crop((left,up,w(im)-right,h(im)-down))
    mr = im.crop((w(im)-right,up,w(im),h(im)-down))
    dl = im.crop((0,h(im)-down,left,h(im)))
    dm = im.crop((left,h(im)-down,w(im)-right,h(im)))
    dr = im.crop((w(im)-right,h(im)-down,w(im),h(im)))
    result = put(result,tl,0,0)
    result = put(result,tm.resize((width-left-right,h(tm)),scalingmethod),left,0)
    result = put(result,tr,width,0,"20")
    result = put(result,ml.resize((w(ml),height-up-down),scalingmethod),0,up)
    result = put(result,mm.resize((width-left-right,height-up-down),scalingmethod),left,up)
    result = put(result,mr.resize((w(mr),height-up-down),scalingmethod),width,up,"20")
    result = put(result,dl,0,height,"02")
    result = put(result,dm.resize((width-left-right,h(dm)),scalingmethod),left,height,"02")
    result = put(result,dr,width,height,"22")
    return result

def resizeanchor(im,x1,y1,x2,y2,left,right,up,down,scalingmethod=Image.NEAREST):  #this is resize, but you give it desired coordinates and it calculates the size the image should be
    return resize(im,x2-x1,y2-y1,left,right,up,down,scalingmethod)

def tile(im,width,height):    #this tiles an image
    result = Image.new("RGBA",(width,height),(0,0,0,0))
    for x in range(ceil(width/w(im))):
        for y in range(ceil(height/h(im))):
            result = put(result,im,x*w(im),y*h(im))
    return result

#the button functions return an image of a button for the OS.

def CreateXPButton(text,style=0):
    styles = ["xp/Button.png","xp/Button Hovered.png","xp/Button Clicked.png","xp/Button Disabled.png","xp/Button Default.png"]
    Button = Image.open(styles[style]).convert("RGBA")
    col = (0,0,0,255)
    if(style==3):
        col = (161,161,146,255)
    textgraphic = createtext(text,".\\xp\\fonts\\text\\",col)
    Button = resize(Button,max(w(textgraphic)+16,75),max(23,h(textgraphic)+10),8,8,9,9,Image.NEAREST)
    Button = put(Button,textgraphic,w(Button)//2-w(textgraphic)//2,5)
    return Button

def CreateMacButton(text,style=0):
    styles = ["mac/Button.png","mac/Button Disabled.png"]
    Button = Image.open(styles[style]).convert("RGBA")
    col = (0,0,0,255)
    if(style==1):
        col = (161,161,146,255)
        textgraphic = createtextmac(text,".\\mac\\fonts\\caption\\",col)
        Button = resize(Button,max(w(textgraphic)+10,60),max(20,h(textgraphic)+4),2,2,2,2,Image.NEAREST)
    else:
        textgraphic = createtextmac(text,".\\mac\\fonts\\caption\\",col)
        Button = resize(Button,max(w(textgraphic)+10,60),max(20,h(textgraphic)+4),4,4,4,4,Image.NEAREST)
    Button = put(Button,textgraphic,floor(w(Button)/2-w(textgraphic)/2),2)
    return Button

def Create7Button(text,style=0):
    styles = ["7/Button.png","","","7/Button Disabled.png","7/Button Defaulted.png","7/Button Defaulted Animation.png"]
    Button = Image.open(styles[style]).convert("RGBA")
    col = (0,0,0,255)
    #if(style==3):
    #    col = (161,161,146,255)
    #textgraphic = createtext(text,".\\7\\fonts\\text\\",col)
    textsize = measuretext7(text,"7\\fonts\\text\\",kerningadjust=-1)
    Button = resize(Button,max(textsize[0]+16,86),max(24,textsize[1]+9),3,3,3,3,Image.NEAREST)
    Button = createtext7(Button,w(Button)//2-textsize[0]//2,4,text,"7\\fonts\\text\\",kerningadjust=-1)
    return Button

def Create7TaskDialogButton(text,style=0):
    styles = ["7/Button.png","","","7/Button Disabled.png","7/Button Defaulted.png","7/Button Defaulted Animation.png"]
    Button = Image.open(styles[style]).convert("RGBA")
    col = (0,0,0,255)
    #if(style==3):
    #    col = (161,161,146,255)
    #textgraphic = createtext(text,".\\7\\fonts\\text\\",col)
    textsize = measuretext7(text,"7\\fonts\\text\\",kerningadjust=-1)
    Button = resize(Button,max(textsize[0]+30,66),max(21,textsize[1]+6),3,3,3,3,Image.NEAREST)
    Button = createtext7(Button,w(Button)//2-textsize[0]//2,3,text,"7\\fonts\\text\\",kerningadjust=-1)
    return Button

def Create3_1Button(text,style=0,underline=False):
    styles = ["3.1/Button.png","3.1/Button Default.png"]
    Button = Image.open(styles[style]).convert("RGBA")
    textgraphic = createtextmac(text,"3.1//fonts//text//",underline=underline)
    if style == 1:
        Button = resize(Button,max(58,w(textgraphic)+5+5),h(textgraphic)+6+6,4,4,4,4)
        Border = Image.open("3.1//Button Text Outline.png").convert("RGBA")
        BorderImg = tile(Border,max(58,w(textgraphic)+5+5),h(textgraphic)+6+6)
        textx = floor(w(Button)/2-w(textgraphic)/2-1)
        textendx = textx+w(textgraphic)
        Button = put(Button,textgraphic,textx,6,"00")
        Button = put(Button,BorderImg.crop((textx-2,      6,                   textx-1,            7+h(textgraphic))),   textx-2,    6)
        Button = put(Button,BorderImg.crop((textx-1,      7+h(textgraphic),    textendx,           7+h(textgraphic)+1)), textx-1,    7+h(textgraphic))
        Button = put(Button,BorderImg.crop((textendx+1,   6,                   textendx+2,         7+h(textgraphic))),   textendx+1, 6)
        Button = put(Button,BorderImg.crop((textx-1,      5,                   textendx,           6)),                  textx-1,    5)
    else:
        Button = resize(Button,max(58,w(textgraphic)+6+6),h(textgraphic)+6+6,3,3,3,3)
        Button = put(Button,textgraphic,floor(w(Button)/2-w(textgraphic)/2-1),6,"00")
    return Button

def CreateUbuntuButton(text,style=0,predefinedsize=[]):
    styles = ["ubuntu/Button.png","ubuntu/Button Default.png"]
    Button = Image.open(styles[style]).convert("RGBA")
    if predefinedsize:
        size = predefinedsize
    else:
        size = measuretext7(text,"ubuntu/fonts/text/")
        size[0] += 16
        size[1] += 10
        size[0] = max(85,size[0])
        size[1] = max(29,size[1])
    Button = resize(Button,size[0],size[1],5,5,5,5,scalingmethod=Image.BICUBIC)
    Button = createtextubuntu(Button, size[0]//2, size[1]//2, text, "ubuntu/fonts/text/",(60,59,55,255),align="11")
    return Button

def Create95Button(text,style=0,underline=False):
    styles = ["95/Button.png","95/Button Default.png"]
    Button = Image.open(styles[style]).convert("RGBA")
    textgraphic = createtextmac(text,"95//fonts//text//",underline=underline,underlineoffset=1)
    if style == 1:
        Button = resize(Button,max(75,w(textgraphic)+5+5),h(textgraphic)+6+4,3,3,3,3)
        Border = Image.open("95//Button Text Outline.png").convert("RGBA")
        BorderImg = tile(Border,max(75,w(textgraphic)+5+5),h(textgraphic)+6+4)
        textx = floor(w(Button)/2-w(textgraphic)/2)
        outx = 4
        outendx = max(75,w(textgraphic)+5+5)-4
        #BorderImg.show()
        Button = put(Button,textgraphic,textx,4)
        Button = put(Button,BorderImg.crop((outx,      4,                   outx+1,            6+h(textgraphic))),   outx,    4)
        Button = put(Button,BorderImg.crop((outx,      5+h(textgraphic),    outendx,           5+h(textgraphic)+1)), outx,    5+h(textgraphic))
        Button = put(Button,BorderImg.crop((outendx-1,   4,                   outendx,         6+h(textgraphic))),   outendx-1, 4)
        Button = put(Button,BorderImg.crop((outx,      4,                   outendx,           5)),                  outx,    4)
    else:
        Button = resize(Button,max(75,w(textgraphic)+5+5),h(textgraphic)+4+6,2,2,2,2)
        Button = put(Button,textgraphic,floor(w(Button)/2-w(textgraphic)/2),4)
    return Button

def Create2000Button(text,style=0,underline=False):
    styles = ["2000/Button.png","2000/Button Default.png"]
    Button = Image.open(styles[style]).convert("RGBA")
    textgraphic = createtext(text,"xp//fonts//text//",(0,0,0,255),underline=underline,underlineoffset=1)
    if style == 1:
        Button = resize(Button,max(75,w(textgraphic)+5+5),h(textgraphic)+6+4,3,3,3,3)
        Border = Image.open("95//Button Text Outline.png").convert("RGBA")
        BorderImg = tile(Border,max(75,w(textgraphic)+5+5),h(textgraphic)+6+4)
        textx = floor(w(Button)/2-w(textgraphic)/2)
        outx = 4
        outendx = max(75,w(textgraphic)+5+5)-4
        #BorderImg.show()
        Button = put(Button,textgraphic,textx,4)
        Button = put(Button,BorderImg.crop((outx,      4,                   outx+1,            6+h(textgraphic))),   outx,    4)
        Button = put(Button,BorderImg.crop((outx,      5+h(textgraphic),    outendx,           5+h(textgraphic)+1)), outx,    5+h(textgraphic))
        Button = put(Button,BorderImg.crop((outendx-1,   4,                   outendx,         6+h(textgraphic))),   outendx-1, 4)
        Button = put(Button,BorderImg.crop((outx,      4,                   outendx,           5)),                  outx,    4)
    else:
        Button = resize(Button,max(75,w(textgraphic)+5+5),h(textgraphic)+4+6,2,2,2,2)
        Button = put(Button,textgraphic,floor(w(Button)/2-w(textgraphic)/2),4)
    return Button

def CreateXPWindow(width,height,captiontext="",active=True,insideimagepath = "",erroriconpath="",errortext="",button1="",button2="",button3="",button1style=0,button2style=0,button3style=0):

    if active:
        TopFrame = Image.open("xp/Frame Up Active.png").convert("RGBA")
        LeftFrame = Image.open("xp/Frame Left Active.png").convert("RGBA")
        RightFrame = Image.open("xp/Frame Right Active.png").convert("RGBA")
        BottomFrame = Image.open("xp/Frame Bottom Active.png").convert("RGBA")
        CloseButton = Image.open("xp/Close button.png").convert("RGBA")
    else:
        TopFrame = Image.open("xp/Frame Up Inactive.png").convert("RGBA")
        LeftFrame = Image.open("xp/Frame Left Inactive.png").convert("RGBA")
        RightFrame = Image.open("xp/Frame Right Inactive.png").convert("RGBA")
        BottomFrame = Image.open("xp/Frame Bottom Inactive.png").convert("RGBA")
        CloseButton = Image.open("xp/Close button Inactive.png").convert("RGBA")
        button1style = button1style*(button1style != 4)
        button2style = button2style*(button2style != 4) 
        button3style = button3style*(button3style != 4)
    textposx = 15+3
    textposy = 11+h(TopFrame)
    
    captiontextwidth = w(createtext(captiontext,".\\xp\\fonts\\caption\\"))
    width = max(width,captiontextwidth+43)
    createdtext = createtext(errortext,".\\xp\\fonts\\text\\",(0,0,0,255))
    #textposy -= min(15,h(createdtext)//2)
    width = max(width,w(createdtext)+textposx+8+3)
    height = max(height,h(createdtext)+h(TopFrame)+3+25)
    print(textposy)
    if(insideimagepath != ""):
        insideimage = Image.open(insideimagepath).convert("RGBA")
        height = max(h(insideimage)+h(TopFrame)+3,height)
        width = max(width,w(insideimage)+6)
    if(erroriconpath != ""):
        erroricon = Image.open(erroriconpath).convert("RGBA")
        textposx += 15+w(erroricon)
        textposy = max(textposy,11+floor(h(erroricon)/2-h(createdtext)/2)+h(TopFrame))
        height = max(height,h(erroricon)+h(TopFrame)+3+11+11+3)
        width += 14+w(erroricon)
        
    buttonsimage = Image.new("RGBA",(0,0),(0,0,0,0))
    buttonswidth = 0
    buttonsheight = 0
    if button1 != "":
        buttonswidth += 11
        
        button1img = CreateXPButton(button1,button1style)
        #IMAGE = put(IMAGE,button1img,3+12,height-3-12,"02")
        buttonsheight = max(buttonsheight,h(button1img)+14)
        temp = Image.new("RGBA",(buttonswidth+w(button1img),buttonsheight),(0,0,0,0))
        temp = put(temp,buttonsimage,0,0)
        temp = put(temp,button1img,buttonswidth,3)
        buttonsimage = temp.copy()
        buttonswidth += w(button1img)
        if button2 != "":
            buttonswidth += 6
            button2img = CreateXPButton(button2,button2style)
            #IMAGE = put(IMAGE,button2img,3+12,height-3-12,"02")
            buttonsheight = max(buttonsheight,h(button2img)+14)
            temp = Image.new("RGBA",(buttonswidth+w(button2img),buttonsheight),(0,0,0,0))
            temp = put(temp,buttonsimage,0,0)
            temp = put(temp,button2img,buttonswidth,3)
            buttonsimage = temp.copy()
            buttonswidth += w(button2img)
            if button3 != "":
                buttonswidth += 6
                button3img = CreateXPButton(button3,button3style)
                #IMAGE = put(IMAGE,button2img,3+12,height-3-12,"02")
                buttonsheight = max(buttonsheight,h(button3img)+14)
                temp = Image.new("RGBA",(buttonswidth+w(button3img),buttonsheight),(0,0,0,0))
                temp = put(temp,buttonsimage,0,0)
                temp = put(temp,button3img,buttonswidth,3)
                buttonsimage = temp.copy()
                buttonswidth += w(button3img)
        width = max(width,buttonswidth+12)
        height += buttonsheight
    #buttonswidth.show()
    
    width = max(66,width)
    IMAGE = Image.new("RGBA", (width,height), (236,233,216,0))
    #IMAGE = put(IMAGE,cropx(TopFrame,0,27),0,0,"00")
    #IMAGE = put(IMAGE,cropx(TopFrame,28,31).resize((width-w(TopFrame)+4,h(TopFrame)),Image.NEAREST),27,0,"00")
    #IMAGE = put(IMAGE,cropx(TopFrame,31,w(TopFrame)),width,0,"20")
    IMAGE = put(IMAGE,resize(TopFrame,width,h(TopFrame),28,35,9,17,Image.NEAREST),0,0)
    IMAGE = put(IMAGE,LeftFrame.resize((3,height-h(TopFrame)-3),Image.NEAREST),0,h(TopFrame),"00")
    IMAGE = put(IMAGE,RightFrame.resize((3,height-h(TopFrame)-3),Image.NEAREST),width,h(TopFrame),"20")
    IMAGE = put(IMAGE,cropx(BottomFrame,0,5).resize((5,3),Image.NEAREST),0,height,"02")
    IMAGE = put(IMAGE,cropx(BottomFrame,4,w(BottomFrame)-5).resize((width-10,3),Image.NEAREST),5,height,"02")
    IMAGE = put(IMAGE,cropx(BottomFrame,w(BottomFrame)-5,w(BottomFrame)).resize((5,3),Image.NEAREST),width,height,"22")
    IMAGE = put(IMAGE,Image.new("RGBA", (width-6,height-3-h(TopFrame)), (236,233,216,255)),3,h(TopFrame),"00")
    IMAGE = put(IMAGE,CloseButton,width-5,5,"20")
    if active:
        IMAGE = put(IMAGE,createtext(captiontext,".\\xp\\fonts\\captionshadow\\",(10,24,131,255)),8,8,"00")
        IMAGE = put(IMAGE,createtext(captiontext,".\\xp\\fonts\\caption\\"),7,7,"00")
    else:
        IMAGE = put(IMAGE,createtext(captiontext,".\\xp\\fonts\\caption\\",(216,228,248,255)),7,7,"00")
    if(insideimagepath != ""):
        IMAGE = put(IMAGE,insideimage,3,h(TopFrame))
    if(erroriconpath != ""):
        IMAGE = put(IMAGE,erroricon,3+11,h(TopFrame)+11)
    IMAGE = put(IMAGE,createtext(errortext,".\\xp\\fonts\\text\\",(0,0,0,255)),textposx,textposy)
    IMAGE = put(IMAGE,buttonsimage,width//2-5,height-3,"12")
    return IMAGE

def CreateMacAlertDialog(width,height,title="",bar=True,icon="",errortext="",subtext="",button1="",button2="",button3="",button1default=False,button2default=False,button3default=False,button1style=0,button2style=0,button3style=0):
    WindowBar = Image.open("mac/Error Window With bar.png").convert("RGBA")
    WindowNoBar = Image.open("mac/Error Window No bar.png").convert("RGBA")
    Ridges = Image.open("mac/Red Ridges.png").convert("RGBA")
    ButtonBorder = Image.open("mac//Button Outline.png").convert("RGBA")
    TextHeight = 0
    IconPadding = 0
    Paddingwidth = 7
    if(bar):
        Paddingheight = 29+4
        Barheight = 29
    else:
        Paddingheight = 3+4
        Barheight = 0
    if(errortext != ""):
        ErrorTextImg = createtextmac(errortext,"mac//fonts//caption//")
        width = max(width,w(ErrorTextImg)+79+90)
        #height = max(height,h(ErrorTextImg)+Paddingheight+20)
        TextHeight += h(ErrorTextImg)
    if(subtext != ""):
        SubTextImg = createtextmac(subtext,"mac//fonts//text//")
        SubTextPos = TextHeight
        width = max(width,w(SubTextImg)+79+90)
        TextHeight += h(SubTextImg)
    height += TextHeight + Paddingheight
    if(icon != ""):
        IconImg = Image.open(icon).convert("RGBA")
        height = max(height,h(IconImg)+Paddingheight)
        width += w(IconImg)
        IconPadding = w(IconImg)
    buttonswidth = 0
    if(button1 != ""):
        height += 60
        button1img = CreateMacButton(button1,button1style)
        buttonswidth += w(button1img)
        if(button2 != ""):
            button2img = CreateMacButton(button2,button2style)
            buttonswidth += w(button2img)
            if(button3 != ""):
                button3img = CreateMacButton(button3,button3style)
                buttonswidth += w(button3img)
    width = max(width,buttonswidth+79+90)
    IMAGE = Image.new("RGBA", (width,height), (236,233,216,0))
    if(bar):
        IMAGE = put(IMAGE,resize(WindowBar,width,height,3,4,24,4),0,0)
    else:
        IMAGE = put(IMAGE,resize(WindowNoBar,width,height,3,4,3,4),0,0)
    if bar:
        if(title == ""):
            IMAGE = put(IMAGE,resizeanchor(Ridges,5,4,width-6,16,1,1,1,1),5,4)
        else:
            TitleImage = createtextmac(title,"mac//fonts//caption//")
            IMAGE = put(IMAGE,TitleImage,width//2-w(TitleImage)//2,3)
            IMAGE = put(IMAGE,resizeanchor(Ridges,5,4,width//2-w(TitleImage)//2-3,16,1,1,1,1),5,4)
            IMAGE = put(IMAGE,resizeanchor(Ridges,width//2+w(TitleImage)//2+5,4,width-6,16,1,1,1,1),width//2+w(TitleImage)//2+5,4)
    if(icon != ""):
        IMAGE = put(IMAGE,IconImg,26,Barheight+15)
    if(errortext != ""):
        IMAGE = put(IMAGE,ErrorTextImg,47+IconPadding,Barheight+14)
    if(subtext != ""):
        IMAGE = put(IMAGE,SubTextImg,47+IconPadding,Barheight+SubTextPos+16)
    if(button1 != ""):
        button1img = CreateMacButton(button1,button1style)
        IMAGE = put(IMAGE,button1img,width-17,height-17,"22")
        if(button1default):
            button1border = resize(ButtonBorder,w(button1img)+6,h(button1img)+6,5,5,5,5)
            IMAGE = put(IMAGE,button1border,width-17+3,height-17+3,"22")
        if(button2 != ""):
            button2img = CreateMacButton(button2,button2style)
            IMAGE = put(IMAGE,button2img,width-17-w(button1img)-22,height-17,"22")
            if(button2default):
                button2border = resize(ButtonBorder,w(button2img)+6,h(button2img)+6,5,5,5,5)
                IMAGE = put(IMAGE,button2border,width-17+3-w(button1img)-22,height-17+3,"22")
            if(button3 != ""):
                button3img = CreateMacButton(button3,button3style)
                IMAGE = put(IMAGE,button3img,width-17-w(button2img)-22-w(button1img)-22,height-17,"22")
                if(button3default):
                    button3border = resize(ButtonBorder,w(button3img)+6,h(button3img)+6,5,5,5,5)
                    IMAGE = put(IMAGE,button3border,width-17+3-w(button2img)-22-w(button1img)-22,height-17+3,"22")
    return IMAGE

def CreateMacWindow(width,height,title="",icon="",errortext="",button1="",button2="",button3="",button1default=False,button2default=False,button3default=False,button1style=0,button2style=0,button3style=0):
    WindowBar = Image.open("mac/Window With bar.png").convert("RGBA")
    Ridges = Image.open("mac/Ridges.png").convert("RGBA")
    ButtonBorder = Image.open("mac//Button Outline.png").convert("RGBA")
    Paddingheight = 29+4
    TextHeight = 0
    iconsize = 0
    if(icon != ""):
        IconImg = Image.open(icon).convert("RGBA")
        iconsize = w(IconImg)+26
    if(errortext != ""):
        ErrorTextImg = createtextmac(errortext,"mac//fonts//caption//")
        width = max(width,w(ErrorTextImg)+iconsize+20+20)
        #height = max(height,h(ErrorTextImg)+Paddingheight+20)
        TextHeight += h(ErrorTextImg)+36
    #if(subtext != ""):
    #    SubTextImg = createtextmac(subtext,"mac//fonts//text//")
    #    width = max(width,w(SubTextImg)+79+90)
    #    TextHeight += h(SubTextImg)
    height += TextHeight+24+4
    if(button1 != ""):
        height += 17+17
    IMAGE = Image.new("RGBA", (width,height), (236,233,216,0))
    IMAGE = put(IMAGE,resize(WindowBar,width,height,3,4,24,4),0,0)
    if(title == ""):
        IMAGE = put(IMAGE,resizeanchor(Ridges,5,4,width-6,16,1,1,1,1),5,4)
    else:
        TitleImage = createtextmac(title,"mac//fonts//caption//")
        IMAGE = put(IMAGE,TitleImage,width//2-w(TitleImage)//2,3)
        IMAGE = put(IMAGE,resizeanchor(Ridges,5,4,width//2-w(TitleImage)//2-3,16,1,1,1,1),5,4)
        IMAGE = put(IMAGE,resizeanchor(Ridges,width//2+w(TitleImage)//2+5,4,width-6,16,1,1,1,1),width//2+w(TitleImage)//2+5,4)
    if(icon != ""):
        IMAGE = put(IMAGE,IconImg,26,37)
    if(errortext != ""):
        IMAGE = put(IMAGE,ErrorTextImg,iconsize+20,36)
    if(button1 != ""):
        button1img = CreateMacButton(button1,button1style)
        IMAGE = put(IMAGE,button1img,width-17,height-17,"22")
        if(button1default):
            button1border = resize(ButtonBorder,w(button1img)+6,h(button1img)+6,5,5,5,5)
            IMAGE = put(IMAGE,button1border,width-17+3,height-17+3,"22")
        if(button2 != ""):
            button2img = CreateMacButton(button2,button2style)
            IMAGE = put(IMAGE,button2img,width-17-w(button1img)-22,height-17,"22")
            if(button2default):
                button2border = resize(ButtonBorder,w(button2img)+6,h(button2img)+6,5,5,5,5)
                IMAGE = put(IMAGE,button2border,width-17+3-w(button1img)-22,height-17+3,"22")
            if(button3 != ""):
                button3img = CreateMacButton(button3,button3style)
                IMAGE = put(IMAGE,button3img,width-17-w(button2img)-22-w(button1img)-22,height-17,"22")
                if(button3default):
                    button3border = resize(ButtonBorder,w(button3img)+6,h(button3img)+6,5,5,5,5)
                    IMAGE = put(IMAGE,button3border,width-17+3-w(button2img)-22-w(button1img)-22,height-17+3,"22")
    return IMAGE

def CreateMacWindoid(icon="",text="",collapsed=False):
    contentwidth = 0
    contentheight = 0
    textpos = 6
    if(text != ""):
        TextImg = createtextmac(text,"mac//fonts//text//")
        contentwidth += w(TextImg)+7
        contentheight += h(TextImg)+3
    if(icon != ""):
        IconImg = Image.open(icon).convert("RGBA")
        contentwidth += w(IconImg) + 7
        contentheight = max(contentheight,h(IconImg))
        textpos += w(IconImg) + 7
    contentwidth += 12
    contentheight += 8
    CONTENT = Image.new("RGBA",(contentwidth,contentheight),(255,255,198))
    if(text != ""):
        CONTENT = put(CONTENT,TextImg,textpos,5)
    if(icon != ""):
        CONTENT = put(CONTENT,IconImg,6,4)
    Border = Image.open("mac//Windoid.png").convert("RGBA")
    CollapsedBorder = Image.open("mac//Windoid Hidden.png").convert("RGBA")
    Studs = Image.open("mac//Studs.png").convert("RGBA")
    CloseButton = Image.open("mac//Windoid Close Button.png").convert("RGBA")
    HideButton = Image.open("mac//Windoid Hide Button.png").convert("RGBA")
    width = contentwidth + 19
    height = contentheight + 9
    IMAGE = Image.new("RGBA",(width,height),(0,0,0,0))
    if not collapsed:
        IMAGE = put(IMAGE,resize(Border,width,height,14,5,4,5),0,0)
        IMAGE = put(IMAGE,CONTENT,14,4)
        IMAGE = put(IMAGE,CloseButton,2,2)
        IMAGE = put(IMAGE,HideButton,2,height-3,"02")
        IMAGE = put(IMAGE,tile(Studs,8,height-14-15),3,14)
    else:
        IMAGE = put(IMAGE,resize(CollapsedBorder,15,height,2,3,2,3),0,0)
        IMAGE = put(IMAGE,CloseButton,2,2)
        IMAGE = put(IMAGE,HideButton,2,height-3,"02")
        IMAGE = put(IMAGE,tile(Studs,8,height-14-15),3,14)
    return IMAGE

def mix(a,b,c):     #smoothly mixes between two values.
    c = min(1,max(0,c))
    c = c**0.5
    return a*(1-c)+b*c


#this function just takes a corner and squishes it based on width and the height of the image by some amount.
#amount of 3 will put it in the width/3,height/3 position
#amount of 7 will put it in the width/7,height/7 position and so on.
#c is there to animate the translation, from 0 - fully translated, to 1 - no translation
def stretch(size,amount,c):   
    result = size-size*(size/(size-size/amount)) #this is needed because deform() does the opposite of what you would think it will do, it takes 4 points, and then squishes them into a rectangle.
    return mix(result,0,c)




        

def Create7Window(icon="",text="",title="",active=True,buttons=[]):
    #print(time)
    #pos and screenres dictate the glass texture position and size on the window border
    #if wallpaper is not empty, it will composite the error onto an image at pos's coordinates, screenres should be the same size as the wallpaper
    contentwidth = 106
    contentheight = 53
    textpos = 0
    textposy = 25+13
    if(text != ""):
        TextDim = measuretext7(text,"7//fonts//text//",kerningadjust=-1)
        contentwidth = max(contentwidth,TextDim[0]+38+12)
        contentheight += TextDim[1]
        textposy = textposy-min(TextDim[1],21)
    if(icon != ""):
        IconImg = Image.open(icon).convert("RGBA")
        contentwidth = max(contentwidth,w(IconImg)+25+25)
        contentheight = max(contentheight,h(IconImg)+26+26)
        textpos += w(IconImg)-4+25
        textposy += h(IconImg)//2-7
        if(text != ""):
            contentwidth = max(contentwidth,w(IconImg)+25+TextDim[0]+38+9)
    if(title != ""):
        TitleDim = measuretext7(title,"7//fonts//text//",kerningadjust=-1)
        contentwidth = max(contentwidth,TitleDim[0]+49)
    buttonswidth = 0
    #len(buttons)*95
    for i in buttons:
        tempbuttontextsize = measuretext7(i[0],"7/fonts/text/",kerningadjust=-1)
        buttonswidth += max(tempbuttontextsize[0]+16,86) + 10
    if(buttons):
        contentheight += 49
        contentwidth = max(contentwidth,buttonswidth+43)
    CONTENT = Image.new("RGBA",(contentwidth,contentheight),(255,255,255))
    if(icon != ""):
        CONTENT = put(CONTENT,IconImg,25,26)
    if(text != ""):
        CONTENT = createtext7(CONTENT,textpos+12,textposy,text,"7//fonts//text//",kerningadjust=-1)
    if(buttons):
        CONTENT = put(CONTENT, Image.new("RGBA",(contentwidth,49),(240,240,240)),0,contentheight,"02")
    buttonpos = 0
    for i in buttons:
        buttonpos += 10
        Button = Create7Button(i[0],i[1])
        CONTENT = put7(CONTENT, Button, contentwidth-buttonpos,contentheight-12,"22")
        buttonpos += w(Button)
    if active:
        Window = Image.open("7//Window.png")
        CloseButton = Image.open("7//Close Button Single.png")
        SideGlowLeft = Image.open("7//Sideglow 1 Left.png")
        SideShine = Image.open("7//Side Shine.png")
        SideGlowRight = Image.open("7//Sideglow 1 Right.png")
        ShadowTop = Image.open("7//Shadow Top.png")
        ShadowRight = Image.open("7//Shadow Right.png")
        ShadowBottom = Image.open("7//Shadow Bottom.png")
        ShadowLeft = Image.open("7//Shadow Left.png")
    else:
        Window = Image.open("7//Window Inactive.png")
        CloseButton = Image.open("7//Close Button Single Inactive.png")
        SideGlowLeft = Image.open("7//Sideglow 2 Left.png")
        SideShine = Image.open("7//Side Shine Inactive.png")
        SideGlowRight = Image.open("7//Sideglow 2 Right.png")
        ShadowTop = Image.open("7//Shadow Top Inactive.png")
        ShadowRight = Image.open("7//Shadow Right Inactive.png")
        ShadowBottom = Image.open("7//Shadow Bottom Inactive.png")
        ShadowLeft = Image.open("7//Shadow Left Inactive.png")
    CloseSymbol = Image.open("7//Close Symbol.png").convert("RGBA")
    GlassImg = Image.open("7//Glass.png")
    GlassMask = Image.open("7//Glass Mask.png").convert("RGBA")
    TextGlow = Image.open("7//Text Glow.png").convert("RGBA")
    width = contentwidth+8+8
    height = contentheight+8+30
    GlassMask = resize(GlassMask,width,height,8,8,30,8)
    ###Glass = put(Image.new("RGBA",(800,602),(0,0,0,0)),GlassImg.resize(screenres,0),int(-pos[0]+width/16-screenres[0]/16+pos[0]/8),-pos[1])
    
    #WithBorder = ImageChops.multiply(GlassMask)
    WithBorder = Image.new("RGBA",(width,height))
    WithBorder = put(WithBorder, SideGlowLeft, 0, 0)
    WithBorder = put(WithBorder, SideGlowRight, width, 0, "20")
    WithBorder = put(WithBorder, SideShine.resize((w(SideShine),(height-29-8)//4)), 0, 29)
    WithBorder = put(WithBorder, SideShine.resize((w(SideShine),(height-29-8)//4)), width, 29, "20")
    #WithBorder.show()
    if(title != ""):
        WithBorder = put(WithBorder,resize(TextGlow,TitleDim[0]+7+14+10,h(TextGlow),23,23,1,1),-7,0)
        WithBorder = createtext7(WithBorder,8,7,title,"7//fonts//text//",kerningadjust=-1)
    
    WithBorder = put(WithBorder,resize(Window,width,height,8,8,30,8),0,0)
    WithBorder = put(WithBorder,CONTENT,8,30)
    WithBorder = put(WithBorder,CloseButton,width-6,1,"20")
    WithBorder = put(WithBorder,CloseSymbol,width-6-18,5,"20")
    IMAGE = Image.new("RGBA",(width+34,height+34),(0,0,0,0))
    IMAGE = put(IMAGE, resize(ShadowTop,width+34,14,28,28,1,1),0,0)
    IMAGE = put(IMAGE, resize(ShadowLeft,14,height,1,1,17,17),0,14)
    IMAGE = put(IMAGE, resize(ShadowRight,20,height,1,1,17,17),width+14,14)
    IMAGE = put(IMAGE, resize(ShadowBottom,width+34,20,30,29,1,1),0,height+14)
    IMAGE = put(IMAGE,WithBorder,14,14)
    #if not close:
    #    t = min(1,bezierapprox(max(0,min(1,time*4))))
    #    crd = getcrd(t,IMAGE)
    #else:
    #    t = min(1,bezierapproxclose(max(0,min(1,1-time*6))))
    #    crd = getcrdclose(t,IMAGE)
    #coeffs = find_coeffs(crd,[[0,0],[w(IMAGE),0],[w(IMAGE),h(IMAGE)],[0,h(IMAGE)]])
    #IMAGE = IMAGE.transform(IMAGE.size, Image.PERSPECTIVE, coeffs,Image.LINEAR)
    #IMAGE = ImageChops.blend(no,transformed,t)
    
    
#IMAGE = ImageChops.blend(no,transformed,t)
    #GlassMask = GlassMask.transform(GlassMask.size, Image.PERSPECTIVE, coeffs,Image.LINEAR)
    #Blur = wallpaper.filter(ImageFilter.GaussianBlur(radius=12))
    #masked = ImageChops.multiply(put(Image.new("RGBA",wallpaper.size,(0,0,0,0)),GlassMask,pos[0], pos[1],align),Blur)
    #masked = put(masked,IMAGE,pos[0]-14*(1-int(align[0])),pos[1]-14*(1-int(align[1])),align)
    #no = masked.copy()
    #no.putalpha(0)
    #masked = ImageChops.blend(no,masked,t)
        
    return IMAGE,GlassMask

"""def Create7ButtonPanel(buttons,windowwidth=360,screenres=(1920,1080)):
    summedwidth = 11
    summedheight = 20
    curwidth = 0
    curlevel = 0
    cachedbuttons = []
    for button in buttons:
        button = Create7Button(button[0],button[1])
        cachedbuttons.append(button)
        size = button.size
        if(curwidth + size[0] > screenres[0]):
            summedheight += curlevel+2
            curwidth = 0
            curlevel = 0
        curwidth += size[0]
        summedwidth= max(summedwidth,curwidth)
        curlevel = max(curlevel,size[1])
    summedheight += curlevel
    
    for button in cachedbuttons:
        size = button.size""" #tbd
        
def Create7TaskDialog(icon="",textbig="",textsmall="",title="",buttons=[],closebutton=True,active=True,pos=(200,100),screenres=(1920,1080),wallpaper=""):
    width = 360
    height = 0
    iconsize = 0
    if(title != ""):
        TitleDim = measuretext7(title,"7//fonts//text//",kerningadjust=-1)
    if(icon != ""):
        IconImg = Image.open(icon).convert("RGBA")
        iconsize = w(IconImg)+10
        height += iconsize+10
    textbigheight = 0
    if(textbig != ""):
        textbigheight = measuretext7(textbig,"7/fonts/bigtext/",fit=width-iconsize-10-10)[1]+10
        height = max(height,textbigheight+10+30)
    if(textsmall != ""):
        height = max(height,measuretext7(textsmall,"7/fonts/text/",fit=width-iconsize-10-10)[1]+15+15)
    if buttons:
        height += 41
    CONTENT = Image.new("RGBA",(width,height),(255,255,255,255))
    if(icon != ""):
        CONTENT = put(CONTENT,IconImg,10,10)
    
    if(textbig != ""):
        CONTENT = createtext7(CONTENT,iconsize+10,10,textbig,"7/fonts/bigtext/",(0,51,153,255),kerningadjust=-1,fit=width-iconsize-10-10)
    if(textsmall != ""):
        CONTENT = createtext7(CONTENT,iconsize+10,textbigheight+15,textsmall,"7/fonts/text/",kerningadjust=-1,fit=width-iconsize-10-10)
    if buttons:
        CONTENT = put(CONTENT, Image.new("RGBA",(width,40),(240,240,240,255)),0,height,"02")
        CONTENT = put(CONTENT, Image.new("RGBA",(width,1),(222,222,222,255)),0,height-41)
    buttonpos = 12
    for button in buttons:
        ButtonImg = Create7TaskDialogButton(button[0],button[1])
        CONTENT = put(CONTENT, ButtonImg, width-buttonpos,height-11,"22")
        buttonpos += w(ButtonImg)+8



    if active:
        Window = Image.open("7//Window.png")
        CloseButton = Image.open("7//Close Button Single.png")
        SideGlowLeft = Image.open("7//Sideglow 1 Left.png")
        SideShine = Image.open("7//Side Shine.png")
        SideGlowRight = Image.open("7//Sideglow 1 Right.png")
        ShadowTop = Image.open("7//Shadow Top.png")
        ShadowRight = Image.open("7//Shadow Right.png")
        ShadowBottom = Image.open("7//Shadow Bottom.png")
        ShadowLeft = Image.open("7//Shadow Left.png")
    else:
        Window = Image.open("7//Window Inactive.png")
        CloseButton = Image.open("7//Close Button Single Inactive.png")
        SideGlowLeft = Image.open("7//Sideglow 2 Left.png")
        SideShine = Image.open("7//Side Shine Inactive.png")
        SideGlowRight = Image.open("7//Sideglow 2 Right.png")
        ShadowTop = Image.open("7//Shadow Top Inactive.png")
        ShadowRight = Image.open("7//Shadow Right Inactive.png")
        ShadowBottom = Image.open("7//Shadow Bottom Inactive.png")
        ShadowLeft = Image.open("7//Shadow Left Inactive.png")
    CloseSymbol = Image.open("7//Close Symbol.png").convert("RGBA")
    GlassImg = Image.open("7//Glass.png").convert("RGBA")
    GlassMask = Image.open("7//Glass Mask.png").convert("RGBA")
    TextGlow = Image.open("7//Text Glow.png").convert("RGBA")
    
    width = width+8+8
    height = height+8+30
    GlassMask = resize(GlassMask,width,height,8,8,30,8)
    #Glass = put(Image.new("RGBA",(800,602),(0,0,0,0)),GlassImg.resize(screenres),int((width/screenres[0])*50-50-pos[0]+pos[0]*0.12173472694),0)
    Glass = put(Image.new("RGBA",(800,602),(0,0,0,0)),GlassImg.resize(screenres),int(-pos[0]+width/16-screenres[0]/16+pos[0]/8),-pos[1])
    WithBorder = ImageChops.multiply(GlassMask,Glass)
    WithBorder = put(WithBorder, SideGlowLeft, 0, 0)
    WithBorder = put(WithBorder, SideGlowRight, width, 0, "20")
    WithBorder = put(WithBorder, SideShine.resize((w(SideShine),(height-29-8)//4)), 0, 29)
    WithBorder = put(WithBorder, SideShine.resize((w(SideShine),(height-29-8)//4)), width, 29, "20")
    #WithBorder.show()
    if(title != ""):
        WithBorder = put(WithBorder,resize(TextGlow,TitleDim[0]+7+14+10,h(TextGlow),23,23,1,1),-7,0)
        WithBorder = createtext7(WithBorder,8,7,title,"7//fonts//text//",kerningadjust=-1)
    
    WithBorder = put(WithBorder,resize(Window,width,height,8,8,30,8),0,0)
    WithBorder = put(WithBorder,CONTENT,8,30)
    if closebutton:
        WithBorder = put(WithBorder,CloseButton,width-6,1,"20")
        WithBorder = put(WithBorder,CloseSymbol,width-6-18,5,"20")
    
    IMAGE = Image.new("RGBA",(width+19+13,height+18+12),(0,0,0,0))
    IMAGE = put(IMAGE, resize(ShadowTop,width+13+16,12,26,26,1,1),0,0)
    IMAGE = put(IMAGE, resize(ShadowLeft,13,height,1,1,20,14),0,12)
    IMAGE = put(IMAGE, resize(ShadowRight,19,height,1,1,20,14),width+13,12)
    IMAGE = put(IMAGE, resize(ShadowBottom,width+13+17,18,28,27,1,1),0,height+12)
    IMAGE = put(IMAGE,WithBorder,13,12)
    if(wallpaper != ""):
        WallpaperImg = Image.open(wallpaper).convert("RGBA")
        IMAGE = put(WallpaperImg, IMAGE, pos[0]-13, pos[1]-12)
    return IMAGE

#def Export7Animation(img,savepath):  #just put the generated window into img and set savepath to the folder you want it to save  "7//animoutput//" is recommended
#    for i in range(16):
#        ImageChops.multiply(ImageOps.deform(img, Windows7Anim(i/60)),Image.new("RGBA",(w(img),h(img)),(255,255,255,int(max(0,min(1,(i+0.1)/15))**0.5*255)))).save(savepath+str(i)+".png")
def even(a):
    c = ceil(a/2)*2
    dc = abs(c-a)
    f = floor(a/2)*2
    df = abs(f-a)
    if(df <= dc):
        return f
    else:
        return c
def buttoneven(a):
    c = ceil(a/2)*2
    dc = abs(c-a)
    f = floor(a/2)*2
    df = abs(f-a)
    if(df < dc):
        return f
    else:
        return c
def getsafe(a, i, fallback):
    try:
        return a[i]
    except IndexError:
        return fallback
def Create3_1Window(icon="",text="",title="",buttons=[],active=True):
    contentwidth = 0
    contentheight = 0
    textpos = 18
    textposy = 16
    iconposy = 17
    if(text != ""):
        TextImg = createtextmac(text,"3.1//fonts//text//")
        contentwidth += w(TextImg)+18+17
        contentheight += h(TextImg)+16+16
    if(icon != ""):
        IconImg = Image.open(icon).convert("RGBA")
        textpos += w(IconImg)+19
        contentwidth += w(IconImg)+18
        contentwidth = max(contentwidth,w(IconImg)+19+19)
        contentheight = max(contentheight,17+h(IconImg)+15)
        if(text != ""):
            textposy = max(16,h(IconImg)//2-h(TextImg)//2+17)
    if(title != ""):
        TitleImg = createtextmac(text,"3.1//fonts//text//")
        contentwidth = max(contentwidth,w(TitleImg)+20+1)
    if buttons:
        contentheight += 44
    buttonswidth = 0
    for button in buttons:
        CurrentButton = Create3_1Button(button[0],button[1],getsafe(button,2,False))
        buttonswidth += w(CurrentButton)+17
    contentwidth = max(contentwidth,buttonswidth+17)
    contentwidth = even(contentwidth)
    if active:
        Window = Image.open("3.1//Window.png").convert("RGBA")
    else:
        Window = Image.open("3.1//Window Inactive.png").convert("RGBA")
    CloseButton = Image.open("3.1//Close Button.png").convert("RGBA")
    CONTENT = Image.new("RGBA",(contentwidth,contentheight),(255,255,255,255))
    if(text != ""):
        CONTENT = put(CONTENT,TextImg,even(textpos),even(textposy))
        if(icon != ""):
            iconposy = even(textposy+h(TextImg)/2-h(IconImg)/2)
    if(icon != ""):
        CONTENT = put(CONTENT,IconImg,18,iconposy)
    buttonpos = contentwidth/2-(58*len(buttons)+17*len(buttons)-17)/2
    if active:
        for i in range(len(buttons)):
            CONTENT = put(CONTENT,Create3_1Button(buttons[i][0],buttons[i][1],getsafe(buttons[i],2,False)),buttoneven(buttonpos),contentheight-10,"02")
            buttonpos += 58+17
    else:
        for i in range(len(buttons)):
            CONTENT = put(CONTENT,Create3_1Button(buttons[i][0],0,getsafe(buttons[i],2,False)),buttoneven(buttonpos),contentheight-10,"02")
            buttonpos += 58+17
    width = contentwidth+5+5
    height = contentheight+24+5
    IMAGE = resize(Window,width,height,6,6,24,5)
    IMAGE = put(IMAGE,CONTENT,5,24)
    IMAGE = put(IMAGE, CloseButton,6,5)
    if(title != ""):
        if active:
            TitleImg = createtextmac(title,"3.1//fonts//text//",(255,255,255,255))
        else:
            TitleImg = createtextmac(title,"3.1//fonts//text//")
        IMAGE = put(IMAGE,TitleImg,floor((contentwidth-20-1)/2-w(TitleImg)/2)+19+6,6)
    return IMAGE
    #

def CreateUbuntuWindow(icon="",bigtext="",text="",title="",buttons=[],active=True):
    contentwidth = 12+12+12
    contentheight = 12+16+24
    textwidth = 0
    textheight = 0
    if(bigtext != ""):
        bigtextsize = measuretext7(bigtext,"ubuntu/fonts/bigtext/")
        textwidth += bigtextsize[0]
        textheight += bigtextsize[1]+12
    if(text != ""):
        textsize = measuretext7(text,"ubuntu/fonts/text/")
        textwidth = max(textwidth,textsize[0])
        textheight += textsize[1]
    else:
        textheight += 17
    contentwidth += textwidth
    contentheight = max(contentheight,textheight+12+24+16)
    if(icon != ""):
        IconImg = Image.open(icon).convert("RGBA")
        contentwidth += w(IconImg)
        contentheight = max(contentheight,h(IconImg)+12+24+16)
    maxbuttonwidth = 0
    maxbuttonheight = 0
    for button in buttons:
        ButtonImg = CreateUbuntuButton(button[0],button[1])
        maxbuttonwidth = max(w(ButtonImg),maxbuttonwidth)
        maxbuttonheight = max(h(ButtonImg),maxbuttonheight)
    contentwidth = max(contentwidth, (maxbuttonwidth+4+4)*len(buttons)+8+8)
    contentheight += maxbuttonheight
    CONTENT = Image.new("RGBA",(contentwidth,contentheight),(240,235,226))
    iconsize = 0
    if(icon != ""):
        CONTENT = put(CONTENT,IconImg,12,12)
        iconsize = w(IconImg)
    if(bigtext == ""):
        if(text != ""):
            CONTENT = createtextubuntu(CONTENT,iconsize+24,12,text,"ubuntu/fonts/text/",(60,59,55,255))
    else:
        CONTENT = createtextubuntu(CONTENT,iconsize+24,12,bigtext,"ubuntu/fonts/bigtext/",(60,59,55,255))
        if(text != ""):
            CONTENT = createtextubuntu(CONTENT,iconsize+24,bigtextsize[1]+12+12,text,"ubuntu/fonts/text/",(60,59,55,255))
    buttonpos = contentwidth-12
    for button in buttons:
        CONTENT = put(CONTENT, CreateUbuntuButton(button[0],active and button[1] or 0,[maxbuttonwidth,maxbuttonheight]),buttonpos,contentheight-16,"22")
        buttonpos -= maxbuttonwidth+8
    
    Frame = Image.open(active and "ubuntu/Window.png" or (not active and "ubuntu/Window Inactive.png")).convert("RGBA")
    CloseButton = Image.open(active and "ubuntu/Close Button.png" or (not active and "ubuntu/Close Button Inactive.png")).convert("RGBA")
    Mask = Image.open("ubuntu/Mask.png").convert("RGBA")
    Highlight = Image.open("ubuntu/Highlight.png").convert("RGBA")
    Mask = resize(Mask,contentwidth,contentheight,5,5,1,4)  
    WINDOW = resize(Frame,contentwidth+1+1,contentheight+27+1,5,5,27,5)
    WINDOW = put(WINDOW, ImageChops.multiply(Mask,CONTENT), 1, 27)
    WINDOW = put(WINDOW, CloseButton, 10, 5)
    WINDOW = put(WINDOW, Highlight,0,27)
    WINDOW = put(WINDOW, Highlight,contentwidth+1,27)
    if(title != ""):
        WINDOW = createtextubuntu(WINDOW, 42, 6, title, "ubuntu/fonts/caption/", (51,51,51,255))
        WINDOW = createtextubuntu(WINDOW, 42, 4, title, "ubuntu/fonts/caption/", (51,51,51,255))
        WINDOW = createtextubuntu(WINDOW, 41, 5, title, "ubuntu/fonts/caption/", (51,51,51,255))
        WINDOW = createtextubuntu(WINDOW, 43, 5, title, "ubuntu/fonts/caption/", (51,51,51,255))
        WINDOW = createtextubuntu(WINDOW, 42, 5, title, "ubuntu/fonts/caption/", (223,216,200,255))
    Shadow = Image.open("ubuntu/Shadow.png").convert("RGBA")
    IMAGE = resize(Shadow,contentwidth+1+1+8+10,contentheight+27+1+8+10,20,20,21,21)
    IMAGE = put(IMAGE,WINDOW,8,8)
    return IMAGE
def betterround(a):
    if(a%1 < 0.5):
        return floor(a)
    else:
        return ceil(a)

def Create95Window(icon="",text="",title="",buttons=[],active=True,closebutton=True):
    width = 0
    height = 0
    textshift = 0
    iconheight = 32
    if(icon):
        IconImg = Image.open(icon).convert("RGBA")
        width += w(IconImg)+12+12
        height = max(height,h(IconImg)+12+6)
        textshift += w(IconImg)+10
        iconheight = h(IconImg)
    if(text):
        TextImg = createtextmac(text,"95/fonts/text/")
        width = max(width,w(TextImg)+textshift+18+11)
        height =max(height,h(TextImg)+12+6)
    #print(buttons)
    buttons = buttons.copy()
    if(buttons):
        button = buttons[0]
        ButtonsImg = Image.new("RGBA",(1,1),(0,0,0,0))
        ButtonImg = Create95Button(button[0],getsafe(button,1,0) if active else 0,getsafe(button,2,False))
        ButtonsImg = put(Image.new("RGBA",(w(ButtonsImg)+w(ButtonImg),max(h(ButtonsImg),h(ButtonImg))),(0,0,0,0)),ButtonsImg,0,0)
        ButtonsImg = put(ButtonsImg,ButtonImg,w(ButtonsImg),0,"20")
        buttons.pop(0)
        for button in buttons:
            ButtonImg = Create95Button(button[0],getsafe(button,1,0) if active else 0,getsafe(button,2,False))
            ButtonsImg = put(Image.new("RGBA",(w(ButtonsImg)+w(ButtonImg)+6,max(h(ButtonsImg),h(ButtonImg))),(0,0,0,0)),ButtonsImg,0,0)
            ButtonsImg = put(ButtonsImg,ButtonImg,w(ButtonsImg),0,"20")
        width = max(width,w(ButtonsImg)+12+12)
        height += h(ButtonsImg)+12+11
        buttons.append("good")
    #width = 262
    #height = 96
    IMAGE = Image.new("RGBA",(width,height),(192,192,192,255))
    if(icon):
        IMAGE = put(IMAGE,IconImg,12,12)
    if(text):

        IMAGE = put(IMAGE,TextImg,18+textshift,21 if h(TextImg) == 13 else 16 if h(TextImg) == 26 else 12 )
    if(buttons):
        IMAGE = put(IMAGE, ButtonsImg,floor(width/2-w(ButtonsImg)/2)+1,height-12,"02")
    if active:
        Window = Image.open("95/Window.png").convert("RGBA")
    else:
        Window = Image.open("95/Window Inactive.png").convert("RGBA")
    if closebutton:
        CloseButton = Image.open("95/Close Button.png").convert("RGBA")
    else:
        CloseButton = Image.open("95/Close Button Disabled.png").convert("RGBA")
    IMAGE = put(resize(Window,width+2+2,height+21+2,3,3,21,2),IMAGE,2,21)
    if(title):
        TitleImg = createtextmac(title,"95/fonts/caption/",(255,255,255) if active else (192,192,192))
        IMAGE = put(IMAGE,TitleImg,5,5)
    print(IMAGE.size)
    IMAGE = put(IMAGE,CloseButton,width-1,5,"20")
    return IMAGE
def Create98Window(icon="",text="",title="",buttons=[],active=True,closebutton=True,gradient1active=(0,0,128),gradient2active=(16,132,208),gradient1inactive=(128,128,128),gradient2inactive=(181,181,181)):
    width = 0
    height = 0
    textshift = 0
    iconheight = 32
    if(icon):
        IconImg = Image.open(icon).convert("RGBA")
        width += w(IconImg)+12+12
        height = max(height,h(IconImg)+12+6)
        textshift += w(IconImg)+10
        iconheight = h(IconImg)
    if(text):
        TextImg = createtextmac(text,"95/fonts/text/")
        width = max(width,w(TextImg)+textshift+18+11)
        height = max(height,h(TextImg)+12+6)
    if(buttons):
        button = buttons[0]
        ButtonsImg = Image.new("RGBA",(1,1),(0,0,0,0))
        ButtonImg = Create95Button(button[0],getsafe(button,1,0) if active else 0,getsafe(button,2,False))
        ButtonsImg = put(Image.new("RGBA",(w(ButtonsImg)+w(ButtonImg),max(h(ButtonsImg),h(ButtonImg))),(0,0,0,0)),ButtonsImg,0,0)
        ButtonsImg = put(ButtonsImg,ButtonImg,w(ButtonsImg),0,"20")
        buttons.pop(0)
        for button in buttons:
            ButtonImg = Create95Button(button[0],getsafe(button,1,0) if active else 0,getsafe(button,2,False))
            ButtonsImg = put(Image.new("RGBA",(w(ButtonsImg)+w(ButtonImg)+6,max(h(ButtonsImg),h(ButtonImg))),(0,0,0,0)),ButtonsImg,0,0)
            ButtonsImg = put(ButtonsImg,ButtonImg,w(ButtonsImg),0,"20")
        width = max(width,w(ButtonsImg)+12+12)
        height += h(ButtonsImg)+12+11
        buttons.append("good")
    #width = 262
    #height = 96
    IMAGE = Image.new("RGBA",(width,height),(192,192,192,255))
    if(icon):
        IMAGE = put(IMAGE,IconImg,12,12)
    if(text):

        IMAGE = put(IMAGE,TextImg,18+textshift,21 if h(TextImg) == 13 else 16 if h(TextImg) == 26 else 12 )
    if(buttons):
        #print(width/2-w(ButtonsImg)/2+1)
        #print(floor(width/2-w(ButtonsImg)/2)+1)
        IMAGE = put(IMAGE, ButtonsImg,floor(width/2-w(ButtonsImg)/2)+1,height-12,"02")
    if active:
        Window = Image.open("95/Window.png").convert("RGBA")
    else:
        Window = Image.open("95/Window Inactive.png").convert("RGBA")
    if closebutton:
        CloseButton = Image.open("95/Close Button.png").convert("RGBA")
    else:
        CloseButton = Image.open("95/Close Button Disabled.png").convert("RGBA")
    IMAGE = put(resize(Window,width+2+2,height+21+2,3,3,21,2),IMAGE,2,21)
    if active:
        IMAGE = put(IMAGE,Image.new("RGBA",(width-2,18),gradient2active),3,3)
        IMAGE = put(IMAGE,gradient(width-2-19,18,gradient1active,gradient2active),3,3)
    else:
        IMAGE = put(IMAGE,Image.new("RGBA",(width-2,18),gradient2inactive),3,3)
        IMAGE = put(IMAGE,gradient(width-2-19,18,gradient1inactive,gradient2inactive),3,3)
    if(title):
        TitleImg = createtextmac(title,"95/fonts/caption/",(255,255,255) if active else (192,192,192))
        IMAGE = put(IMAGE,TitleImg,5,5)
    #print(IMAGE.size)
    IMAGE = put(IMAGE,CloseButton,width-1,5,"20")
    return IMAGE
def Create2000Window(icon="",text="",title="",buttons=[],active=True,closebutton=True):
    width = 0
    height = 0
    textshift = 0
    iconheight = 32
    if(icon):
        IconImg = Image.open(icon).convert("RGBA")
        width += w(IconImg)+12+12
        height = max(height,h(IconImg)+12+6)
        textshift += w(IconImg)+10
        iconheight = h(IconImg)
    if(text):
        TextImg = createtext(text,"xp/fonts/text/",(0,0,0,255))
        width = max(width,w(TextImg)+textshift+18+11)
        height = max(height,h(TextImg)+12+6)
    if(buttons):
        button = buttons[0]
        ButtonsImg = Image.new("RGBA",(1,1),(0,0,0,0))
        ButtonImg = Create2000Button(button[0],getsafe(button,1,0) if active else 0,getsafe(button,2,False))
        ButtonsImg = put(Image.new("RGBA",(w(ButtonsImg)+w(ButtonImg),max(h(ButtonsImg),h(ButtonImg))),(0,0,0,0)),ButtonsImg,0,0)
        ButtonsImg = put(ButtonsImg,ButtonImg,w(ButtonsImg),0,"20")
        buttons.pop(0)
        for button in buttons:
            ButtonImg = Create2000Button(button[0],getsafe(button,1,0) if active else 0,getsafe(button,2,False))
            ButtonsImg = put(Image.new("RGBA",(w(ButtonsImg)+w(ButtonImg)+6,max(h(ButtonsImg),h(ButtonImg))),(0,0,0,0)),ButtonsImg,0,0)
            ButtonsImg = put(ButtonsImg,ButtonImg,w(ButtonsImg),0,"20")
        width = max(width,w(ButtonsImg)+12+12)
        height += h(ButtonsImg)+12+11
        buttons.append("good")
    #width = 262
    #height = 96
    IMAGE = Image.new("RGBA",(width,height),(212,208,200,255))
    if(icon):
        IMAGE = put(IMAGE,IconImg,12,12)
    if(text):

        IMAGE = put(IMAGE,TextImg,18+textshift,21 if h(TextImg) == 13 else 16 if h(TextImg) == 26 else 12 )
    if(buttons):
        #print(width/2-w(ButtonsImg)/2+1)
        #print(floor(width/2-w(ButtonsImg)/2)+1)
        IMAGE = put(IMAGE, ButtonsImg,floor(width/2-w(ButtonsImg)/2)+1,height-12,"02")
    if active:
        Window = Image.open("2000/Window.png").convert("RGBA")
    else:
        Window = Image.open("2000/Window Inactive.png").convert("RGBA")
    if closebutton:
        CloseButton = Image.open("2000/Close Button.png").convert("RGBA")
    else:
        CloseButton = Image.open("2000/Close Button Disabled.png").convert("RGBA")
    IMAGE = put(resize(Window,width+2+2,height+21+2,3,3,21,2),IMAGE,2,21)
    if active:
        IMAGE = put(IMAGE,Image.new("RGBA",(width-2,18),(166,202,240)),3,3)
        IMAGE = put(IMAGE,gradient(width-2-19,18,(10,36,106),(166,202,240)),3,3)
    else:
        IMAGE = put(IMAGE,Image.new("RGBA",(width-2,18),(192,192,192)),3,3)
        IMAGE = put(IMAGE,gradient(width-2-19,18,(128,128,128),(192,192,192)),3,3)
    if(title):
        TitleImg = createtext(title,"xp/fonts/text/",(255,255,255,255) if active else (212,208,200,255),kerningadjust=1)
        IMAGE = put(IMAGE,TitleImg,5,5)
        IMAGE = put(IMAGE,TitleImg,6,5)
    #print(IMAGE.size)
    IMAGE = put(IMAGE,CloseButton,width-1,5,"20")
    return IMAGE

def FrameXPWindow(image,title,active=True,close=1,maximize=1,minimize=1,question=0):
    if (maximize-1)&3 == 3:
        if active:
            TopFrame = Image.open("xp/Frame Up Active.png").convert("RGBA")
            LeftFrame = Image.open("xp/Frame Left Active Unresizable.png").convert("RGBA")
            RightFrame = Image.open("xp/Frame Right Active Unresizable.png").convert("RGBA")
            BottomFrame = Image.open("xp/Frame Bottom Active Unresizable.png").convert("RGBA")
        else:
            TopFrame = Image.open("xp/Frame Up Inactive.png").convert("RGBA")
            LeftFrame = Image.open("xp/Frame Left Inactive Unresizable.png").convert("RGBA")
            RightFrame = Image.open("xp/Frame Right Inactive Unresizable.png").convert("RGBA")
            BottomFrame = Image.open("xp/Frame Bottom Inactive Unresizable.png").convert("RGBA")
    else:
        if active:
            TopFrame = Image.open("xp/Frame Up Active.png").convert("RGBA")
            LeftFrame = Image.open("xp/Frame Left Active.png").convert("RGBA")
            RightFrame = Image.open("xp/Frame Right Active.png").convert("RGBA")
            BottomFrame = Image.open("xp/Frame Bottom Active.png").convert("RGBA")
        else:
            TopFrame = Image.open("xp/Frame Up Inactive.png").convert("RGBA")
            LeftFrame = Image.open("xp/Frame Left Inactive.png").convert("RGBA")
            RightFrame = Image.open("xp/Frame Right Inactive.png").convert("RGBA")
            BottomFrame = Image.open("xp/Frame Bottom Inactive.png").convert("RGBA")
    CONTENT = Image.open(image).convert("RGBA")
    width = w(CONTENT)+w(RightFrame)+w(LeftFrame)
    height = h(CONTENT)+h(TopFrame)+h(BottomFrame)
    IMAGE = Image.new("RGBA", (width,height), (0,0,0,0))
    IMAGE = put(IMAGE,resize(TopFrame,width,h(TopFrame),28,35,9,17,Image.NEAREST),0,0)
    IMAGE = put(IMAGE,LeftFrame.resize((w(LeftFrame),height-h(TopFrame)-3),Image.NEAREST),0,h(TopFrame),"00")
    IMAGE = put(IMAGE,RightFrame.resize((w(RightFrame),height-h(TopFrame)-3),Image.NEAREST),width,h(TopFrame),"20")
    IMAGE = put(IMAGE,cropx(BottomFrame,0,5),0,height,"02")
    IMAGE = put(IMAGE,cropx(BottomFrame,4,w(BottomFrame)-5).resize((width-10,h(BottomFrame)),Image.NEAREST),5,height,"02")
    IMAGE = put(IMAGE,cropx(BottomFrame,w(BottomFrame)-5,w(BottomFrame)),width,height,"22")
    IMAGE = put(IMAGE,CONTENT,w(LeftFrame),h(TopFrame),"00")
    buttonsoffset = 0
    if(close != 0):
        Buttons = Image.open("xp/Close Buttons.png").convert("RGBA")
        IMAGE = put(IMAGE,take(Buttons,8,close-1+4*(not active)),width-5-buttonsoffset,5,"20")
        buttonsoffset += w(Buttons)+2
    if(maximize != 0):
        Buttons = Image.open("xp/Maximize Buttons.png").convert("RGBA")
        IMAGE = put(IMAGE,take(Buttons,8,maximize-1+4*(not active)),width-5-buttonsoffset,5,"20")
        buttonsoffset += w(Buttons)+2
    if(minimize != 0):
        Buttons = Image.open("xp/Minimize Buttons.png").convert("RGBA")
        IMAGE = put(IMAGE,take(Buttons,8,minimize-1+4*(not active)),width-5-buttonsoffset,5,"20")
        buttonsoffset += w(Buttons)+2
    if(question != 0):
        Buttons = Image.open("xp/Help Buttons.png").convert("RGBA")
        IMAGE = put(IMAGE,take(Buttons,8,question-1+4*(not active)),width-5-buttonsoffset,5,"20")
        buttonsoffset += w(Buttons)+2
    if title:
        if active:
            IMAGE = put(IMAGE,createtext(title,".\\xp\\fonts\\captionshadow\\",(10,24,131,255)),8,8,"00")
            IMAGE = put(IMAGE,createtext(title,".\\xp\\fonts\\caption\\"),7,7,"00")
        else:
            IMAGE = put(IMAGE,createtext(title,".\\xp\\fonts\\caption\\",(216,228,248,255)),7,7,"00")
    return IMAGE
# Example XP windows:
#o = CreateXPWindow(0,0,"Notepad",errortext="The text in the Untitled file has changed.\n\nDo you want to save the changes?",button1="Yes",button2="No",button3="Cancel",button1style=4)

#o = CreateXPWindow(0,0,"Notepad",erroriconpath="xp\\Exclamation.png",errortext="The text in the Untitled file has changed.\n\nDo you want to save the changes?",button1="Yes",button1style=4)

#o = CreateXPWindow(0,0,"Notepad",erroriconpath="xp\\Exclamation.png",errortext="The text in the Untitled file has changed.\n\nDo you want to save the changes?")

#o = CreateXPWindow(0,0,"Notepad",errortext="The text in the Untitled file has changed.\n\nDo you want to save the changes?")

#o = CreateXPWindow(0,0,"LOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONG",errortext="short",button1="OK",button1style=4)

#o = CreateXPWindow(0,0,"Notepad",erroriconpath="xp\\Exclamation.png",errortext="The text in the Untitled file has changed.\n\nDo you want to save the changes?",button1="Yes",button2="No",button3="Cancel",button1style=4)

# Example 7 windows:
#o = Create7Window(icon="7\\Question Mark.png",text="text",title="title",buttons=[["Cancel",0],["No",0],["Yes",4]])
#o = Create7Window(icon="7\\Question Mark.png",text="text",title="title",buttons=[["Cancel",0],["No",0],["Yes",4]],wallpaper="7\\wallpaper.png",pos=(400,400))

#o = CreateXPWindow(0,0,captiontext="Question",erroriconpath="xp\\Question.png",errortext="Multiple buttons with different styles\nAnd showing off the multiline capabilities\n.\n.\n.\n.",button1="OK",button1style=4,button2="Cancel",button3="This button is disabled and long\nand has a double line!",button3style=3)

#o = Create7Window(icon="7\\Critical Error.png",text="Example error.",buttons=[["OK",4],["Disabled button",3]])

#o = CreateXPWindow(0,0,captiontext="Error",erroriconpath="xp\\Exclamation.png",errortext="This error has no buttons")
#CreateMacAlertDialog(width,height,title="",bar=True,icon="",errortext="",subtext="",button1="",button2="",button3="",button1default=False,button2default=False,button3default=False,button1style=0,button2style=0,button3style=0)
#CreateMacWindoid(icon="",text="",collapsed=False):
#o = CreateMacWindow(0,0,title="Window",icon="mac//Speech Bubble.png",errortext="Mac OS 9 error",button1="OK",button1default=True)
#o = CreateMacWindoid(icon="mac//Speech Bubble Small.png",text="This is a Mac Windoid     qwertyuiopasdfghjklzxcvbnm\n---------------------------\n---------------------------")

#o = Create3_1Window(icon="3.1//Exclamation.png",text="Cannot read drive a:.\n\nPlease verify the drive door is closed and that \nthe disk is formatted and free of errors.",title="Save As",buttons=[["Retry",1,True],["Cancel",0]])
#o = Create3_1Window(icon="3.1//Exclamation.png",text="The text in the (Untitled) file has changed.\n\nDo you want to save the changes?",title="Notepad",buttons=[["Yes",1,True],["No",0,True],["Cancel",0]])
#o = Create3_1Window(icon="3.1//Exclamation.png",text="(Untitled)\nThe image has changed.\n\nDo you want to save current changes?",title="Paintbrush",buttons=[["Yes",1,True],["No",0,True],["Cancel",0]])
#o = Create3_1Window(text="You must be running mail with security enabled",title="Microsoft At Work Fax",buttons=[["OK",1]])
#o = Create3_1Window(text="The selected COM port is either not supported or is \nbeing used by another device.\n\nSelect another port",title="Terminal - Error",buttons=[["OK",1]])
#o = Create3_1Window(icon="3.1//Information.png",text="Now 1.459854% more accurate!",title="The Create3_1Window function",buttons=[["OK",1]])
#o = Create7Window(text="Error with no icon and buttons",title="Window title")
#o = Create3_1Window(icon="3.1//Question Mark.png",text="The component that you want to install requires \nMicrosoft Windows Network.\n\nDo you want to install Microsoft Workgroup \nNetwork now?",title="Remote Access",buttons=[["Yes",1,True],["No",0,True]],active=False)
#o = CreateUbuntuWindow(icon="ubuntu/Error.png",bigtext="Big text",text="Small text",title="title(dont use this)",buttons=[["OK",1],["Cancel",0]])
#
#
#o = Create7TaskDialog(icon="7/Exclamation.png",textbig="An error has occured",textsmall="That's all we know.",buttons=[["Close",4],["Help",0]],title="Windows",closebutton=False)
#o=CreateMacWindow(0,0,icon="mac/Exclamation.png",errortext="This is named 'errortext'",button1="guh")
#o = CreateXPWindow(0,0,captiontext="Windows",erroriconpath="xp\\Exclamation.png",errortext="An error has occured.",button1="Cancel",button2="Retry",button3="Debug",button2style=4)
#Export7Animation(o,"7//animoutput//")
#o = Create3_1Window(icon="3.1//Exclamation.png",text="cos",title="gfdgdf",buttons=[["Yes",1,True],["No",0,True],["Cancel",0]])
#o = Create95Window(icon="95/Exclamation.png",text="Save changes to Document?",title="WordPad",buttons=[["Yes",1,True],["No",0,True],["Cancel",0]])
#o = Create95Window(icon="95/Exclamation.png",text="The file C:\\WINDOWS\\SYSTEM\\Krnl386.exe contains no icons.\n\nChoose an icon from the list or specify a different file.",title="Change Icon",buttons=[["OK",1]],closebutton=False)
#o = Create95Window(icon="95/Exclamation.png",text="The file C:\\New Shortcut.lnk cannot be found.",title="Create Shortcut",buttons=[["OK",1]],closebutton=False,active=True)
#o = Create95Window(icon="95/Exclamation.png",text="Setup has finished configuring your system.\n\nYou must restart your computer before the new settings will take \neffect.\n\nClick OK to restart your computer now.",buttons=[["OK",1]],closebutton=False,active=True,title="Windows 95 Setup")
#o = Create95Window(icon="95/Critical Error.png",text="Please insert the disk labeled 'Windows 95 Disk1', and then click \nOK.",buttons=[["OK",1]],closebutton=False,active=True,title="Insert Disk")
#o = Create95Window(icon="95/Information.png",text="You must provide computer and workgroup names that will identify \nthis computer on the network.",buttons=[["OK",1]],closebutton=False,active=True,title="Network")
#o = Create95Window(icon="95/Critical Error.png",text="G:\\\n\nA device attached to the system is not functioning.",title="G:\\",buttons=[["OK",1]],closebutton=False,active=True)
#o = Create95Button(text="Yes",underline=True,style=1)
#o = Create3_1Button("OK",0)
#o = Create98Window(icon="95/Exclamation.png",text="Look how fancy",title="amazing",buttons=[["OK",1]],closebutton=False,gradient1active=(181,60,10),gradient2active=(230,154,40))
#o = FrameXPWindow(image="output - Copy.png",title="how cool",maximize=4)
#o = Create7Window(icon="7\\Question Mark.png",text="text",title="title",buttons=[["Cancel",0],["No",0],["Yes",4]],wallpaper="tempdesktop.png",pos=(400,400))
#o.show()
#o.save("output.png")







