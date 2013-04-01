# party.py
# -*- coding: utf-8 -*-

import markdown
import htmlhelp
from htmlhelp import li
import entity
import article
import area

""" dict of all parties, key is abbreviated name, e.g. 'lab' """
parties = {}

def getParty(p):
    p = str(p)
    return parties[p]

#---------------------------------------------------------------------
"""
Instance variables:

ab [str] abbreviation
col [str] colour
desc [str] description
wp [str] partial url to wikipedia article
web [str] the party's website
standsIn [list of str] areas it stands in
mani [list of (str,str)] manifestos that the party has. The order is:
   (title, filename). E.g.:
      [('2009', 'cp_cpa_eu2009.pdf'), ('2010', 'cp2010.pdf')]
   Filenames resolve to a URL like /static/manifesto/<filename>.
   If the title is one of the following, it is expanded thus:
      2009 => 2009 European election
      2010 => 2010 general election
   (governed by manifestoNameRewrite())
"""

def manifestoNameRewrite(yr):
    mrw = {'2009': '2009 European',
           '2010': '2010 general',
           '2011': '2011 Scottish general',
           '2012': '2012 London'}
    if mrw.has_key(yr):
        return mrw[yr]
    return yr

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


class Party(entity.Entity):
    def __init__(self, ab, name, title, standsIn=None):
        global parties
        self.ab = ab
        self.name = name.decode('utf-8') # convert to unicode
        if title:
            self.title = title.decode('utf-8')
        else:
            self.title = self.name
        if self.name[:6]=="Ind - ":
            self.title = self.name[6:] + " (Independent)"
            surname = self.name.split()[-1]
            self.name = surname
            #self.name = self.name[6:] + " (I)"
        self.desc = "" # description
        self.col = "fff" # colour
        self.logo = ""
        self.mani = None
        self.wp = self.web = self.tw =  None
        if standsIn==None:
            self.standsIn = ['gb']
        else:
            self.standsIn = standsIn
        parties[ab] = self

    def html(self):
        h = ("<h1>%s</h1>\n\n" % self.title
             + self.htmlAttributes())
        if self.desc:
            h += "<h2>Description</h2>\n%s\n" % self.desc
        return h

    def xxhtmlManifestos(self):
        h = ""
        if not self.mani: return ""
        h = "<li>Manifestos:</li>\n<ul>\n"
        for fn in self.mani:
            h += ("<li><a href='/static/manifesto/%s'>%s</a></li>" %
                  (fn, manifestoNameFromFn(fn)))
        #//for
        h += "</ul>\n"
        return h

    def xxhtmlAttributes(self):
        """ return html for various attributes, such as
        colour, wikipedia url, etc.
        """
        h = ""
        if self.logo:
            if self.logo[:7]=="http://":
                logoUrl = self.logo
            else:
                logoUrl = "/static/logo/" + self.logo
            h += ("<div class='logo'><img src='%s' alt='%s logo'></div>"
                  % (logoUrl, self.name))
        h += "<ul>\n"
        if self.col!="fff":
            h += (("<li>Colour: <span style='"
                   "background-color:#%s; width:50px; height:16px;'"
                   ">&nbsp; &nbsp; &nbsp;</span></li>\n\n") % self.col)
        if self.wp:
            h += li("<a href='%s'>Wikipedia article</a>"%self.wp)
        if self.web:
            h += li("<a href='%s'>Website</a>"%self.web)
        if self.tw:
            h += li("<a href='%s'>Twitter</a>"%self.tw)
        h += self.htmlManifestos()
        if self.standsIn:
            areaHtml = ", ".join([area.areas[aab].nameInUrl()
                                   for aab in self.standsIn])
            h += li("Intends to stand in " + areaHtml)

        h += "</ul>\n"
        return h

    def url(self):
        u = "/party/%s" % self.ab
        return u

    def nameInUrl(self, sw=None):
        """ the party's name encased in a url
        @param sw [Swing]
        """
        if sw==None:
            h = "<a href='%s'>%s</a>" % (self.url(), self.name)
        else:
            h = ("<a href='/pred_party/%s%s'>%s</a>"
                 % (self.ab, sw.queryString(), self.name))
        return h

    def titleInUrl(self, sw=None):
        """ the party's title encased in a url
        @param sw [Swing]
        """
        if sw==None:
            h = "<a href='%s'>%s</a>" % (self.url(), self.title)
        else:
            h = ("<a href='/pred_party/%s%s'>%s</a>"
                 % (self.ab, sw.queryString(), self.title))
        return h

