# article.py

"""
Articles are a way that I can quickly write static web pages. Articles
are written in markdown and appear in a url of the form:

    /article/name_of_article

Articles are written in files with the extension .art. Each file contains
one or more articles. Each article contains a title (one line) followed
by the article. The title is of the form:

   $$$$$ The Name
"""

import string, re, os

import butil
import htmlhelp
import entity

articles = {}

#---------------------------------------------------------------------

class Article(entity.Entity):

    def __init__(self, ab, name):
        self.ab = ab
        self.name = name
        self.body = ""

    def __str__(self):
        s = "$$$$$ %s\n%s\n" % (name, body)
        return s

    def __repr__(self):
        return "Article(%r, %r)" % (self.ab, self.name)

    def getA(self):
        return "<a href='%s'>%s</a>" % (self.getUrl(), self.name)

    def getUrl(self):
        return "/article/%s" % (self.ab,)


#---------------------------------------------------------------------

def abForName(s):
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

def processArticle(title, body):
    """ process an article
    @param title [str]
    @param body [str]
    """
    if not title: return
    #print "Process article $$$$$ %s" % (title,)
    ab = abForName(title)
    article = Article(ab, title)
    article.desc = htmlhelp.md(mwLink(body).decode('utf-8'))
    articles[ab] = article
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
    topDir = "/home/phil/proj/euroelection"
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

def getLeftBarFor(artDir):
    abList = artDir.keys()
    abList.sort()
    h = "<h3>Articles</h3>\n\n"
    h += "<br>\n".join(["&#9656; " + artDir[ab].getA()
                        for ab in abList])
    return h

#---------------------------------------------------------------------

# load all articles:
loadArticles()
leftBarHtml = getLeftBarFor(articles)

#---------------------------------------------------------------------
# add attributes

def seta(ab, **kwargs):
    ab = abForName(ab)
    if articles.has_key(ab):
        articles[ab].setAttrs(**kwargs)

'''
seta("",
    logo="",
    wp="",
    web="",
    tw="",
    mani=[],
    standsIn=[],
)
'''

seta("scottish_green_party",
    logo="Scottish_Green_Party_logo.gif",
    wp="http://en.wikipedia.org/wiki/Scottish_Green_Party",
    web="http://www.scottishgreens.org.uk/",
    tw="https://twitter.com/scotgp",
    mani=['sgp_2009euro.pdf',
          'sgp_2010ge.pdf',
          'sgp_2011scot.pdf'],
    standsIn=['scot'],
    aff='European Green Party',
)
seta("green_party_of_england_and_wales",
    logo="http://upload.wikimedia.org/wikipedia/en/thumb/a/ab/Green_Party_of_England_and_Wales_logo.svg/200px-Green_Party_of_England_and_Wales_logo.svg.png",
    wp="http://en.wikipedia.org/wiki/Green_Party_of_England_and_Wales",
    web="http://www.greenparty.org.uk/",
    tw="https://twitter.com/thegreenparty",
    mani=['gpew_2009euro.pdf',
          'gpew_2010ge.pdf'],
    standsIn=['eng','wales'],
    aff='European Green Party',
)

seta("green_party_in_northern_ireland",
    logo="gpni.jpg",
    wp="http://en.wikipedia.org/wiki/Green_Party_in_Northern_Ireland",
    web="http://www.greenpartyni.org/",
    tw="",
    mani=[],
    standsIn=['ni'],
    aff='European Green Party',
)

seta("european_parliament_groups",
    logo="",
    wp="http://en.wikipedia.org/wiki/Political_groups_of_the_European_Parliament",
    web="",
    tw="",
    mani=[],
    standsIn=[],
)

seta("European People's Party",
    logo="http://upload.wikimedia.org/wikipedia/en/5/56/EPP-ED_logo.svg",
    wp="http://en.wikipedia.org/wiki/European_People's_Party_(European_Parliament_group)",
    web="http://www.eppgroup.eu/",
    tw="https://twitter.com/EPPGroup",
    mani=[],
    standsIn=[],
)

