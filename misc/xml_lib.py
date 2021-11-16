
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