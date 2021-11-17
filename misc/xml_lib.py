
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


def fetch_content(cur, att_key, att_val, returnOthers=False):
    # https://stackoverflow.com/questions/2243131/getting-certain-attribute-value-using-xpath
    ret = list()
    others = list()
    for c in cur:
        t = c.xpath( att_key + "=\"" + att_val + "\"")
        if t:
            ret.append(c)
        else:
            others.append(c)

    if returnOthers:
        return ret, others
    
    return ret

def fetch_content_recursive(cur, att_key, att_val):
    ret = list()
    _, cur = fetch_content(cur, att_key, att_val, returnOthers=True)

    for child in cur:
        ret.append(child)
        ret += fetch_content_recursive(child.xpath("./*"), att_key, att_val)
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