#---------------------------------------------------------------------
# load parties

def setStandsIn(parties, areas):
    """ state which areas a party intends to stand in in 2014 """
    if isinstance(parties, str): parties = parties.split(":")
    if isinstance(areas, str): areas = areas.split(":")
    for pab in parties:
        p = getParty(pab)
        p.standsIn = areas

def seta(pab, **kwargs):
    """ Set attributes for a party.
    @param pab [str] party abbreviation
    @param kwargs [dict] key-value pairs for attributes to be
    set.
    """
    party = getParty(pab)
    for k, v in kwargs.items():
        if k=='desc':
            party.__dict__[k] = htmlhelp.md(article.mwLink(v))
        else:
            party.__dict__[k] = v
    #//for

#order is ab:name:title:colour
partyNames = """
lab:Labour:Labour Party:dc241f
con:Conservative:Conservative Party:0087dc
ld:Lib Dem:Liberal Democrats:fdbb30
green:Green:Green parties:9c3
ukip:UKIP:United Kingdom Independence Party:70147a
bnp:BNP:British National Party:00008b
slp:Soc Labour:Socialist Labour Party:900
christ:Christian:Christian list:96c
no2eu:No2EU:No to EU - Yes to Democracy:900
jury:Jury Team
libert:Libertas
peace:Peace:Peace Party:da70d6
roman:Roman:Roman Party Ave
ukf:UK First
animal:Animals Count
fpft:Fair Pay:Fair Pay Fair Trade
pen:Pensioners:Pensioners Party
yes2eu:Yes2Europe
social:Socialist (GB):Socialist Party of Great Britain:900
wai:Wai D:Wai D Your Decision
pir:Pirate:Pirate Party UK:0ec

snp:SNP:Scottish Nationalist Party:ff0
ssp:SSP:Scottish Socialist Party:900
pc:Plaid Cymru:Plaid Cymru:008142
ed:Eng Dem:English Democrats:915f6d
mebyon:Mebyon Kernow::cc0

sf:Sinn Féin:Sinn Féin:080
dup:Dem Unionist:Democratic Unionist Party:d46a4c
uu:Ulster Unionist:Ulster Unionist Party:0087dc
sdlp:SDLP:Social Democratic and Labour Party:9f6
tuv:Trad Unionist:Traditional Unionist Voice:d46a4c
alli:Alliance:Alliance Party:ffd700

i_rob:Ind - Duncan Robertson
i_apaloo:Ind - Francis Apaloo
i_rigby:Ind - Peter Rigby
i_hopkins:Ind - Katie Hopkins
i_jan:Ind - Jan Jananayagam
i_cheung:Ind -  Steven Cheung
i_rahman:Ind - Sohale Rahman
i_alcan:Ind - Gene Alcantara
i_saad:Ind - Haroon Saad
"""

for line in partyNames.split("\n"):
    if ":" in line:
        lsp = line.split(":")
        ab = lsp[0]; name = lsp[1]
        col = "fff"
        if len(lsp)>=3:
            title = lsp[2]
        else:
            title = name
        if len(lsp)>=4:
            col = lsp[3]
        p = Party(ab, name, title)
        p.col = col
#//for

setStandsIn('snp:ssp', 'scot')

