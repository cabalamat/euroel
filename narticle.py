# narticle.py = new article

"""
See <NEW_ARTICLE_FORMAT> for description.


"""

import os, string, re

import butil
import istream
import htmlhelp
from htmlhelp import li

import area

articles = {}

#---------------------------------------------------------------------
# functions for module

def idForTitle(s):
    """ put a string into a form suitable for a partial url
    @param s [str]
    @return [str]
    """
    result = ""
    for char in s:
        if (char in string.ascii_letters
            or char in string.digits):
            result += char.lower()
        elif ((char==" " or char=="_" or char=="-")
              and result[-1:]!="_"):
            result += "_"
    return result

def manifestoNameFromFn(fn):
    """ decide what to call the manifesto, based on the filename
    @param fn [str]
    @return [str] the name of the manifesto
    """
    mffn = [("2009euro", "2009 European"),
            ("2010ge", "2010 general"),
            ("2011scot", "2011 Scottish Parliament"),
            ("2011wales", "2011 Welsh Assembly"),
            ("2012london", "2012 London Assembly"),
            ("2011ni", "2011 Northern Ireland Assembly"),]
    for pfn, name in mffn:
        if pfn in fn: return name
    return fn

#---------------------------------------------------------------------

class NArticle:

    def __init__(self, id, title):
        self.id = id
        self.title = title

        # default values:
        self.col = "fff"
        self.desc = ""


    def getAttr(self, k, default=None):
        """
        @param k [str] the attribute's key
        @param default what is returned if it doesn't exist
        """
        if self.__dict__.has_key(k):
            return self.__dict__[k]
        else:
            return default

    def getA(self):
        return "<a href='%s'>%s</a>" % (self.getUrl(), self.title)

    def getUrl(self):
        return "/narticle/%s" % (self.id,)

    def setAttrs(self, **kwargs):
        self.__dict__.update(kwargs)

    #========== write HTML ==========


    def html(self):
        h = "<h1>%s</h1>\n\n" % (self.title,)
        h += self.htmlAttributes()
        desc =  self.getAttr('desc')
        if desc:
            h += "<h2>Description</h2>\n\n" + desc
        return h

    def htmlAttributes(self):
        """ return html for various attributes, such as
        colour, wikipedia url, etc.
        """
        h = ""

        logo  = self.getAttr('logo')
        if logo:
            if logo[:7]=="http://":
                logoUrl = logo
            else:
                logoUrl = "/static/logo/" + logo
            h += ("<div class='logo'><img src='%s' alt='%s logo'></div>"
                  % (logoUrl, self.title))
        h += "<ul>\n"

        col = self.getAttr('col', "fff")
        if col!="fff":
            h += (("<li>Colour: <span style='"
                   "background-color:#%s; width:50px; height:16px;'"
                   ">&nbsp; &nbsp; &nbsp;</span></li>\n\n") % col)

        wp = self.getAttr('wp')
        if wp:
            h += li("<a href='%s'>Wikipedia article</a>"%wp)

        web = self.getAttr('web')
        if web:
            h += li("<a href='%s'>Website</a>"%web)

        tw = self.getAttr('tw')
        if tw:
            h += li("<a href='%s'>Twitter</a>"%tw)

        h += self.htmlManifestos()

        standsIn = self.getAttr('standsIn')
        if standsIn:
            areaHtml = ", ".join([area.areas[aab].nameInUrl()
                                  for aab in standsIn])
            h += li("Intends to stand in " + areaHtml)

        aff = self.getAttr('aff')
        if aff:
            h += self.htmlAff(aff)

        h += "</ul>\n"
        return h

    def htmlManifestos(self):
        h = ""
        mani = self.getAttr('mani')
        if not mani: return ""
        h = "<li>Manifestos:</li>\n<ul>\n"
        for fn in mani:
            h += ("<li><a href='/static/manifesto/%s'>%s</a></li>" %
                  (fn, manifestoNameFromFn(fn)))
        #//for
        h += "</ul>\n"
        return h

    def htmlAff(self, affs):
        """ return html for the affiliations of this organisation """
        if isinstance(affs, str): affs = [affs]
        h = "<li>Affiliation: "
        for aff in affs:
            h += getHtmlForAff(aff) + ", "
        h = h[:-2]
        h += "</li>"
        return h

    def leftBarHtml(self):
        return ""

    #==========

#---------------------------------------------------------------------
# load all articles

globalAttributes = ""

def mwLink(s):
    """ convert mediwiki-like links into markdown ones, e.g.:
    [[Credits]] -> [credits](/article/credits)
    """
    def replaceFun(matchOb):
        g = matchOb.group(1)
        inner = g[2:-2]
        ab = abForName(inner)
        r = "[%s](/article/%s)" % (inner, ab)
        return r
    s2 = re.sub(r"(\[\[.*?\]\])", replaceFun, s)
    return s2

def getValuesDesc(body):
    ss = istream.ScanString(body)
    ss.skipPast("<<")
    values = ss.grabToBefore(">>", skip=True)
    desc = ss.getChars()
    return values, desc

def processGlobal(body):
    global globalAttributes
    globalAttributes, _ = getValuesDesc(body)

def processArticle(title, body):
    """ process an article
    @param title [str]
    @param body [str]
    """
    if not title: return
    if title == "GLOBAL":
        processGlobal(body)
        return
    #print "Process article $$$$$ %s" % (title,)
    id = idForTitle(title)
    article = NArticle(id, title)
    values, desc = getValuesDesc(body)
    article.desc = htmlhelp.md(mwLink(desc).decode('utf-8'))
    if globalAttributes:
        exec "article.setAttrs(" + globalAttributes + ")"
    exec "article.setAttrs(" + values + ")"
    articles[id] = article
    #print "%s" % (articles,)

def readArticles(arts):
    """ Read some articles
    @param arts [str] containing one or more articles
    """
    a = arts.split("\n")
    title = None
    body = ""
    for line in a:
        if line.startswith("$$$$$"):
            processArticle(title, body)
            body = ""
            title = line[5:].strip()
        else:
            body += line + "\n"
    #//for
    processArticle(title, body)

def loadArticles():
    """ load articles from the euro election top-level directory """
    #print "loadArticles()"
    topDir = "/home/phil/proj/euroelection/articles"
    allFns = os.listdir(topDir)
    artFns = [fn
              for fn in allFns
              if fn.endswith(".art")]
    #print "loadArticles() artFns=%r" % (artFns,)
    for artFn in artFns:
        artPn = topDir+"/"+artFn
        #print "loading articles in <%s>..." % (artPn,)
        artFStr = butil.readFile(topDir+"/"+artFn)
        readArticles(artFStr)
    #//for

#---------------------------------------------------------------------

loadArticles()

#end