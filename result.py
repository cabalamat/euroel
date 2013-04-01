# result.py

""" election results

EResult = election result
ins var:
    area [Area] = an area

RResult = result of a region
ins var:
    totSeats = total seats
    totVotes = total votes
    electorate = size of electorate
    pVotes = list of (partyAb, votes)
    resultTable = list of (partyAb, votes, pcVotes, seats, pcSeats)
        sorted by votes (decreasing), seats (decreasing)

AgResult = result for an aggregation
"""

import collections

import dhondt
import htmlhelp
import area
import party
import swing

eResults = {} # key is region abbreviation

USING_PRED_CACHE = True
predCache = {}

def getPredictedAreaResult(areaAb, sw):
    if predCache:
        key = (areaAb, sw.queryString())
        if predCache.has_key(key):
            return predCache[key]
        else:
            actualResult = getAreaResult(areaAb)
            predictedResult = actualResult.makePrediction(sw)
            predCache[key] = predictedResult
            return predictedResult
    else:
        actualResult = getAreaResult(areaAb)
        predictedResult = actualResult.makePrediction(sw)
        return predictedResult


def getAreaResult(areaAb, sw=None):
    """ Get result for an area (region or aggregate)
    @param areaAb [str]
    @param sw [Swing] if there is noe,m means it's a prediction
    @return [EResult]
    """
    if sw:
        actualResult = getAreaResult(areaAb)
        predictedResult = actualResult.makePrediction(sw)
        return getPredictedAreaResult(areaAb, sw)
    else:
        areaAb = str(areaAb)
        return eResults[areaAb]


#---------------------------------------------------------------------

def thousands(i):
    """ Separate thousands with a comma
    @param i [int]
    @return [str]
    """
    if i>=0:
        si = "%d" % (i,)
        return thou(si)
    else:
        si = "%d" % (-i,)
        return "-" + thou(si)

def thou(si):
    if len(si)<4: return si
    body, last3chars = si[:-3], si[-3:]
    return thou(body) + "," + last3chars

def pcStr(n, d):
    """ returns a string containing 100*n/d.
    If d is 0, returns ""
    """
    try:
        s = "%6.2f" % (100.0*n/d,)
    except:
        s = ""
    return s

#---------------------------------------------------------------------

class EResult:
    """ election result """

    def url(self):
        u = "/eresult/%s" % self.area.ab
        return u

    def forParty(self, pab):
        """ return a result for a party.
        @return the relevant row of the resultTable, i.e.
             (partyAb, votes, pcVotes, seats, pcSeats)
        """
        for row in self.resultTable:
            if row[0] == pab: return row
        return ("", 0, 0.0, 0, 0.0)


    def calcResultTable(self, partyVotes, partySeats):
        """ calculate self.resultTable
        @param partyVotes [list of (str, int)] votes for each party
        @param partySeats [dict of str:int] seats for each party
        """
        resultTable = []
        for pab, v in partyVotes:
            pcVotes = 100.0 * v / self.totVotes
            seats = partySeats[pab]
            pcSeats = 100.0 * seats / self.totSeats
            line = (pab, v, pcVotes, seats, pcSeats)
            resultTable.append(line)
        def voteSeatCmp(line1, line2):
            _,v1,_,s1,_ = line1
            _,v2,_,s2,_ = line2
            c = cmp(v1, v2)
            if c==0: c = cmp(s1, s2)
            return c
        resultTable.sort(voteSeatCmp, reverse=True)
        self.resultTable = tuple(resultTable)

    def getPartyA(self, aParty):
        """
        @param aParty [Party]
        @return [str] containing an <a href>..</a> html segment
            which gives a link to the party
        """
        return aParty.nameInUrl()

    def html(self):
        aAb = self.area.ab
        aName = self.area.name
        h = self.titleH()
        h += self.listRegions()
        h += self.desc()
        h += self.swingExplanation()
        h += self.htmlResultsTable()
        return h

    def titleH(self):
        h = ("<h1>European Election 2009 - result in %s</h1>\n\n"
             % (self.area.title,))
        return h

    def desc(self):
        """ return the area's description, if any """
        d = self.area.desc
        if d:
            h = "<h2>Description</h2>\n\n" + d + "\n\n"
            return h
        return ""

    def yearStr(self):
        """ this defaults to the 2009 result, and is over-ridden for
        predicted results """
        return "2009"

    def swingExplanation(self):
        """ explain swings used. Defaults to nothing, for 2009 results """
        return ""

    def nameInUrl(self, sw=None):
        """ the area's name encased in a url
        @param sw [Swing]
        """
        if sw==None:
            h = ("<a href='/eresult/%s'>%s</a>"
                 % (self.area.ab, self.area.name))
        else:
            h = ("<a href='/pred_result/%s%s'>%s</a>"
                 % (self.area.ab, sw.queryString(), self.area.name))
        return h

