import re, string, cgi
from cStringIO import StringIO
from image import createImage, createCoverFromImage

'''
Created on May 31, 2011
@author: rhuang

Modified on Feb 8th, 2015
@modifier: mmartinez
#note - I'm heavily modifying this class as I find it unintuitive.
'''

class Html():
    input = None
    ouput = None
    toc = []
    rfcElms = ['Info', 'Title', 'Abstract', 'Toc', 'Content']
    rfc = ''
    title = ''
    leftIndent = 0
    textBlock = None
    imageCount = 1
    prevLine = ''
    hasTOC = False
    orig_lines = []
    preprocessed_lines = []
    def __init__(self, rfc, input, output):
        self.input = input
        self.output = output
        self.rfc = rfc.lower()
        self.info = StringIO()
        
        for line in self.input:
            self.orig_lines.append(line)
            line = cgi.escape(line)
            self.hasTOC = is_toc(line) or self.hasTOC
            self.preprocessed_lines.append(line)
        
        if not self.hasTOC:
           builtTOC = buildTOC(preprocessed_lines)
        
    def writeInfo(self, line):
        if not re.match('^\s*$', line):
            self.info.write(line) 
        elif self.info.tell():
            return getattr(self, "writeTitle")
        return getattr(self, "writeInfo")
    
    def writeTitle(self, line):
        if re.match('^\S.*$', line):
            self.output.write('''
<html>
<head>
<title>%s</title>
<link rel="stylesheet" href="../css/rfc.css" type="text/css" />
</head>
<body>''' % (self.rfc.upper()+" - "+self.title))
            createImage(self.info.getvalue(), '%s/auths.jpg' % (self.rfc))
            createCoverFromImage('%s/auths.jpg' % (self.rfc), '%s/cover.jpg' % (self.rfc))

            self.output.write('<img src="auths.jpg" />')
            self.output.write("<h1>%s</h1>" % (self.title))
            return self.writeAbstract(line)

        if line.lstrip().rstrip():
            self.title = self.title and (self.title + ' ' + line.lstrip().rstrip()) or line.lstrip().rstrip()
          
        return getattr(self, "writeTitle")
    
    def writeAbstract(self, line):
        if isRFCPageBreaker(line):
            return getattr(self, "writeAbstract")
        
        if is_toc(line):
            self.output.write("<mbp:pagebreak/>\n")
            self.output.write('<p><a id="TOC"/><h3>%s</h3></a></p>\n' % (line.rstrip()))
            return getattr(self, "writeTOC")
        
        if re.match(r'^\S.*', line):
            self.output.write('<h2>%s</h2>' % (line))
        else:
            if self.leftIndent == 0: 
                m = re.match(r'^(\s+)\S.*', line)
                if m: 
                    self.leftIndent = len(m.group(1))
            self.output.write(line)
        
        return getattr(self, "writeAbstract")
    
    def writeTOC(self, line):
        if isRFCPageBreaker(line) or re.match('^\s*$', line):
            return getattr(self, "writeTOC")
        
        if re.match(r'^\S.*', line) and not re.search(r'\.{3}', line):
            self.output.write("<mbp:pagebreak/>\n")
            return self.writeContent(line)
        
        m = re.match(r'^\s+([\d.]+)(\s+)([^.]+?)\.+?.*', line)
        if m:
            self.toc.append((m.group(1), m.group(3)))
            lnk = m.group(1)[-1] == '.' and m.group(1)[:-1] or m.group(1)
            self.output.write('<a href="#%s">' % (lnk))
            self.output.write(m.group(1))
            for s in m.group(2):
                self.output.write('&nbsp;')
                
            self.output.write('%s</a><br />\n' % (m.group(3)))
        
        return getattr(self, "writeTOC")
        
    def writeContent(self, line):
        if isRFCPageBreaker(line):
            return getattr(self, "writeContent")
        
        if re.match(r'^\d+\.?\s.*', line):
            m=re.match(r'^(\d+)\.?\s.*', line)
            self.output.write('\n<a id="%s"/><h2>%s</h2></a>\n<p>\n' %( m.group(1), line))
        elif re.match(r'^\s*\d+\.\d+\.?\s.*', line):
            m=re.match(r'^\s*(\d+\.\d+)\.?\s.*', line)
            self.output.write('\n<a id="%s"/><h3>%s</h3></a>\n<p>\n' %( m.group(1), line))
        elif re.match(r'^\s*\d+\.\d+\.\d+\.?\s.*', line):
            m=re.match(r'^\s*(\d+\.\d+\.\d+)\.?\s.*', line)
            self.output.write('\n<a id="%s"/><h4>%s</h4></a>\n<p>\n' %( m.group(1), line))
        elif re.match(r'^\s*\d+\.\d+\.\d+[\d.]+\.?\s.*', line):
            m=re.match(r'^\s*(\d+\.\d+\.\d+[\d.]+)\.?\s.*', line)
            lnk = m.group(1)[-1] == '.' and m.group(1)[:-1] or m.group(1)
            self.output.write('\n<a name="%s"><h5>%s</h5></a>\n<p>\n' %( lnk, line))
        elif re.match(r'^\s*$', line):
            return getattr(self, "newLine")
        elif self.isTextBlockStart(line):
            # detect special lines.
            # sepcial lines require strict line break. figure is one of them.
            self.textBlock = StringIO()
            self.output.write("</p>")
            return self.writeTextBlock(line)
        else:      
            self.output.write(line)
        
        return getattr(self, "writeContent")

    def newLine(self, line):
        if isRFCPageBreaker(line):
            return getattr(self, "pageBreakNewLine")
        
        if not re.match(r'^\s*$', line):
            if re.match(r'^\s*\S.*', line):
                self.output.write("</P>\n<P>\n")
                return self.writeContent(line)
            else:
                return self.writeContent(line)
            
        return getattr(self, "newLine")
    
    def pageBreakNewLine(self, line):
        if isRFCPageBreaker(line):
            return getattr(self, "pageBreakNewLine")
        
        if not re.match(r'^\s*$', line):
            if re.match(r'^\s*[A-Z0-9].*', line):
                self.output.write("</P>\n<P>\n")
                return self.writeContent(line)
            else:
                return self.writeContent(line)
            
        return getattr(self, "pageBreakNewLine")

    def outputTextBlock(self):
	outputlines = self.textBlock.getvalue().splitlines()[:-1]
	if isImageOutput(outputlines):
	    createImage(self.textBlock.getvalue(), "%s/img%d.jpg" % (self.rfc, self.imageCount))
	    self.output.write('<img src="img%d.jpg" />' % (self.imageCount))
	    self.imageCount = self.imageCount + 1
	else:
	    self.output.write("<blockquote> \n")
	    for i in outputlines:
		#if re.match(r'^\s+[A-Z].*', i):
		#    self.output.write("<br />")
		#self.output.write("%s\n" %(re.sub(r"\s", "&nbsp;", i.lstrip())))
		self.output.write("%s\n" %(i))

	    self.output.write("</blockquote> \n")

	self.textBlock.close()
	self.textBlock = None
	self.output.write("<p>\n")

    def writeTextBlock(self, line):
        # rqhuang.... bug here.
        if isRFCPageBreaker(line):
            self.outputTextBlock()
            return getattr(self, "writeContent")
        
        if re.match(r'^\s+Figure\s.*', line):
            self.textBlock.write(line)
            createImage(self.textBlock.getvalue(), "%s/img%d.jpg" % (self.rfc, self.imageCount))
            self.output.write('<img src="img%d.jpg" />' % (self.imageCount))
            self.imageCount = self.imageCount + 1
            self.textBlock.close()
            self.textBlock = None
            self.output.write("<p>\n")
            return getattr(self, "writeContent")
        
        if self.isTextBlockBlockEnd(line):
            self.outputTextBlock()
            return self.writeContent(line)
            
        self.textBlock.write(line)
        return getattr(self, "writeTextBlock")

    def isTextBlockStart(self, line):
        # previous line always empty
        if self.prevLine.lstrip().rstrip():
            return False

        return isTextBlockLine(line, self.leftIndent)
    
    def isTextBlockBlockEnd(self, line):
        return not isTextBlockLine(line, self.leftIndent) and not self.prevLine.lstrip().rstrip()

    def createHTML(self):
        lineProcessor = getattr(self, "write"+self.rfcElms[0])
        for line in self.preprocessed_lines:
            lineProcessor = lineProcessor(line)
            self.prevLine = line
        self.output.write("</body></html>")

