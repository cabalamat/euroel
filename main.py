# main.py = main program for neweuro

import os.path
import datetime

from flask import Flask, request
app = Flask(__name__)

import htmlhelp
import article
import swing
import area
import party
import result

#import narticle

#---------------------------------------------------------------------
# read config file

config = {}
execfile(os.path.expanduser("~phil/.euroelection/config"), {}, config)


#---------------------------------------------------------------------

def body(h, title="Euro Election 2014", leftBarHtml=None):
    """ encapsulate an html body """
    adsenseCode = """
<script type="text/javascript">//<!--
google_ad_client = "ca-pub-3404409487381930";
/* Euroelection ad */
google_ad_slot = "4187864486";
google_ad_width = 120;
google_ad_height = 600;
//-->
</script>
<script type="text/javascript" src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
</script>
"""
    if config['debug']:
        #adsenseCode = "<br><img src='http://placekitten.com/g/120/600'>"
        adsenseCode = ""
    navbar = """\
<div class="navbar">
  <div class="navbar-inner">
    <div class="container">

      <a class="brand" href="/">Euro Election 2014</a>
      <ul class="nav">
        <li><a href="/eresult/uk">2009 Result</a></li>
        <li><a href="/allparties">Parties</a></li>
        <li><a href="/make_prediction">Predict</a></li>
        <li><a href="/blog/">Blog</a></li>
      </ul>
    </div><!--container-->
  </div>
</div>
"""
    if leftBarHtml==None:
        leftbar = area.leftbarHtml()
    else:
        leftbar = leftBarHtml

    googleAnalytics = """\
<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-37997302-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>
"""
    if config['debug']: googleAnalytics = ""

    rightBar = """\
<a class="twitter-timeline"
   href="https://twitter.com/EUElection2014"
   data-widget-id="299157656554323968">Tweets by @EUElection2014</a>
<script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="//platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>
"""
    #rightBar = "this is the right bar."

    footer = """\
<br><br><br><br>
Disclaimer: The government says we have to tell you that this site uses cookies. If you
don't like that, you're free to not use it.
"""
    footer = ""

    before = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>%(title)s</title>
  <link href="/static/bs/united-bootstrap.min.css" rel="stylesheet">
  <style type="text/css">
    body {
      //padding-top: 60px;
      padding-bottom: 40px;
    }
    .sidebar-nav {
      padding: 9px 0;
    }
  </style>
  <link href="/static/bs/bootstrap-responsive.css" rel="stylesheet">
  <link href="/static/style.css" rel="stylesheet">
  <link rel="shortcut icon" href="/static/favicon4.ico">
</head><body>

%(navbar)s

<div class="container">
  <div class="row">
    <div class="span2 leftBar">
       %(leftbar)s
       <br>
       %(adsenseCode)s
    </div>
    <div class="span7 mainPanel">
""" % {
    'title': title,
    'navbar': navbar,
    'leftbar': leftbar,
    'adsenseCode': adsenseCode,
}
    after = """\
    </div>
    <div class="span3 rightBar">
       %(rightBar)s
    </div>
  </div>
</div>
<div class="container">
  <div class="row">
    <div class="offset1 span10 footer">
      %(footer)s
    </div>
  </div>
</div>
%(analytics)s</body></html>
""" % { 'footer': footer,
        'rightBar': rightBar,
        'analytics': googleAnalytics}
    return before + h + after

#---------------------------------------------------------------------

@app.route('/')
def hello_world():
    today = datetime.date.today()
    electionDay = datetime.date(2014,5,22)
    daysToElection = (electionDay - today).days
    head = """\
<h1>Euro Election 2014</h1>

<p class='electionDays'><b>%(numDays)d</b>
days to<br>election day<sup>*</sup></p>

<p>The next election to the European Parliament will be in May 2014.
This site aims to be a resource for that election in the UK.</p>

<p>(<b>*</b> We don't yet know for certain when the election will take
place. It will probably be on Thursday 22th May, which is
in %(numDays)d days time.)</p>
""" % {'numDays': daysToElection }

    rest = """\
<h2>You can:</h2>
<ul>
<li>Look at <a href="/eresult/uk">the 2009 result</a>, for the UK or by region</li>
<li>See the <a href="/allparties">parties and independents</a> who stood in that election</li>
<li><a href="/make_prediction">Make a prediction</a> for 2014</li>
<li>Read the
<a href="/article/about_euro_election_2014">About</a> page or the
<a href="/article/frequently_asked_questions">Frequently Asked Questions</a></li>
</ul>

<h2>Useful links</h2>

<ul>
<li>The 2009 European Parliament election
<a href="http://en.wikipedia.org/wiki/European_Parliament_election,_2009">throughout Europe</a> and
<a href="http://en.wikipedia.org/wiki/European_Parliament_election,_2009_%28United_Kingdom%29">in the UK</a>.</li>
<li>Don't know which European Parliamentary region you live in? Look it up on
<a href="http://mapit.mysociety.org/">MapIt</a>.</li>
<li><a href="http://www.europarl.europa.eu/portal/en">European Parliament</a> website</li>
</ul>

"""
    return body(head + rest)

#---------------------------------------------------------------------

@app.route('/allparties')
def allPartiesHtml():
    pabs = party.parties.keys()
    pabs.sort()
    partiesHtml = "<br>\n".join([party.getParty(pab).titleInUrl()
                                 for pab in pabs])
    h = """<h1>List of all parties</h1>

<p><i>This is a list of all the parties, lists, and independents that stood in 2009
or that intend to stand in 2014 (as far as we know).</i></p>