#---------------------------------------------------------------------

class RResult(EResult):
    """ a result in a Region (as opposed to an Aggregation) """

    def __init__(self, a, electorate, seats):
        self.area = a
        self.electorate = electorate
        self.totSeats = seats

    def setPartyVotes(self, partyVotes):
        """
        @param partyVotes list of (partyAb, votes), in decreasing order
        """
        self.pVotes = partyVotes
        self.totVotes = sum([v for pab,v in self.pVotes])
        partySeats = dhondt.getSeats(dict(self.pVotes), self.totSeats)
        self.calcResultTable(partyVotes, partySeats)

    def listRegions(self):
        """ list my subregions (for html) """
        return ""

    def makePrediction(self, sw):
        """ Make a prediction
        @param sw [Swing]
        @return [RResult]
        """
        predResult = PredRResult(self, sw)
        return predResult

    def willStandHere(self, pab):
        """ Will party (pab) stand in this region?
        @param pab [str] party abbreviation
        @return [bool]
        """
        standsWhereAb = swing.willStand[pab]
        standsWhere = area.areas[standsWhereAb]
        return standsWhere.contains(self.area)

    def htmlResultsTable(self):
        h = (u"<table class='results'>\n<tr>"
            "<th colspan=2>Party</th>\n"
            "<th>Votes</th>\n"
            "<th>%Vote</th>\n"
            "<th>Quotas</th>\n"
            "<th>Seats</th>\n"
            "<th>Graph</th>\n"
            "</tr>\n")

        for pab,v,pcv,s,pcs in self.resultTable:
            theParty = party.getParty(pab)
            line = "<tr>"
            line += ("<td style='background:#%(partyCol)s;'>&nbsp;</td>\n"
                "   <td>%(party)s</td>\n"
                "   <td align=right>%(v)s</td><td align=right>%(pcv)6.2f</td>\n"
                "   <td align=right>%(q)5.2f</td>\n"
                "   <td align=right>%(s)d</td>\n"
                "   <td class=barGraph>%(bar)s</td>\n") % {
                'partyCol': theParty.col,
                'party': self.getPartyA(theParty),
                'v':     thousands(v),
                'pcv':   pcv,
                'q':     (self.totSeats+1)*pcv/100.0,
                's':     s,
                'bar':   htmlhelp.barGraph(pcv, theParty.col),}
            line += "</tr>\n"
            h += line
        #//for
        h += ("<tr class='totalLine'><td></td>\n"
            "   <td style='border-left:0px;'>Total</td>\n"
            "   <td align=right><b>%(v)s</b></td>\n"
            "   <td align=right>%(pcv)6.2f</td>\n"
            "    <td></td>\n"
            "   <td align=right>%(s)d</td>\n"
            "   <td></td>\n"
            "</tr>\n") % {
            'v':   thousands(self.totVotes),
            'pcv': 100.0,
            's':   self.totSeats}
        h += "</table>\n\n"

        h += htmlhelp.md("""\
Key:

* **Votes** - the votes the party got in that region
* **%Vote** - the percentage of total votes in that region the party got
* **Quotas** - the number of [d'Hondt](http://en.wikipedia.org/wiki/D%27Hondt_method)
  quotas the party got. A party
  is guaranteed a seat for each quota it gets, and may receive more.
  This can be used as a measure of how close a party is to getting a seat.
* **Seats** - how many seats the party got out of the total available
* **Graph** - a bargraph of the party's vote share in a region
""")
        return h

#---------------------------------------------------------------------

