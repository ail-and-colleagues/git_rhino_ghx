from parse import parse
from lxml import etree as et

def string_parser(pattern, src):
    return parse(pattern, src)

def fetch_children_by_attrib(cur, attrib):
    children = cur.xpath("./*")
    ret = list()
    for c in children:
        if c.xpath(attrib):
            ret.append(c)
    return ret


def fetch_descendants_by_attrib(cur, attrib):
    children = cur.xpath(attrib)
    if children:
        return [cur]
    else:
        children = cur.xpath("./*")
        ret = list()
        for c in children:
            ret += fetch_descendants_by_attrib(c, attrib)
        return ret

def fetch_ancestor_by_attrib(cur, attrib):
    parent = cur.xpath("..")
    if not parent:
        return None
    else:
        # print("fetch_parent_by_attrib tag: ", parent[0].tag, ", attrib:", parent[0].attrib)
        ret = parent[0].xpath(attrib)
        if ret:
            return parent[0]
        else:
            return fetch_ancestor_by_attrib(parent[0], attrib)


def print_contents(cur, silent=False):
    def chk(t):
        if t is None:
            return False
        if  t[0] == "\n":
            return False
        return True
    ret = "tag: {}, attrib: {}".format(cur.tag, cur.attrib)
    if chk(cur.text):
        ret += ", text: {}".format(cur.text) 
    if not silent:
        print(ret)
    return ret


class Line_to_Xml_Element:
    def __init__(self):
        self.is_end = False
        self.map = list()
        self.depth = 0
        self.element_idx = -1
        self.depth_element_idx = dict()
        self.br_count = 0
    def start(self, tag, attrib):
        self.depth += 1
        self.element_idx += 1
        # print("start: ", tag, attrib)
        self.depth_element_idx[self.depth] = self.element_idx
        # print("depth_element_idx: ", self.depth_element_idx)
    def end(self, tag):
        self.is_end = True
        # print("end: ", tag)
    def data(self, data):
        self.br_count = data.count("\n")
        # print("data: ", data, ", br_count: ", self.br_count )
        cur_idx = self.depth_element_idx[self.depth]
        self.map += [cur_idx] * self.br_count
        if self.is_end:
            self.depth += -1
            self.is_end = False
    def close(self):
        # Add idx(s) because data() does not be called on the last line.
        cur_idx = self.depth_element_idx[self.depth]
        self.map += [cur_idx] * self.br_count
        # Insert "-1" for the skipped first line "<?xml version=~".
        self.map = [-1] + self.map
        # print("map: ", self.map)
        return self.map