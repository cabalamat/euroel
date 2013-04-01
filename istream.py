# istream.py

"""
input streams for Python

Class hierarchy;

IStream (ab)
   PeekStream (ab)
      ScanString -- a scannable string

"""

import string

debug = 0

#---------------------------------------------------------------------

DIGITS = "0123456789"
LETTERSU = string.ascii_letters + "_"
IDENTCHARS = LETTERSU + string.digits

def cin(c, s):
    """ is c in s? If c is empty, return False.
    @param c [string] = a character or ''
    @param s [string] = a string; c must match one char in s
    @return [bool]
    """
    if c=='': return False
    return c in s

def isDigit(c):
    return cin(c, DIGITS)

def isLetterU(c):
    return cin(c, LETTERSU)

def isIdentChar(c):
    return cin(c, IDENTCHARS)

#---------------------------------------------------------------------

class IStream:

    #========================================================
    # to be implemented by subclasses:

    def get(self):
        """ Get the next character in the stream
        @return [string] length 1; or '' if EOF
        """
        raise NotImplementedError

    def eof(self):
        """ are we at the end of this stream?
        @return [bool]
        """
        raise NotImplementedError

    #========================================================

    def getChar(self):
        """ alias for get() """
        return self.get()

    def getLine(self):
        """ Get the next line, including '\n' at end
        @return [string]
        """

    def getLines(self):
        """ Get all the lines
        @return [list of string]
        """


    def getAll(self):
        """ Get all the characters in the stream as a string
        @return [string]
        """
        r = ""
        while not self.eof():
            r += self.get()
        return r

    def getChars(self, n =-1):
        """ Get (n) characters in the stream. If n<0, get the lot.
        @return [string]
        """
        if n==-1: return self.getAll()
        r = ""
        for i in range(0, n):
            if self.eof(): return r
            r += self.getChar()
        return r



#---------------------------------------------------------------------

class PeekStream(IStream):

    #========================================================
    # to be implemented by subclasses:

    def peek(self, lookahead=0):
        """ Returns a peek of one char. If lookahead==0, returns the
        next to be written in the stream.
        @param n [int]
        @return [string] length 1; or "" if no more chars
           at relevant position
        """
        raise NotImplementedError

    #========================================================

    def eof(self):
        return self.peek()==''

    def peekChar(self, lookahead=0):
        """ alias for peek() """
        return self.peek(lookahead)

    def peekStr(self, n=1):
        """ Returns a peek of the next (n) chars
        @param n [int]
        @return [string] length n or shorter if no more characters
        """

    def isNext(self, matchStr):
        """ Are the next chars (matchStr)?
        @param matchStr [string]
        @return [bool]
        """
        return self.peekStr(len(matchStr)) == matchStr

    def isNextWord(self, startChars=LETTERSU):
        """ Is what follows a identifier? This defaults to a C-style
        identifier, but other styles can be used
        @param startChars [string] = the chars that a word can start with
           (defaults to those for C identifier)
        @return [bool]
        """
        ch = self.peek()
        r = cin(ch, startChars)
        if debug: print "isNextWord() ch=%r => %r" % (ch, r)
        return r

    def grabToBefore(self, matchStr, skip=False):
        """ Grab a string until the peek is (matchStr).
        @param matchStr [str]
        @param skip [bool] if this is true, skip the (matchStr)
        @return [str]
        """
        s = ""
        while 1:
            if self.isNext(matchStr) or self.eof():
                self.getChars(len(matchStr))
                return s
            s += self.get()
        #//while

    def grabWord(self, startChars=LETTERSU, wordChars=IDENTCHARS):
        """ grab a C-style identifier. Throw away characters until
        we're at the start of one, then greedily grab all of it.
        @param startChars [string] = the chars that a word can start with
           (defaults to those for C identifier)
        @param wordChars [string] = the chars that can appear in the word
           after the 1st char (defaults to those for C identifier)
        @return [string] = the identifier, or '' if couldn't get one
        """
        while 1:
            if self.peek()=='': return ''
            if self.isNextWord(startChars): break
            self.get()
        r = ''
        r = self.get()
        while cin(self.peek(), wordChars):
            r += self.get()
        return r

    def isNextInt(self):
        """ Is what follows an integer? (ie optional '-'
        followed by 1 or more [0-9]
        @return [bool]
        """
        c = self.peek()
        if c=='': return False
        if isDigit(c): return True
        if c=="-" and isDigit(self.peek(1)): return True
        return False

    def grabInt(self, notFound=None):
        """ Scan forward until an int is found, then return it.
        If no int found, return (notFound)
        @return [int]
        """
        while not self.isNextInt():
            c = self.get()
            if c == '': return notFound
        r = self.get()
        while isDigit(self.peek()):
            r += self.get()
        return int(r)


    def isNextSkip(self, matchStr):
        """ Are the next chars (matchStr)? If so, skip them
        and return True.
        @param matchStr [string]
        @return [bool]
        """
        lm = len(matchStr)
        isNext = (self.peekStr(lm) == matchStr)
        if isNext: self.getChars(lm)
        return isNext

    def skipPast(self, s):
        """ Keep consuming characters until the most recently
        consumed are the string (s)
        @param s [string]
        @return [bool] True if skipped any characters
        """
        ls = len(s)
        if ls==0: return False
        while 1:
            if self.isNextSkip(s) or self.eof(): return True
            self.get()

    def skipPastSet(self, chars):
        """ Keep consuming characters until the next char to be read
        isn't in the set (chars),
        skip past it.
        @param chars [string]
        @return [bool] True if skipped any characters
        """
        r = False
        while 1:
            ch = self.peek()
            if ch=='': break
            if ch not in chars: break
            self.get()
            r = True
        return r


#---------------------------------------------------------------------

class ScanString(PeekStream):

    def __init__(self, s):
        self.s = s
        self.at = 0

    #========================================================
    # inherited from superclasses:

    def get(self):
        ch = self.s[self.at:self.at+1]
        self.at += 1
        return ch

    def getChars(self, n=-1):
        if n<0:
            r = self.s[self.at:]
            self.at = len(self.s)
        else:
            ixto = self.at + n
            r = self.s[self.at:ixto]
            self.at += n
            if self.at > len(self.s): self.at = len(self.s)
        return r

    def peek(self, lookahead=0):
        ix = self.at + lookahead
        #print "ScanString s=%r at=%r" % (self.s, self.at)
        return self.s[ix:ix+1]

    def peekStr(self, n=1):
        ixto = self.at + n
        return self.s[self.at:ixto]

    #========================================================

    def getLocation(self):
        """ return where we are in the string.
        NB this function is inefficient as it stands. Lines are
        numbered from 1, columns from 0.
        @return [list of [int,int]] the list is [line,column]
        """
        line = 1
        col = 0
        for ch in self.s[:self.at]:
            if ch=='\n':
                line += 1
                col = 0
            else:
                col += 1
        return [line, col]


#---------------------------------------------------------------------


#end