setStandsIn('pc', 'wales')
setStandsIn('ed', 'eng')
setStandsIn('green', 'uk')
setStandsIn('sf:dup:uu:sdlp:tuv:alli','ni')

independents = [pab
                for pab in parties.keys()
                if pab[:2]=='i_']
setStandsIn(independents, [])

getParty('pir').desc = """Was founded in 2009, shortly after
the European election of that year"""

seta('pir',
    logo="ppuk.svg",
    desc = """Pirate Party UK was founded in 2009, shortly after
    the European election of that year, so it will contest its first
    European election in 2014.""",
    wp = "http://en.wikipedia.org/wiki/Pirate_Party_UK",
    web = "http://www.pirateparty.org.uk/",
    tw = "https://twitter.com/PiratePartyUK",
    standsIn = ["uk"],
    mani=['ppuk_2010ge.pdf'],
    aff="Pirate Parties International",
)

seta("wai",
    #title="Wai D Your Decision",
    desc = """Wai D had the dubious distinction of coming last in the 2009
election. Maybe they will do better in 2014.

The name "Wai D" appears to be a phonetic rendition of the initials Y.D. for
"Your Decision".
""",
    web = "http://www.yourdecision.co.uk/england/exeter/priory/index.php",
)

seta("con",
    #title="Conservative Party",
    logo="http://upload.wikimedia.org/wikipedia/en/b/b6/Conservative_logo_2006.svg",
    desc="""The Tories came first in 2009, with a robust 27.7% of GB
votes, which gave them 25 seats -- almost twice as many as their nearest
rivals, [UKIP](/party/ukip) and [Labour](/party/lab).

Will they do as well in 2014? There are reasons to suggest they might not:

* In 2009 they were in opposition, but now they are in government. There
is typically an anti-government protest vote in European elections.
* They have been consistently behind Labour since the
[omnishambles](http://en.wikipedia.org/wiki/Omnishambles)
budget in March 2012.
* UKIP have been doing well in the polls since November 2012, when they finished second in the
[Rotherham by-election](http://en.wikipedia.org/wiki/Rotherham_by-election,_2012);
UKIP may attract lots of votes from disgruntled Conservative supporters.
""",
    wp="http://en.wikipedia.org/wiki/Conservative_Party_%28UK%29",
    web="http://www.conservatives.com/",
    tw="https://twitter.com/Conservatives",
    mani=['con_2009euro.pdf',
          'con_2010ge.pdf',
          'con_2011scot.pdf',
          'con_2011wales.pdf']
)

seta("ukip",
    #title="United Kingdom Independence Party",
    logo="ukip.png",
    desc="""UKIP have increased their share of the vote and number
of seats in every European election since proportional representation
was introduced in 1999. Since the [Rotherham by-election](http://en.wikipedia.org/wiki/Rotherham_by-election,_2012), when
they came second, they've been riding high in the opinion polls.

It has been speculated, particularly by UKIP supporters, that they could
come first this time. In the past, UKIP have sometimes been written off
as a joke; if they do come first no-one will be able to do that any more
with a straight face.
""",
    wp="http://en.wikipedia.org/wiki/UK_Independence_Party",
    web="http://www.ukip.org/",
    tw="https://twitter.com/UKIP",
    mani=['ukip_2010ge.pdf']
)

seta("lab",
    #title="Labour Party",
    logo="http://upload.wikimedia.org/wikipedia/en/0/05/Logo_Labour_Party.svg",
    desc="""Labour did very badly in 2009. To put it into historical
perspective, they got their lowest vote share in any nationwide election
since the [December 1910 general election](http://en.wikipedia.org/wiki/United_Kingdom_general_election,_December_1910). In South West England less than 3% of the electorate voted for them,
an appalling result for a governing party.

But then they were in government, and at the end of an unpopular worn-out government to boot. Now they're in opposition. There is usually an
anti-government swing in European elections,
and 2014 is unlikely to be different.
Furthermore, it's not just the Tories who are in government,
the Lib Dems are too.
This means that not only will the Lib Dems lose votes due to being in
government, they will also fail to pick up protest votes, which could go
Labour's way instead.

Will Labour come first in 2014? It looks that either they or UKIP will.
""",
    wp="http://en.wikipedia.org/wiki/Labour_Party_%28UK%29",
    web="http://www.labour.org.uk/",
    tw="https://twitter.com/UKLabour",
    mani=['labour_2009euro.pdf',
          'labour_2010ge.pdf']
)

