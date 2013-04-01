# entity.py


from htmlhelp import li
import area

#---------------------------------------------------------------------
""" An entity is something (such as a Party, Region/Aggregation, or
Article) that has a web page for itself, and wihch has attributes (such
as links to a website or Wikipedia article).

The possible attributes are:

logo [str] logo for a party or entity
col [str] color
wp [str] URL of wikipedia article
web [str] URL of website
tw [str]  URL of twitter
rss [str] URL of RSS feed
mani [list pf str] previous manifestos a party has
standsIn [list of str] list of area abbreviations
aff [str|list of str] affiliation. what europarty or EP group a party belongs to.
"""

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

def getHtmlForAff(aff):
    """ If the affiliation is a valid article name, link to it. Otherwise
    keep it as straight text.
    @param aff [str] an affiliation
    @return [str] containing html
    """
    import article
    abWouldBe = article.abForName(aff)
    if article.articles.has_key(abWouldBe):
        h = article.articles[abWouldBe].getA()
    else:
        h = aff
    return h


class Entity:

    def html(self):
        h = "<h1>%s</h1>\n\n" % (self.name,)
        h += self.htmlAttributes()
        h += self.desc
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
                  % (logoUrl, self.name))
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


    def getAttr(self, k, default=None):
        """
        @param k [str] the attribute's key
        @param default what is returned if it doesn't exist
        """
        if self.__dict__.has_key(k):
            return self.__dict__[k]
        else:
            return default

    def setAttrs(self, **kwargs):
        self.__dict__.update(kwargs)

#---------------------------------------------------------------------


#end