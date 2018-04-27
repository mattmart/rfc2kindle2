from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

#textFont=ImageFont.truetype("/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf", 20)
#_default_font = ImageFont.truetype('/Library/Fonts/Courier New Bold.ttf', 18)
_default_font = ImageFont.truetype('/usr/share/fonts/dejavu/DejaVuSans.ttf',20)

class RFCImage():
    def __init__(self, width, height, filename):
        self.im = Image.new ( "1", (width, height), 0xffff )
        self.draw = ImageDraw.Draw ( self.im )
        self.filename = filename
        self.line = 0

    def drawLine(self, text):
        global _default_font
        self.draw.text( (0,0+self.line*18), text, font=_default_font)
        self.line = self.line+1
        
    def save(self):
        self.im.save ( self.filename )
    

def createImage(text, filename):
    lines = text.splitlines()
    # Remove empty trailing lines.
    for i in range(len(lines)-1, 0, -1):
        if lines[i].lstrip().rstrip():
             break
        else: 
             lines.pop()

    leftSpacing = min(len(li) == 0 and 100 or len(li) - len(li.lstrip()) for li in lines)
    height= len(lines) * 18
    width=(max(len(n.rstrip()) for n in lines) - leftSpacing) * 11
    rfcImg = RFCImage(width, height, filename)
    for f in lines:
        rfcImg.drawLine(f[leftSpacing:])
        #rfcImg.drawLine(f)

    rfcImg.save()

# Turn the authors page into a .mobi compliant cover (at least 500x800 px)
def createCoverFromImage(srcFilename, destFilename):
    print("Generating cover from ", srcFilename, "...")
    origImg = Image.open(srcFilename)

    imgSize = list(origImg.size)
    imgOffset = [0,0]
    if imgSize[0] < 500:
        imgOffset[0] = (500 - imgSize[0]) // 2
        imgSize[0] = 500
    if imgSize[1] < 800:
        imgOffset[1] = (800 - imgSize[1]) // 2
        imgSize[1] = 800

    coverImg = Image.new('RGB',tuple(imgSize),(255,255,255))
    coverImg.paste(origImg,tuple(imgOffset))
    coverImg.save(destFilename)
    #TODO convert the following print stmt
    #print("Cover", destFilename, "generated (%s x %s px) from %s (%s x %s px)." % (destFilename, imgSize[0], imgSize[1], srcFilename, origImg.size[0], origImg.size[1])

if __name__ == "__main__":
    figure='''
                     atlanta.com  . . . biloxi.com
                 .      proxy              proxy     .
               .                                       .
       Alice's  . . . . . . . . . . . . . . . . . . . .  Bob's
      softphone                                        SIP Phone
         |                |                |                |
         |    INVITE F1   |                |                |
         |--------------->|    INVITE F2   |                |
         |  100 Trying F3 |--------------->|    INVITE F4   |
         |<---------------|  100 Trying F5 |--------------->|
         |                |<-------------- | 180 Ringing F6 |
         |                | 180 Ringing F7 |<---------------|
         | 180 Ringing F8 |<---------------|     200 OK F9  |
         |<---------------|    200 OK F10  |<---------------|
         |    200 OK F11  |<---------------|                |
         |<---------------|                |                |
         |                       ACK F12                    |
         |------------------------------------------------->|
         |                   Media Session                  |
         |<================================================>|
         |                       BYE F13                    |
         |<-------------------------------------------------|
         |                     200 OK F14                   |
         |------------------------------------------------->|
         |                                                  |

         Figure 1: SIP session setup example with SIP trapezoid
'''
    createImage(figure, 'mytext.jpg')
    createCover(figure, 'mytext-cover.jpg')