class PredMixin:
    """ Mixin for classes containing predicted results """

    def titleH(self):
        h = ("<h1>European Election 2014 prediction - %s</h1>\n\n"
             % (self.area.title,))
        return h

    def desc(self): return ""

    def yearStr(self):
        """ this defaults to the 2009 result, and is over-ridden for
        predicted results """
        return "2014 prediction"

    def swingExplanation(self):
        """ explain swings used. Defaults to nothing, for 2009 results """
        return "<p>Swings: %s</p>" % (self.sw.html(),)

    def getPartyA(self, aParty):
        """
        @param aParty [Party]
        @return [str] containing an <a href>..</a> html segment
            which gives a link to the party. For predicted results,
            this url is to /pred_party/<p> giving the swing.
        """
        h = ("<a href='/pred_party/%s%s'>%s</a>"
             % (aParty.ab, self.sw.queryString(), aParty.name))
        return h

#---------------------------------------------------------------------

class PredRResult(PredMixin, RResult):
    """ Predicted Regional Result """

    def __init__(self, fromRes, sw):
        """
        @param fromRes [RResult] the regional result from which we are
            making the prediction
        @param sw [Swing] the swings from (fromRResult)
        """
        self.fromRes = fromRes
        self.sw = sw

        self.area = fromRes.area
        self.electorate = fromRes.electorate
        self.totSeats = fromRes.totSeats
        predPartyVotes = {}
        existingParties = [pab for pab,v in fromRes.pVotes]
        for pab, v in fromRes.pVotes:
            if sw.sd.has_key(pab):
                predPartyVotes[pab]  = max(int(v +
                    fromRes.totVotes*sw.sd[pab]/10000.0 +0.5), 0)
            else:
                predPartyVotes[pab] = v
        for pab, delta in sw.sd.items():
            if pab not in existingParties and self.willStandHere(pab):
                predPartyVotes[pab] = max(int(
                    fromRes.totVotes*sw.sd[pab]/10000.0 + 0.5), 0)
        self.setPartyVotes(predPartyVotes.items())

#---------------------------------------------------------------------

class AgResult(EResult):

    def __init__(self, a, regionResults=None):
        """
        @param a [Aggregation]
        @param regionResults [dict of str:EResult] to get regional
            results from. For aggregates of 2009 results, this will be
            our global variable (eResults) which is what it defaults to.
        """
        self.area = a
        if regionResults==None:
            regionResults = eResults
        self._accumulateRegions(regionResults)

    def _accumulateRegions(self, regionResults):
        self.totSeats = 0
        self.totVotes = 0
        self.electorate = 0
        totPartyVotes = collections.defaultdict(int)
        totPartySeats = collections.defaultdict(int)
        for region in self.area.getRegions():
            rr = regionResults[region.ab]
            self.totSeats += rr.totSeats
            self.totVotes += rr.totVotes
            self.electorate += rr.electorate
            for pab, v, _, s, _ in rr.resultTable:
                totPartyVotes[pab] += v
                totPartySeats[pab] += s
            #//for
        #//for
        self.calcResultTable(totPartyVotes.items(), totPartySeats)

    def listRegions(self):
        """ list my subregions (for html) """
        h = "<p>%s is made up of these regions: " % (self.area.name,)
        for region in self.area.getRegions():
            rr = eResults[region.ab]
            h += rr.nameInUrl() + ", "
        h = h[:-2]
        return h

    def makePrediction(self, sw):
        """ Make a prediction
        @param sw [Swing]
        @return [AgResult]
        """
        predResult = PredAgResult(self, sw)
        return predResult
        #-----
        regionalPredictions = {}
        for rab in area.regionAbs:
            regionalPredictions[rab] = getAreaResult(rab).makePrediction(sw)
        predResult = AgResult(self.area, regionalPredictions)
        return predResult

    def htmlResultsTable(self):
        h = ("<table class='results'>\n<tr>"
            "<th colspan=2>Party</th>\n"
            "<th>Votes</th>\n"
            "<th>%Vote</th>\n"
            "<th>Seats</th>\n"
            "<th>%Seats</th>\n"
            "<th>Graph</th>\n"
            "</tr>\n")

        for pab,v,pcv,s,pcs in self.resultTable:
            theParty = party.getParty(pab)
            line = "<tr>"
            line += ("<td style='background:#%(partyCol)s;'>&nbsp;</td>\n"
                "   <td>%(party)s</td>\n"
                "   <td align=right>%(v)s</td><td align=right>%(pcv)6.2f</td>\n"
                "   <td align=right>%(s)d</td>\n"
                "   <td align=right>%(pcs)6.2f</td>\n"
                "   <td class=barGraph>%(bar)s</td>\n") % {
                'partyCol': theParty.col,
                'party': self.getPartyA(theParty),
                'v':     thousands(v),
                'pcv':   pcv,
                's':     s,
                'pcs':   pcs,
                'bar':   htmlhelp.barGraph(pcv, theParty.col),}
            line += "</tr>\n"
            h += line
        #//for
        h += ("<tr class='totalLine'><td></td>\n"
            "   <td style='border-left:0px;'>Total</td>\n"
            "   <td align=right><b>%(v)s</b></td>\n"
            "   <td align=right>%(pcv)6.2f</td>\n"
            "   <td align=right>%(s)d</td>\n"
            "   <td align=right>%(pcs)6.2f</td>\n"
            "   <td></td>\n"
            "</tr>\n") % {
            'v':   thousands(self.totVotes),
            'pcv': 100.0,
            's':   self.totSeats,
            'pcs': 100.0,}
        h += "</table>\n\n"

        h += htmlhelp.md("""Key:

* **Votes** - the votes a party got
* **%Vote** - the percentage of total votes the party got
* **Seats** - how many seats the party got
* **%Seats** - the percentage of seats the party got
* **Graph** - a bargraph of the party's vote share
""")
        return h
