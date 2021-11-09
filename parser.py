from lxml import etree as et


# from xml.etree import ElementTree as et

tree = et.parse("./sample/xmlTest.ghx")
root = tree.getroot()


# def fetch_branch(temp_root, tag, att_key, att_val):
#     temp_root.iter
#     for c in temp_root:
#         if att_key in c.attrib.keys():
#             v = c.attrib[att_key]
#             if v == att_val:
#                 return c
#     return None

# def print_contents(temp_root):
#     print(temp_root.tag, temp_root.attrib)
#     for c in temp_root:
#         print("\t", c.tag, c.attrib)


# print_contents(root)
# # _Definition = fetch_branch(root, "chunks")
# # print(root.tag, root.attrib)
# # for c in root:
# #     print(c.tag, c.attrib)

# # # temp = fetch_branch(root, "count", "1")
# # # print("temp: ", temp)


# for c in root.iter("item",):
#     print(c.tag, c.attrib)


