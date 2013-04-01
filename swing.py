# swing.py = swings

"""
Canonical query strings
=======================

These have typ=delta, which means all values are deltas (differences
from 2009 results) in units of 100ths of a percent. So:

   con=100

would mean conservatives up 1%.


"""

#---------------------------------------------------------------------
# helper data and functions for swings

swingPartyInfo = (
    ("con", 2774, "gb"),
    ("ukip", 1650, "gb"),
    ("lab", 1574, "gb"),
    ("ld", 1375, "gb"),
    ("green", 861, "uk"),
    ("bnp", 623, "gb"),
    ("pir", 0, "uk"),
    ("snp", 2906, "scot"),
    ("ed", 210, "eng"),
    ("pc", 1851, "wales"),
)

swingParties = [spi[0] for spi in swingPartyInfo]
pc2009 = dict([(spi[0], spi[1]) for spi in swingPartyInfo])
willStand = dict([(pab, aab) for pab,_,aab in swingPartyInfo])

def processValueStr(v):
    """ Process a value for Swing:__init__
    @param v [str]
    @return (int, str)
       [0] = value, multiplied by 100 and changed to integer
       [1] = 'delta' or 'pc' ,or '' (for unread)
    """
    v = str(v).strip()
    v0 = v[:1]
    typ = 'pc'
    if v0=="+" or v0=="-":
        typ = 'delta'
        v = v[1:]
    value = 0
    try:
        value = int(float(v)*100 +0.5)
        if value>10000: value = 10000
        if v0=="-": value = -value
    except:
        typ = ''
    return (value, typ)

#---------------------------------------------------------------------
"""
ins vars:
sd [dict str:int (pab, delta in 100ths of a %)]

"""

class Swing:
    def __init__(self, args):
        """ Create the swing. (args) is either (request.args) from
        Flask, (which behaves like a dict) or it is a string in the
        form returned by the queryString() method.
        """
        if isinstance(args, str):
            self._createFromStr(args)
        else:
            if args.get('typ', "") == "delta":
                self._createFromDeltaDict(args)
            else:
                self._createFromFormDict(args)

    def _createFromFormDict(self, args):
        sd = dict([(pab, 0) for pab in swingParties])
        for k, v in args.items():
            if k in swingParties:
                value, isDelta = processValueStr(v)
                if isDelta == 'delta':
                    sd[k] = value
                elif isDelta == "pc":
                    sd[k] = value - pc2009[k]
                else:
                    # isDelta == "", do nothing
                    pass
        #//for
        self.sd = sd

    def _createFromDeltaDict(self, args):
        sd = dict([(pab, 0) for pab in swingParties])
        for k, vs in args.items():
            if k=="typ": continue
            if k not in swingParties: continue
            try:
                vi = int(vs)
            except:
                vi = 0
            if vi>10000: vi = 10000
            if vi<-10000: vi = -10000
            sd[k] = vi
        self.sd = sd

    def _createFromStr(self, qString):
        sd = dict([(pab, 0) for pab in swingParties])
        qs = qString[1:].split("&")
        for item in qs:
            key, value = item.split("=")
            if key=="typ": continue
            valueInt = int(value)
            sd[key] = valueInt
        self.sd = sd


    def queryString(self):
        """ return a canonical query string for this Swing """
        qs = "?typ=delta"
        for pab in swingParties:
            d = self.sd[pab]
            if d!=0: qs += "&%s=%d" % (pab, d)
        return qs


    def html(self):
        """ return an html partial paragraph describing this Swing """
        h = ""
        up = "<span style='color:#080;'><b>&#9650;"
        down = "<span style='color:#a00;'><b>&#9660;"
        for pab in swingParties:
            if self.sd.has_key(pab):
                delta = self.sd[pab]
                if delta==0: continue
                upDown = up
                if delta<0: upDown = down
                h += ("%s %s %g</b></span>, "
                      % (pab, upDown, abs(delta)/100.0))
        return h[:-2]


#---------------------------------------------------------------------

#end