#---------------------------------------------------------------------

class PredAgResult(PredMixin, AgResult):
    """ predicted Aggregate result """

    def __init__(self, fromRes, sw):
        """
        @param fromRes [RResult] the regional result from which we are
            making the prediction
        @param sw [Swing] the swings from (fromRResult)
        """
        self.fromRes = fromRes
        self.sw = sw
        self.area = fromRes.area

        regionalPredictions = {}
        for rab in area.regionAbs:
            regionalPredictions[rab] = getAreaResult(rab).makePrediction(sw)
        self._accumulateRegions(regionalPredictions)

    def listRegions(self):
        """ list my subregions (for html) """
        h = "<p>%s is made up of these regions: " % (self.area.name,)
        for region in self.area.getRegions():
            rr = eResults[region.ab]
            h += "<a href='/pred_result/%s%s'>%s</a>, " % (
                 rr.area.ab, self.sw.queryString(), rr.area.name)
        h = h[:-2]
        return h

#---------------------------------------------------------------------

def makeAggregateResults():
    """ for each area.Aggregation, make a correponding AgResult """
    for areaAb, a in area.areas.items():
        if isinstance(a, area.Aggregation):
            agr = AgResult(a)
            eResults[areaAb] = agr

#---------------------------------------------------------------------
# results for a party

def regionalResults(pab, sw=None):
    """ return regional results for a player
    @param pab [str]
    @param sw [Swing] if None this is a 2009 result, if there is
        a Swing object, it's a prediction
    @return list of (result, votes, pcVotes, q, seats, seatsInRegion)
                    ::(EResult,int,float,float,int,int)
            sorted by decreasing q
    (q) is the number of quotas a party got, = (totS+1)*pcv/100
    """
    lines = []
    for rab in area.regionAbs:
        rr = getAreaResult(rab, sw)
        rtLines = [rtLine for rtLine in rr.resultTable if rtLine[0]==pab]
        if len(rtLines) >= 1:
            _,v,pcv,s,pcs = rtLines[0]
            q = (rr.totSeats + 1)*pcv/100.0
            line = (rr, v, pcv, q, s, rr.totSeats)
            lines.append(line)
    def pcvCmp(a,b):
        return cmp(a[2], b[2])
    lines.sort(pcvCmp, reverse=True)
    return lines

def aggregateResults(pab, sw=None):
    """ return aggregate results for a player
    @param pab [str]
    @param sw [Swing] if None this is a 2009 result, if there is
        a Swing object, it's a prediction
    @return list of (result, votes, pcVotes, seats, seatsInRegion)
                    ::(EResult,int,float,int,int)
    """
    lines = []
    for rab in area.aggregationAbs:
        rr = getAreaResult(rab, sw)
        rtLines = [rtLine for rtLine in rr.resultTable if rtLine[0]==pab]
        if len(rtLines) >= 1:
            _,v,pcv,s,pcs = rtLines[0]
            line = (rr, v, pcv, s, rr.totSeats)
            lines.append(line)
    return lines