seta("Progressive Alliance of Socialists and Democrats",
    logo="http://upload.wikimedia.org/wikipedia/commons/6/6b/S%26D_logo.jpg",
    wp="http://en.wikipedia.org/wiki/Progressive_Alliance_of_Socialists_and_Democrats",
    web="http://www.socialistsanddemocrats.eu/",
    tw="https://twitter.com/TheProgressives",
    mani=[],
    standsIn=[],
)

seta("Alliance of Liberals and Democrats for Europe",
    logo="http://upload.wikimedia.org/wikipedia/en/2/2d/ALDE_logo.svg",
    wp="http://en.wikipedia.org/wiki/Group_of_the_Alliance_of_Liberals_and_Democrats_for_Europe",
    web="http://www.alde.eu/",
    tw="https://twitter.com/ALDEADLE",
    mani=[],
    standsIn=[],
)

seta("Greens - European Free Alliance",
    logo="http://upload.wikimedia.org/wikipedia/en/thumb/4/4c/Logo_greens-efa.png/200px-Logo_greens-efa.png",
    wp="http://en.wikipedia.org/wiki/The_Greens%E2%80%93European_Free_Alliance",
    web="http://www.greens-efa.eu/",
    tw="https://twitter.com/greensep",
    mani=[],
    standsIn=[],
)

seta("European Conservatives and Reformists",
    logo="http://upload.wikimedia.org/wikipedia/en/thumb/e/e9/European_Conservatives_and_Reformists_logo.png/200px-European_Conservatives_and_Reformists_logo.png",
    wp="http://en.wikipedia.org/wiki/European_Conservatives_and_Reformists",
    web="http://ecrgroup.eu/",
    tw="https://twitter.com/ecrgroup",
    mani=[],
    standsIn=[],
)

seta("european_united_left_nordic_green_left",
    logo="http://upload.wikimedia.org/wikipedia/en/b/b6/Logo_gue-ngl.png",
    wp="http://en.wikipedia.org/wiki/European_United_Left%E2%80%93Nordic_Green_Left",
    web="http://www.guengl.eu/",
    tw="https://twitter.com/GUENGL",
    mani=[],
    standsIn=[],
)

seta("Europe of Freedom and Democracy",
    logo="http://upload.wikimedia.org/wikipedia/en/thumb/8/87/Europe_of_Freedom_and_Democracy_logo.jpg/200px-Europe_of_Freedom_and_Democracy_logo.jpg",
    wp="http://en.wikipedia.org/wiki/Europe_of_Freedom_and_Democracy",
    web="http://www.efdgroup.eu/",
    tw="",
    mani=[],
    standsIn=[],
)

seta("about_euro_election_2014",
    logo="ballot_box_128x128.png",
)

seta("single_transferable_vote",
    wp="http://en.wikipedia.org/wiki/Single_transferable_vote",
)

seta("dhondt",
    wp="http://en.wikipedia.org/wiki/D%27Hondt_method",
)
seta("european_political_party",
    wp="http://en.wikipedia.org/wiki/European_political_party",
)


seta("european_peoples_party",
    logo="http://upload.wikimedia.org/wikipedia/en/thumb/e/e7/EPP_logo.svg/200px-EPP_logo.svg.png",
    wp="http://en.wikipedia.org/wiki/European_People%27s_Party",
    web="http://www.epp.eu/index.asp",
    tw="https://twitter.com/epptweet",
    mani=[],
)

seta("party_of_european_socialists",
    logo="http://upload.wikimedia.org/wikipedia/en/4/45/PES_logo.svg",
    wp="http://en.wikipedia.org/wiki/Party_of_European_Socialists",
    web="http://www.pes.eu/",
    tw="https://twitter.com/PES_PSE",
    mani=[],
)

seta("alliance_of_liberals_and_democrats_for_europe_party",
    logo="http://upload.wikimedia.org/wikipedia/en/2/2d/ALDE_logo.svg",
    wp="http://en.wikipedia.org/wiki/Alliance_of_Liberals_and_Democrats_for_Europe_Party",
    web="http://www.aldeparty.eu/en",
    tw="",
    mani=[],
)