seta("ld",
    logo="http://upload.wikimedia.org/wikipedia/en/8/84/Liberal_Democrat_Logo.svg",
    desc="""The Liberal Democrats have not prospered from their
Westminster coalition with the Conservatives. For example, in the
[2012 local elections](http://en.wikipedia.org/wiki/United_Kingdom_local_elections,_2012)
they got 16% of the vote, down 10 points from the 26%
they got in
[2010](http://en.wikipedia.org/wiki/United_Kingdom_local_elections,_2010).
Or consider Scotland, where their vote share halved in the
[Scottish Parliamentary election](http://en.wikipedia.org/wiki/Scottish_Parliament_election,_2011)
in 2011 and almost halved in the [local elections](http://en.wikipedia.org/wiki/Scottish_local_elections,_2012)
the next year.

So it seems likely that the Lib Dem vote will go down. This is a
particular problem for them because there's an implied hurdle in the
voting system at about 10% of the vote: a party that gets less than that
is likely to be under-represented in seats. For example, if the Lib Dems [lose half their votes](/pred_party/ld?typ=delta&ld=-687),
they'll be down to two seats, one in South East England and the other in South West England.

With all this in mind, it's likely that the Lib Dems will treat the European
election as a damage limitation exercise, looking to retain their existing
seats rather than gaining new ones. Ironically, the hardest seat for them to
keep may be the region where they did best in 2009,
North East England, because there are only 3 seats in the region.
""",
    wp="http://en.wikipedia.org/wiki/Liberal_Democrats",
    web="www.libdems.org.uk",
    tw="https://twitter.com/LibDems",)

seta("green",
    #title="Green Parties",
    desc="""There are in fact three green parties in the UK, founded when
the Green Party (UK) amicably split in 1990:

* [[Green Party of England and Wales]]
* [[Scottish Green Party]]
* [[Green Party in Northern Ireland]]

They are considered together in this website as they all share the
same philosophy, and consequently a swing towards one green party
is likely to be reflected as a swing towards them all.

The Greens got 8.6% of GB votes in 2009, which was 2.5 points more than
they had achieved in 2004 or 1999, although that increase in votes didn't
give them any more seats -- in all three elections they won 2 seats.

This is because there is an implied hurdle in the voting system at about
10% of the vote: if a party gets more than that, they will get seats at least proportional to their vote, but if they get a lower vote share, they will
get a lower proportion of seats than votes. So for example, the Greens got
8.4% of UK votes but only 2.8% of seats.

This effect could work to the Greens' advantage if they do well: for example
if they get an [extra 2% of votes across the UK](/pred_result/uk?typ=delta&green=224), they will win 6 seats, three
time more than they currently have.
""",
    logo="http://upload.wikimedia.org/wikipedia/commons/f/ff/Sunflower_%28Green_symbol%29.svg",
    wp="http://en.wikipedia.org/wiki/Green_politics",
    web="",
    aff="European Green Party",
    )

seta("bnp",
    logo="http://upload.wikimedia.org/wikipedia/en/9/96/British_National_Party.svg",
    desc="""The BNP won its first seats in the European parliament in 2009,
when [Andrew Brons](http://en.wikipedia.org/wiki/Andrew_Brons)
won a seat in Yorkshire and the Humber, and party leader
[Nick Griffin](http://en.wikipedia.org/wiki/Nick_Griffin)
won a seat in North West England.

However, Brons resigned the BNP whip in 2012, and he has been involved in
the creation of a rival nationalist party, the British Democratic Party.

Will the BNP manage to keep Griffin's seat, and win back Brons's? Or will
the British Democratic Party split the nationalist vote?
These questions will be answered in June 2014.
""",
    wp="http://en.wikipedia.org/wiki/British_National_Party",
    web="http://www.bnp.org.uk/",
    tw="https://twitter.com/bnp",
    mani=['bnp_2010ge.pdf'],
)

