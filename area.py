# area.py = areas

"""
instance vatriables:
   ab [str] = abbreviation for name (used as identifier)
   name [str] = name as it goes in tables
   title [str] = full name
"""

import htmlhelp

areas = {}
regionAbs = []
aggregationAbs = []

#---------------------------------------------------------------------

class Area:

    def getRegions(self):
        raise ImplementedBySubclass

    def __repr__(self):
        return self.__str__()

    def nameInUrl(self):
        """ return the area's name in a url """
        h = "<a href='/eresult/%s'>%s</a>" % (self.ab, self.name)
        return h

    def contains(self, anArea):
        """ Does (self) include (anArea)?
        @param anArea [Area]
        @return [bool]
        """
        if self is anArea: return True
        selfAbs = [r.ab for r in self.getRegions()]
        areaAbs = [r.ab for r in anArea.getRegions()]
        return areaAbs[0] in selfAbs


#---------------------------------------------------------------------

class Region(Area):

    def __init__(self, ab, name, title=None):
        self.ab = ab
        self.name = name
        if title:
            self.title = title
        else:
            self.title = name
        self.desc = None

    def getRegions(self):
        return [self]


    def __str__(self):
        s = "<%s:%s>" % (self.ab, self.name)
        return s

#---------------------------------------------------------------------

def readContents(contents):
    areaNames = contents.split(":")
    regions = []
    for ab in areaNames:
        area = areas[ab]
        regions += area.getRegions()
    return regions

class Aggregation(Area):

    def __init__(self, ab, name, title, contents):
        self.ab = ab
        self.name = name
        self.title = title
        self.desc = None
        self.regions = readContents(contents)

    def getRegions(self):
        return self.regions

    def __str__(self):
        s = "<%s:%s=%s>" % (
            self.ab,
            self.name,
            ",".join([r.ab for r in self.regions]))
        return s

#---------------------------------------------------------------------

areasForLeftbar = """\
eng
nee:North East
nwe:North West
york:Yorkshire
em:East Midlands
wm:West Midlands
ee:East
see:South East
swe:South West
london:London
noteng
ni
scot
wales
gb
uk"""

def leftbarHtml(preUrl="/eresult/", postUrl=""):
    h = "<h3>Regions</h3>\n\n"
    for line in areasForLeftbar.split("\n"):
        line = line.strip()
        if ":" in line:
            areaAb, shortName = line.split(":")
        else:
            areaAb = line
            shortName = areas[areaAb].name
        if isinstance(areas[areaAb], Region):
            tab = "&nbsp;&nbsp;&nbsp;"
        else:
            tab = "\n"
        h += ("%s<a href='%s%s%s'>%s</a><br>\n"
              % (tab, preUrl, areaAb, postUrl, shortName))
    #//for
    return h



#---------------------------------------------------------------------
# load areas:

def makeRegion(ab, name, title=None):
    r = Region(ab, name, title)
    areas[ab] = r
    regionAbs.append(ab)

def makeAggregation(ab, name, contents):
    ag = Aggregation(ab, name, name, contents)
    areas[ab] = ag
    aggregationAbs.append(ab)

def saa(aab, **kwargs):
    """ Set Area Attributes
    @param aab [str] area abbreviation
    @param kwargs [dict]
    """
    area = areas[aab]
    for k, v in kwargs.items():
        if k=='desc':
            area.__dict__[k] = htmlhelp.md(v)
        else:
            area.__dict__[k] = v
    #//for

makeRegion("nee", "NE England", "North East England")
makeRegion("nwe", "NW England", "North West England")
makeRegion("york", "Yorkshire", "Yorkshire and the Humber")
makeRegion("em", "East Midlands")
makeRegion("wm", "West Midlands")
makeRegion("ee", "East of England")
makeRegion("see", "SE England", "South East England")
makeRegion("swe", "SW England", "South West England")
makeRegion("london", "London")

makeRegion("ni", "N Ireland", "Northern Ireland")
makeRegion("scot", "Scotland")
makeRegion("wales", "Wales")

makeAggregation("eng", "England", "nee:nwe:york:em:wm:ee:see:swe:london")
makeAggregation("neng", "North England", "nee:nwe:york")
makeAggregation("mid", "Midlands", "em:wm")
makeAggregation("seng", "South England", "ee:see:swe:london")
makeAggregation("noteng", "Not England", "ni:scot:wales")
makeAggregation("gb", "Great Britain", "eng:scot:wales")
makeAggregation("uk", "United Kingdom", "gb:ni")


# attrbutes:

saa("ni", desc = """\
Northern Ireland is the only part of the UK that uses
[Single Transferable Vote](/article/single_transferable_vote) (STV) as its
electoral system for the European elections. All other UK
electoral regions use [d'Hondt](/article/dhondt) closed lists. Northern Ireland
uses STV for all elections except those for the Westminster Parliament,
which use FPTP.)

Note that because NI uses STV the results table below is incomplete,
since it only shows first preferences and the result of an STV election
depends on lower preferences, not just first preferences. Although
having said that,
in all NI elections to the European Parliament, the three
candidates with the most 1st preferences were in fact elected.

""")

saa("wm", desc = """\
The table below says that West Midlands elected 7 MEPs. However in
June 2009, only 6 were elected.
Why then does it say 7? Because at the time of the election the UK was entitled to
72 MEPs, but when the Lisbon Treaty came into effect on 1 December 2009,
allocation of MEPs changed and Britain was allocated 73.

So the electoral
commission dusted off the formula they used to decide how many MEPs
each region got, and found that if Britain had had an extra MEP,
the extra seat
would have gone to the West Midlands, giving it 7. It further decided
that under the d'Hondt system used to allocate seats to parties, the
extra seat would have gone to the Conservatives.

The Conservatives already had 2 MEPs,
so the extra seat went to the third candidate on their list,
[Anthea McIntyre](http://en.wikipedia.org/wiki/Anthea_McIntyre).

Looking at other parties, UKIP had 2 MEPs elected in 2009,
[Mike Nattrass](http://en.wikipedia.org/wiki/Mike_Nattrass)
and [Nikki Sinclaire](http://en.wikipedia.org/wiki/Nikki_Sinclaire).
However they only have one in this region now, because Sinclaire
left UKIP in January 2010, and in September 2012 set up her own
*We Demand a Referendum* party, who are calling for a referendum
on Britain's membership of the EU.

""")


#end