def resultsForPartyHtml(pab, sw=None):
    """ return html containing results for a party.
    @param pab [str] party abbreviation
    @param sw [Swing] if None this is a 2009 result, if there is
        a Swing object, it's a prediction
    @return [str]
    """
    p = party.getParty(pab)
    isPrediction = (sw!=None)
    year = 2014 if isPrediction else 2009
    h = ("<%(header)s>%(predRes)s in %(year)d for %(party)s</%(header)s>\n\n"
         % {'header': "h1" if isPrediction else "h2",
            'predRes': "Prediction" if isPrediction else "Result",
            'year': year,
            'party': p.name})
    if isPrediction:
        h += "Based on swings: %s\n\n" % sw.html()

    regRes = regionalResults(pab, sw)
    agRes = aggregateResults(pab, sw)
    h += "<table class='results'>\n" + htmlhelp.trHeaders("Region",
        "Votes", "%Vote", "Quotas", "Seats", "Graph")
    totVotes = totRegionVotes = totSeatsWon = totSeatsFought = 0
    multiplier = None
    for r, v, pcv, q, s, totS in regRes:
        if multiplier==None:
            multiplier = max(30.0/(pcv+1), 1.0)
        h += htmlhelp.tr(
            r.nameInUrl(sw),
            thousands(v),
            "%6.2f" % pcv,
            "%5.2f" % q,
            "%d/%d" % (s, totS),
            htmlhelp.barGraph(multiplier*pcv, p.col),
            align="lrrrr")
        totVotes += v
        totRegionVotes += r.totVotes
        totSeatsWon += s
        totSeatsFought += totS
    try:
        barGraphH = htmlhelp.barGraph(
            multiplier*100.0*totVotes/totRegionVotes, p.col)
    except:
        barGraphH = ""
    h += htmlhelp.tr("<b>Total</b>",
        "<b>%s</b>" % thousands(totVotes),
        "<b>%s</b>" % pcStr(totVotes, totRegionVotes),
        "",
        "<b>%d/%d</b>" % (totSeatsWon, totSeatsFought),
        barGraphH,
        trClass="totalLine",
        align = "lrrrr")
    #h += "</table>\n"

    #h += "<table class='results'>\n" + htmlhelp.trHeaders("Aggregation",
    #    "Votes", "% Votes", "Seats", "Graph")

    for r, v, pcv, s, totS in agRes:
        try:
            barGraphH = htmlhelp.barGraph(
                multiplier*pcv, p.col)
        except:
            barGraphH = ""
        h += htmlhelp.tr(
            "<i>%s</i>" % r.nameInUrl(sw),
            thousands(v),
            "%6.2f" % pcv,
            "",
            "%d/%d" % (s, totS),
            barGraphH,
            align="lrrrr")
    h += "</table>\n\n"

    h += """<p>Key:</p>
<ul>
<li><b>Votes</b> - the votes the party got in that region</li>
<li><b>%Vote</b> - the percentage of total votes in that region the party got</li>
<li><b>Quotas</b> - the number of
<a href="http://en.wikipedia.org/wiki/D%27Hondt_method">d'Hondt</a>
quotas the party got.
A party is guaranteed a seat for each quota it gets, and may receive more.
This is a measure of how close a party is to getting a seat.</li>
<li><b>Seats</b> - how many seats the party got out of the total available</li>
<li><b>Graph</b> - a bargraph of the party's vote share in a region</li>
</ul>
"""
    return h



#---------------------------------------------------------------------
# load results

theRegAb = None
theRegInfo = None

def reg(regAb):
    global theRegAb
    theRegAb = regAb

def regInfo(votes, turnout, seats):
    global theRegInfo
    theRegInfo = (votes, turnout, seats)

def eres(**partyVotes):
    """ uses (theRegAb) and (theRegInfo) to create a RResult.
    Puts the result in eResults
    """
    a = area.areas[theRegAb]
    votes, turnout, seats = theRegInfo
    elec = int(votes*100.0/turnout + 0.5)
    rr = RResult(a, elec, seats)
    rr.setPartyVotes(partyVotes.items())
    eResults[theRegAb] = rr

