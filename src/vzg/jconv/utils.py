# -*- coding: UTF-8 -*-
"""Beschreibung

##############################################################################
#
# Copyright (c) 2020 Verbundzentrale des GBV.
# All Rights Reserved.
#
##############################################################################
"""

# Imports
from lxml import etree
import re
from vzg.jconv.gapi import NAMESPACES

__author__ = """Marc-J. Tegethoff <marc.tegethoff@gbv.de>"""
__docformat__ = 'plaintext'

# TeX formular
TEXREX = re.compile("(\${1,2}.*\${1,2})")
# Upper case greek letters within a formula
GREEX = re.compile(r"\\up(\w+)")
# Subscript
SUBREX = re.compile(r"(\s*)(\w+)<sub>(.*?)\</sub>")
# Superscript
SUPREX = re.compile(r"(\s*)(\w+)<sup>(.*?)\</sup>")


def node2text(node):
    """Strip all text from a node and their children

    Parameters
    ----------
    node : etree._Element
        Element
    """
    stripchars = ("\n", "\t")

    # remove mml:math
    expression = "inline-formula/alternatives/mml:math"
    for mathnode in node.xpath(expression, namespaces=NAMESPACES):
        mathnode.clear()

    # remove TeX commands
    # extract the formula description

    def repl_greek(matchobj):
        gc_ = "\\"
        gc_ += matchobj.group(1)
        return gc_

    for texnode in node.iter("tex-math"):
        match = TEXREX.search(texnode.text)
        if match is not None:
            formula = match.group(1)
            formula = GREEX.sub(repl_greek, formula)
            newelem = etree.Element("tex-math")
            newelem.text = formula
            texnode.getparent().replace(texnode, newelem)

    # convert <sup> and <sub> to Tex

    nodebytes = etree.tostring(node, encoding="utf-8")
    nodetext = nodebytes.decode()

    def repl_sup(matchobj):
        gc_ = "{0}$ {1}^{{{2}}} $".format(matchobj.group(
            1), matchobj.group(2), matchobj.group(3))
        return gc_

    def repl_sub(matchobj):
        gc_ = "{0}$ {1}_{{{2}}} $".format(matchobj.group(
            1), matchobj.group(2), matchobj.group(3))
        return gc_

    nodetext = SUPREX.sub(repl_sup, nodetext)
    nodetext = SUBREX.sub(repl_sub, nodetext)

    snode = etree.fromstring(nodetext)
    nodebytes = etree.tostring(snode, encoding="utf-8", method="text")
    nodetext = nodebytes.decode()

    for c_ in stripchars:
        nodetext = nodetext.replace(c_, '')

    return nodetext
