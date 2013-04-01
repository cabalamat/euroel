# htmlhelp.py = helper functions for html

import os, os.path
import markdown

#---------------------------------------------------------------------

def ul(*listItems):
    inner = "".join([li(item) for item in listItems])
    h = "<ul>\n%s</ul>\n" % inner
    return h

def li(s):
    return "<li>" + s + "</li>\n"

def barGraph(vpc, col):
    """ an html bar graph of the vote share in percent """
    if col=="" or col=="fff": col = "888"
    h = ("<div style='valign: center; "
         "background-color:#%s; width:%dpx; height:19px;'></div>"
         % (col, int(vpc*6+0.5)))
    return h

def tr(*tds, **flags):
    """ outputs <tr><th>a header</th>...</tr>
    param tds [list of str]
    """
    align = flags.get("align", "")
    trClass = flags.get("trClass", "")
    if trClass:
        trClass = " class='%s'" % trClass
    h = "<tr%s>" % trClass
    for ix, td in enumerate(tds):
        alignStr = ""
        if len(align)>ix:
            alignChar = align[ix]
            if alignChar=='r': alignStr = " align=right"
            if alignChar=='c': alignStr = " align=center"
        h += "<td%s>%s</td>\n" % (alignStr, td)
    h += "</tr>\n"
    return h

def trHeaders(*hs):
    """ outputs <tr><th>a header</th>...</tr>
    param hs [list of str]
    """
    h = ("<tr>"
         + "".join(["<th>%s</th>\n" % h for h in hs])
         + "</tr>\n")
    return h

def md(s):
    """ Convert markdown to html """
    md = markdown.Markdown()
    h = md.convert(s)
    return h

def evals(s):
    """ execute a string and produce useful output, for debugging """
    value = eval(s)
    h = "<p>%s = <tt>%r</tt></p>\n" % (s, value)
    return h

#---------------------------------------------------------------------


#end