reg("scot")
regInfo(votes=1104512, turnout=28.5, seats=6)
eres(snp=321007, lab=229853, con=185794, ld=127038,
       green=80442,
       ukip=57788,
       bnp=27174,
       slp=22135,
       christ=16738,
       ssp=10404,
       i_rob=10189,
       no2eu=9693,
       jury=6257)


reg("wales")
regInfo(votes=684520, turnout=30.4, seats=4)
eres(con=145193, lab=138852, pc=126702, ukip=87585,
       ld=73082,
       green=38160,
       bnp=37114,
       christ=13037,
       slp=12402,
       no2eu=8600,
       jury=3793)


reg("ni")
regInfo(votes=438469, turnout=42.8, seats=3)
eres(sf=126184, dup=88346, uu=82893,
       sdlp=78489,
       tuv=66197,
       alli=26699,
       green=15764)


reg("nee") # North East England
regInfo(votes=589862, turnout=30.4, seats=3)
eres(lab=147338, con=116911, ld=103644,
       ukip=90700,
       bnp=52700,
       green=34081,
       ed=13007,
       slp=10238,
       no2eu=8066,
       christ=7263,
       libert=3010,
       jury=2904)

reg("nwe") # North West England
regInfo(votes=1651825, turnout=31.7, seats=8)
eres(con=423174, lab=336831, ukip=261740, ld=235639, bnp=132194,
       green=127133,
       ed=40027,
       slp=26224,
       christ=25999,
       no2eu=23580,
       jury=8783,
       libert=6980,
       i_apaloo=3621)

reg("york") # Yorkshire and the Humber
regInfo(votes=1226180, turnout=32.3, seats=6)
eres(con=299802, lab=230009, ukip=213750, ld=161552, bnp=120139,
       green=104456,
       ed=31287,
       slp=19380,
       christ=16742,
       no2eu=15614,
       jury=7181,
       libert=6268)

reg("em") # East Midlands
regInfo(votes=1228065, turnout=37.1, seats=5)
eres(con=370275, lab=206945, ukip=201184, ld=151428,
       bnp=106319,
       green=83939,
       ed=28498,
       ukf=20561,
       christ=17907,
       slp=13590,
       no2eu=11375,
       libert=7882,
       jury=7362)

reg("wm") # West Midlands
regInfo(votes=1413036, turnout=34.8, seats=7)
eres(con=396847, ukip=300471, lab=240201, ld=170246,
       bnp=121967,
       green=88244,
       ed=32455,
       christ=18784,
       slp=14724,
       no2eu=13415,
       jury=8721,
       libert=6961)

reg("ee") # East of England
regInfo(votes=1603340, turnout=37.7, seats=7)
eres(con=500331, ukip=313921, ld=221235, lab=167833,
       green=141016,
       bnp=97013,
       ukf=38185,
       ed=32211,
       christ=24646,
       no2eu=13939,
       slp=13599,
       animal=13201,
       libert=9940,
       i_rigby=9916,
       jury=6354)


reg("see") # South East England
regInfo(votes=2334858, turnout=37.5, seats=10)
eres(con=812288, ukip=440002, ld=330340, green=271506, lab=192592,
       bnp=101769,
       ed=52526,
       christ=35712,
       no2eu=21455,
       libert=16767,
       slp=15484,
       ukf=15261,
       jury=14172,
       peace=9534,
       roman=5450)

reg("swe") # South West England
regInfo(votes=1549708, turnout=38.8, seats=6)
eres(con=468742, ukip=341845, ld=266253,
       green=144179,
       lab=118716,
       bnp=60889,
       pen=37785,
       ed=25313,
       christ=21329,
       mebyon=14922,
       slp=10033,
       no2eu=9741,
       i_hopkins=8971,
       libert=7292,
       fpft=7151,
       jury=5758,
       wai=789)

reg("london") # London
regInfo(votes=1751026, turnout=33.3, seats=8)
eres(con=479037, lab=372590, ld=240156, green=190589, ukip=188440,
       bnp=86420,
       christ=51336,
       i_jan=50014,
       ed=24477,
       no2eu=17758,
       slp=15306,
       libert=8444,
       jury=7284,
       i_cheung=4918,
       social=4050,
       yes2eu=3384,
       i_rahman=3248,
       i_alcan=1972,
       i_saad=1603)

makeAggregateResults()


#end
