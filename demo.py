#!/usr/bin/env python
"""Colorize the SVG by modifying the XML directly, via ElementTree."""
from __future__ import absolute_import, division, print_function
import random
import sys
from xml.etree import ElementTree as ET

import yaml


class ShapeStyle(object):
    base_styles = {
        "fill": "#cccccc",
        "fill-rule": "evenodd",
        "stroke": "#222222",
        "stroke-width": "2px",
        "stroke-linecap": "butt",
        "stroke-linejoin": "miter",
        "stroke-opacity": 1,
    }

    def __init__(self, styles):
        styles = dict(styles)
        # Safety dance
        for k in styles:
            if k not in self.base_styles:
                raise ValueError("Unexpected style: %s" % k)
        self._styles = self.base_styles.copy()
        self._styles.update(styles)

    def __getitem__(self, key):
        return self._styles[key]

    def __setitem__(self, key, value):
        assert key in self._styles
        self._styles[key] = value

    def __str__(self):
        return ';'.join("%s:%s" % (k, v)
                        for k, v in sorted(self._styles.iteritems()))


def intensity2color(scale):
    """Interpolate from pale grey to deep red-orange.

    Boundaries:

        min, 0.0: #cccccc = (204, 204, 204)
        max, 1.0: #ff2000 = (255, 32, 0)
    """
    assert 0.0 <= scale <= 1.0
    baseline = 204
    max_rgb = (255, 32, 0)
    new_rbg = tuple(baseline + int(round(scale * (component - baseline)))
                    for component in max_rgb)
    return new_rbg


def rgb2hex(rgb):
    return "#%02x%02x%02x" % rgb


def hex2rgb(hexstr):
    assert (isinstance(hexstr, basestring) and
            hexstr.startswith('#') and
            len(hexstr) == 7
            ), "need a 24-bit hexadecimal string, e.g. #000000"

    rgb_hex24 = hexstr[1:3], hexstr[3:5], hexstr[5:]
    return tuple(int('0x' + cc, base=16) for cc in rgb_hex24)


def all_labels(obj):
    """Flatten a YAML/JSON-sourced dict/list object tree.

    Returns all internal and external node labels in DFS pre-order.
    """
    def iter_dict(dc):
        for k, v in dc.iteritems():
            yield k
            if isinstance(v, dict):
                for key in iter_dict(v):
                    yield key
            else:
                for val in v:
                    yield val

    assert isinstance(obj, dict)
    for key in iter_dict(obj):
        yield key


def leaf_labels(obj):
    """Get terminal node labels from a YAML/JSON-sourced dict/list object tree.

    Returns only terminal node labels in DFS order.
    """
    def iter_dict(dc):
        for k, v in dc.iteritems():
            if not v:
                yield k
            elif isinstance(v, dict):
                for key in iter_dict(v):
                    yield key
            else:
                for val in v:
                    yield val

    assert isinstance(obj, dict)
    for key in iter_dict(obj):
        yield key



if __name__ == '__main__':
    # Take region names from the vocabulary definition file
    with open("maps/robot/robot.yaml") as f:
        vocab_tree = yaml.load(f)
    labels = set(leaf_labels(vocab_tree))
    print(labels, file=sys.stderr)

    # Load the SVG as an XML tree
    tree = ET.ElementTree(file="maps/robot/robot.plain.svg")
    for element in tree.iter():
        if element.get("id") in labels:
            # Set the "style" attribute's fill value to a random heat color
            intensity = random.random()
            style = ShapeStyle({"fill": rgb2hex(intensity2color(intensity))})
            element.set("style", str(style))

    # Serialize the XML back to an SVG file
    tree.write("robot-randheat.svg")
    print("Wrote", "robot-randheat.svg", file=sys.stderr)