%s""" % partiesHtml
    return body(h)

#---------------------------------------------------------------------

@app.route('/party/<p>')
def partyHtml(p):
    theParty = party.getParty(p)
    h = theParty.html() + result.resultsForPartyHtml(p)
    return body(h,
                title = theParty.title + " | Euro Election 2014")

#---------------------------------------------------------------------

@app.route('/eresult/<a>')
def electionResult(a):
    """ show the election result for an area """
    theArea = area.areas[a]
    h = result.getAreaResult(a).html()
    return body(h,
                title = "2009 result in " + theArea.name)

#---------------------------------------------------------------------

def predForm(*formItem):
    h = """<form action="/pred_result/uk" method=GET><table class=results>\n"""
    h += "\n".join(formItem)
    h += """</table></form>\n\n"""
    return h

def partySup(pab, rab="gb"):
    p = party.getParty(pab)
    r = result.getAreaResult(rab)
    notes = ""
    if rab != "gb": notes = "in %s only" % r.area.name
    h = ("""<tr>
        <td style='background:#%(pCol)s'>&nbsp;&nbsp;</td>
        <td>&nbsp;<a href="/party/%(pab)s">%(pName)s</a></td>
        <td align=right>%(pcVotes)6.2f</td>
        <td><input type="text" id="%(pab)s" name="%(pab)s" size="6"></td>
        <td><i>%(notes)s</i></td>
    </tr>\n""" % {
    'pCol': p.col,
    'pab': pab,
    'pName': p.name,
    'pcVotes': r.forParty(pab)[2],
    'notes': notes,})
    return h

@app.route('/make_prediction')
def makePrediction():
    """ display form allowing user to make a prediction """
    h = """<h1>Make your prediction</h1>\n\n
<p>For each party, say how much support you think it will get.
"20" means 20% of the votes,
"+5" means 5% more than 2009,
"-6" means 6% less than 2009.</p>\n
    """
    divider = ("<tr>"
        + "<td colspan=4><div style='background-color:#bbb; width:100%; height:1px; margin:4px 0 4px 0;'></div></td>"
        + "</tr>")
    divider2 = ("<tr>"
        + "<td colspan=5><div style='background-color:#fff; width:100%; height:1px; margin:4px 0 4px 0;'></div></td>"
        + "</tr>")
    form = predForm(
        ("""<tr><th colspan=2>Party</th>
         <th>2009<br>result</th>
         <th>Support<br>(+/-)</th>
         <th>In regions</th>
         </tr>"""),
        #divider2,
        partySup("con"),
        partySup("ukip"),
        partySup("lab"),
        partySup("ld"),
        partySup("green"),
        partySup("bnp"),
        partySup("pir"),
        #divider2,
        partySup("snp", "scot"),
        partySup("ed", "eng"),
        partySup("pc", "wales"),
        #divider2,
        ("""<tr>
        <td colspan=5 align=center style='padding:3px;'>
        <button type='submit' class='btn btn-primary' name='send'><b>Make Prediction</b></button></td>
        </tr>""")
        )

    h += form
    return body(h, title="Prediction | Euro Election 2014")

#---------------------------------------------------------------------

@app.route('/pred_result/<a>')
def predResult(a):
    """ make a prediction for a particular region. The Swings for
    the prediction go in the query string
    """
    sw = swing.Swing(request.args)
    actualResult = result.getAreaResult(a)
    predictedResult = actualResult.makePrediction(sw)
    h = predictedResult.html()
    leftbarHtml = area.leftbarHtml("/pred_result/", sw.queryString())
    return body(h,
                "2014 prediction in " + actualResult.area.name,
                leftbarHtml)

#---------------------------------------------------------------------

@app.route('/pred_party/<p>')
def predParty(p):
    """ Show the results of a prediction for a party, in each
    region (i.e. similar to /party/<p> but for predictions)
    """
    sw = swing.Swing(request.args)
    theParty = party.getParty(p)
    h = result.resultsForPartyHtml(p, sw)
    leftbarHtml = area.leftbarHtml("/pred_result/", sw.queryString())
    return body(h,
                "2014 prediction for " + theParty.title,
                leftbarHtml)

#---------------------------------------------------------------------

@app.route('/article/<a>')
def showArticle(a):
    """ Show an article """
    h = article.articles[a].html()
    return body(h,
                title=article.articles[a].name + " | Euro Election 2014",
                leftBarHtml=article.leftBarHtml)

#---------------------------------------------------------------------

@app.route('/articles')
def showArticles():
    """ Show a list of all articles """
    keys = article.articles.keys()
    keys.sort()
    h = "<h1>List of articles</h1>\n\n"
    for key in keys:
        art = article.articles[key]
        h += "<a href='/article/%s'>%s</a><br>\n" % (key, art.name)
    '''
    h += htmlhelp.md("""##Debugging information""")
    h += htmlhelp.evals('os.path.abspath(".")')
    h += htmlhelp.evals('os.listdir("/home/phil/proj/euroelection")')
    '''
    return body(h,
                title="List of articles | Euro Election 2014",
                leftBarHtml="&nbsp;")

#---------------------------------------------------------------------
'''
@app.route('/narticle/<id>')
def showNArticle(id):
    """ Show an article """
    theNarticle = narticle.articles[id]
    return body(theNarticle.html(),
                title = theNarticle.title
                        + " | Euro Election 2014",
                leftBarHtml = theNarticle.leftBarHtml())

@app.route('/narticles')
def showNArticles():
    """ Show a list of all articles """
    keys = narticle.articles.keys()
    keys.sort()
    h = "<h1>List of NEW articles</h1>\n\n"
    for key in keys:
        art = narticle.articles[key]
        h += art.getA() + "<br>\n"
    return body(h,
                title="List of NEW articles | Euro Election 2014",)
'''
#---------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=config['debug'])

#end