seta("snp",
    logo="http://upload.wikimedia.org/wikipedia/en/3/30/Scottish_National_Party_logo.svg",
    desc=u"""The Scottish Nationalists currently hold 2 seats in the
European Parliament. But they've done well in recent elections -- they
scored 44% of the vote in the
[2011 Scottish Parliamentary election](http://en.wikipedia.org/wiki/Scottish_Parliament_election,_2011), and
33% of first preferences in the
[local elections](http://en.wikipedia.org/wiki/Scottish_local_elections,_2012)
a year later
-- so they are probably hoping to win 3 seats in this European election.

Having said that, the SNP probably view the European election as somewhat of
a sideshow. Their *raison d'être* is Scottish independence, and there will be
a
[referendum](http://en.wikipedia.org/wiki/Scottish_independence_referendum,_2014)
on that a few months after the European election. They'll
be hoping for a good result in the European election that will transform
into a win for the Yes vote on independence.

The SNP will also probably be secretly hoping the Conservatives do well in the
European election. Many Scots don't like the Tories, and the prospect of another
Tory government after the
[2015 UK general election](http://en.wikipedia.org/wiki/Next_United_Kingdom_general_election)
could push a few into the
Yes camp for independence.""",
    wp="http://en.wikipedia.org/wiki/Scottish_National_Party",
    web="http://www.snp.org/",
    tw="https://twitter.com/theSNP",)

seta("ed",
    logo="eng_dem.png",
    desc="""The English Democrats were founded in 1998 by Robin Tilbrook as the
*English National Party*, in response to calls for Scottish and Welsh
devolution. They changed their name to English Democrats in 2002.

The English Democrats' main policy is the creation of an English Parliament
with similar powers to the Scottish Parliament.

Their greatest electoral success so far was in 2009, when
[Peter Davies](http://en.wikipedia.org/wiki/Peter_Davies_%28politician%29)
was elected
[Mayor of Doncaster](http://en.wikipedia.org/wiki/Mayor_of_Doncaster).
""",
    wp="http://en.wikipedia.org/wiki/English_Democrats",
    web="http://www.englishdemocrats.org.uk/",
    tw="https://twitter.com/EnglishVoice",)

seta("pc",
    logo="plaid_cymru.png",
    desc=""" """,
    wp="http://en.wikipedia.org/wiki/Plaid_Cymru",
    web="http://www.english.plaidcymru.org/?force=1",
    tw="https://twitter.com/plaid_cymru",)

seta("christ",
    desc="""The Christian list in the 2009 European election was a joint
list by two parties, the [[Christian Party]] and the [[Christian People's Alliance]].
""",
    mani = ['CP-CPA_euro2009.pdf']
)

seta("sf",
    logo="sinn_fein.png",
    desc=""" """,
    wp="http://en.wikipedia.org/wiki/Sinn_F%C3%A9in",
    web="http://www.sinnfein.ie/",
    tw="https://twitter.com/sinnfeinireland",)

seta("dup",
    #title="Democratic Unionist Party",
    logo="dup.png",
    desc=""" """,
    wp="http://en.wikipedia.org/wiki/Democratic_Unionist_Party",
    web="http://www.mydup.com/",
    tw="https://twitter.com/duponline",)

