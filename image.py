import Image
import ImageDraw
import ImageFont

#textFont=ImageFont.truetype("/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf", 20)
_default_font = ImageFont.truetype('/usr/share/cups/fonts/Courier-Bold', 18)

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