seta("european_green_party",
    logo="http://upload.wikimedia.org/wikipedia/en/c/c9/European_Greens_logo.svg",
    wp="http://en.wikipedia.org/wiki/European_Green_Party",
    web="http://europeangreens.eu/",
    tw="https://twitter.com/europeangreens",
    aff="Greens - European Free Alliance",
)

seta("alliance_of_european_conservatives_and_reformists",
    logo="http://upload.wikimedia.org/wikipedia/en/8/88/Alliance_of_European_Conservatives_and_Reformists_logo.png",
    wp="http://en.wikipedia.org/wiki/Alliance_of_European_Conservatives_and_Reformists",
    web="http://www.aecr.eu/",
    tw="",
    mani=[],
)

seta("party_of_the_european_left",
    logo="http://upload.wikimedia.org/wikipedia/en/7/72/European_Left_logo.svg",
    wp="http://en.wikipedia.org/wiki/Party_of_the_European_Left",
    web="http://www.european-left.org/",
    tw="https://twitter.com/europeanleft",
    mani=[],
)

seta("movement_for_a_europe_of_liberties_and_democracy",
    logo="http://upload.wikimedia.org/wikipedia/en/thumb/d/d5/Movement_for_a_Europe_of_Liberties_and_Democracy_logo.png/200px-Movement_for_a_Europe_of_Liberties_and_Democracy_logo.png",
    wp="http://en.wikipedia.org/wiki/Movement_for_a_Europe_of_Liberties_and_Democracy",
    web="http://www.meldeuropa.com/",
    tw="",
    mani=[],
)

seta("european_democratic_party",
    logo="http://upload.wikimedia.org/wikipedia/en/7/75/European_Democratic_Party_logo.png",
    wp="http://en.wikipedia.org/wiki/European_Democratic_Party",
    web="http://www.pde-edp.eu/",
    tw="",
    mani=[],
)

seta("european_free_alliance",
    logo="http://upload.wikimedia.org/wikipedia/commons/4/4f/Party_Logo_of_the_European_Free_Alliance.svg",
    wp="http://en.wikipedia.org/wiki/European_Free_Alliance",
    web="http://www.e-f-a.org/home.php",
    tw="",
    mani=[],
)

seta("european_alliance_for_freedom",
    logo="european_alliance_for_freedom.png",
    wp="http://en.wikipedia.org/wiki/European_Alliance_for_Freedom",
    web="http://www.eurallfree.org/",
    tw="",
    mani=[],
)


seta("christian_party",
    logo="http://upload.wikimedia.org/wikipedia/en/1/1c/Christian_Party_logo.gif",
    wp="http://en.wikipedia.org/wiki/Christian_Party_%28UK%29",
    web="",
    tw="",
    mani=["CP-CPA_2009euro.pdf"],
    standsIn=["gb"],
)

seta("christian_peoples_alliance",
    logo="http://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/ChristianPeoplesAlliance.png/200px-ChristianPeoplesAlliance.png",
    wp="http://en.wikipedia.org/wiki/Christian_Peoples_Alliance",
    web="http://www.cpaparty.org.uk/",
    tw="",
    mani=["CP-CPA_2009euro.pdf", "cpa_2010ge.pdf"],
    standsIn=["gb"],
    aff="European Christian Political Movement",
)

seta("european_christian_political_movement",
    logo="http://upload.wikimedia.org/wikipedia/en/thumb/7/77/European_Christian_Political_Movement.png/200px-European_Christian_Political_Movement.png",
    wp="http://en.wikipedia.org/wiki/European_Christian_Political_Movement",
    web="http://www.ecpm.info/en/",
    tw="",
    mani=[],
    standsIn=[],
)

seta("Pirate Parties International",
    logo="http://upload.wikimedia.org/wikipedia/commons/5/5c/PPI_signet.svg",
    wp="http://en.wikipedia.org/wiki/Pirate_Parties_International",
    web="http://www.pp-international.net/",
    tw="",
    mani=[],
    standsIn=[],
    aff="Greens - European Free Alliance"
)

#---------------------------------------------------------------------

''' ***** keep this template at bottom *****
seta("",
    logo="",
    wp="",
    web="",
    tw="",
    mani=[],
    standsIn=[],
)
'''

#end