seta("uu",
    #title="Ulster Unionist Party",
    logo="uu.png",
    desc="""The Ulster Unionists' candidate in the 2009 European election,
[Jim Nicholson](http://en.wikipedia.org/wiki/Jim_Nicholson_%28UK_politician%29),
actually stood under the banner of
"[Conservatives and Unionists](http://en.wikipedia.org/wiki/Ulster_Conservatives_and_Unionists)"
which was a short form of "Ulster Conservatives and Unionists - New Force (UCUNF)",
an electoral alliance between the Ulster Unionists and the Conservative Party.

However since this alliance is nbow defunct, Nicholson is listed as an
Ulster Unionist.
""",
    wp="http://en.wikipedia.org/wiki/Ulster_Unionist_Party",
    web="http://www.uup.org/",
    )

seta("sdlp",
    #title="Social Democratic and Labour Party",
    logo="sdlp.png",
    desc=""" """,
    wp="http://en.wikipedia.org/wiki/Social_Democratic_and_Labour_Party",
    web="http://www.sdlp.ie/",
    tw="https://twitter.com/SDLPlive",)

seta("tuv",
    #title="Traditional Unionist Voice",
    logo="tuv.png",
    desc=""" """,
    wp="http://en.wikipedia.org/wiki/Traditional_Unionist_Voice",
    web="http://www.tuv.org.uk/",
    tw="https://twitter.com/JimAllister",)

seta("alli",
    #title="Alliance Party of Northern Ireland",
    logo="alliance.png",
    desc=""" """,
    wp="http://en.wikipedia.org/wiki/Alliance_Party_of_Northern_Ireland",
    web="http://allianceparty.org/",
    tw="https://twitter.com/allianceparty",)

seta("i_jan",
    desc="""Janani Jananayagam was the highest-polling independent in the 2009 European election. She stood in London where she got over fifty thousand votes.""",
    wp="http://en.wikipedia.org/wiki/Jan_Jananayagam",
    tw="https://twitter.com/jan_jananayagam",)

seta("slp",
    logo="slp.png",
    desc=""" """,
    wp="http://en.wikipedia.org/wiki/Socialist_Labour_Party_%28UK%29",
    web="http://www.socialist-labour-party.org.uk/",
    tw="https://twitter.com/slp_gb",)

seta("no2eu",
    logo="no2eu.gif",
    #title="No2EU - Yes to Democracy",
    desc="""No2EU was an electoral alliance created by a trade union, the
National Union of Rail, Maritime and Transport Workers (RMT), to contest the 2009 European election in Great Britain. The coalition included:

* Socialist Party
* Communist Party of Britain
* Solidarity
* Alliance for Green Socialism
* Liberal Party
* Socialist Resistance
* Indian Workers' Association

The coalition also received support from members of:

* Respect
* Socialist Workers Party

### Defunct?

No2EU's Twitter account hasn't been updated since August 2009, and
the most recent news item on their website dates from March 2010,
which suggests to me that they are defunct.
""",
    wp="http://en.wikipedia.org/wiki/NO2EU",
    web="http://www.no2eu.com/",
    tw="https://twitter.com/no2eu",)

seta("jury",
    logo="jury.jpg",
    desc=""" """,
    wp="http://en.wikipedia.org/wiki/Jury_Team",
    web="",
    tw="",)

seta("mebyon",
    logo="http://upload.wikimedia.org/wikipedia/en/thumb/1/1c/Mebyon_Kernow_logo.svg/200px-Mebyon_Kernow_logo.svg.png",
    desc=""" """,
    wp="http://en.wikipedia.org/wiki/Mebyon_Kernow",
    web="http://www.mebyonkernow.org/",
    tw="https://twitter.com/MebyonKernow",)


seta("ukf",
    logo="http://upload.wikimedia.org/wikipedia/en/thumb/0/03/UK_First_logo.png/200px-UK_First_logo.png",
    desc=""" """,
    wp="http://en.wikipedia.org/wiki/United_Kingdom_First_Party",
    web="http://ukfirstparty.blogspot.co.uk/",
    tw="",)


seta("ssp",
    #title="Scottish Socialist Party",
    desc=""" """,
    wp="",
    web="",
    tw="",)








#end