def isRFCPageBreaker(line):
    return is_normal_page_number(line) or is_roman_numeral(line) or is_other_formatting(line)

def is_normal_page_number(line):
    return re.match(r'.*\[Page.*\d+?\]', line) 

def is_roman_numeral(line):
    # F'ing Roman numerals...
    return re.match(r'^RFC.*[1-2]\d\d\d', line) 

def is_other_formatting(line):
    return re.match(r'.*\[Page.*M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})?\]', line, re.IGNORECASE)

isFigureLine = lambda i: string.count(i, '---') > 0 or string.count(i, '|') > 1 or string.count(i, '+') > 1 or string.count(i, '>') > 3 or string.count(i, '<') > 3

def isTextBlockLine(line, leftIndent):
    m = re.match(r'^(\s*)\S.*$', line)
    bigindent = m and len(m.group(1)) > leftIndent
    # this is how I detected a text block. It may not be always correct.
    return  re.match(r'^\s*$', line) or bigindent or len(' '.join(line.split())) < len(line.rstrip().lstrip()) - 3 or isFigureLine(line)

def isImageOutput(lines):
    if len(lines) > 50:
    # maximum lines allow for image.
        return False

    for i in lines:
        if isFigureLine(i):
            return True

    return False

def is_toc(line):
    return re.match(r'table of contents', line.lstrip().rstrip().lower())
