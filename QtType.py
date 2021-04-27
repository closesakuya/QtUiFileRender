from bs4 import BeautifulSoup, element
import re


class QtStyleSheet(dict):

    PT_ELEMENT = re.compile(r'(\n|^|})([\w\d:#!\s]+)([\n]?{)([\d\w\/\.\(\)\[\]+-:#;_\n\s\t\\t]+)(})')
    PT_ELEMENT_NAME = re.compile(r'#[\w\d_-]+($|:)')

    def __init__(self, src: str):
        super(QtStyleSheet, self).__init__({})
        self.__src = src  # .replace(' ', '')
        self.__abs_key = {}  # 记录元素值包含具体对象时提取的包含对象名的元素名
        res = re.findall(self.PT_ELEMENT, self.__src)
        for item in res:
            key = item[1].replace("\n", "").replace("\t", "").replace(" ", "")
            key_2 = re.sub(self.PT_ELEMENT_NAME, "", key)
            self[key] = {}
            if key_2 != key:
                self.__abs_key[key_2] = True
                self[key_2] = self[key]
            values = item[3].replace("\n", "").replace("\t", "").split(";")
            for v in values:
                # print(v)
                vs = v.split(":")
                if vs.__len__() >= 2:
                    self[key][vs[0].replace(" ", "")] = ":".join(vs[1:])

        # 查找{}外的元素
        temp_s = re.sub(self.PT_ELEMENT, "", self.__src).replace("\n", "").replace("\t", "")\
            .split(";")
        # print(temp_s)
        for item in temp_s:
            vs = item.split(":")
            if vs.__len__() >= 2:
                self[vs[0].replace(" ", "")] = ":".join(vs[1:])

    def __getitem__(self, item):
        try:
            return super(QtStyleSheet, self).__getitem__(item)
        except KeyError:
            key = re.sub(self.PT_ELEMENT_NAME, "", item)
            return super(QtStyleSheet, self).__getitem__(key)

    def __setitem__(self, key, value):
        try:
            return super(QtStyleSheet, self).__setitem__(key, value)
        except KeyError:
            key = re.sub(self.PT_ELEMENT_NAME, "", key)
            return super(QtStyleSheet, self).__setitem__(key, value)

    @staticmethod
    def loads(src: str):
        return QtStyleSheet(src)

    def to_string(self) -> str:
        s = ""
        for k, v in self.items():
            if isinstance(v, dict):
                if self.__abs_key.get(k, None) is True:
                    continue
                s += "{0}\n{{\n".format(k)
                for sub_k, sub_v in v.items():
                    s += "    {0}:{1};\n".format(sub_k, sub_v)
                s += "}\n"
            else:
                s += "{0}:{1};\n".format(k, v)
        return s

    def dump(self, dist_file: str):
        try:
            with open(dist_file, "w+", encoding="utf-8") as f:
                f.write(self.to_string())
        except Exception as e:
            print("dump Qt stylesheet failed ", e)



class QtUiObject:
    def __init__(self, src: element.Tag):
        # object.__setattr__(self, "__tag", src)
        self.__tag = src
        self.__ori = None

    @staticmethod
    def loads(src: str):
        a = BeautifulSoup(src, "html.parser")
        # print(src)
        obj = QtUiObject(a.ui.widget)
        obj.__ori = a
        return obj

    def to_string(self):
        return self.__ori.__str__()

    def dump(self, dst: str):
        if not self.__ori:
            raise Exception("pls use 'QtUiObject.loads()' to generate instance\n")
        with open(dst, "w+", encoding="utf-8") as f:
            f.write(self.to_string())

    def to_bs4element(self):
        return self.__tag
    def __str__(self):
        return self.__tag.__str__()

    def __getattribute__(self, item):
        try:
            return super(QtUiObject, self).__getattribute__(item)
        except AttributeError:
                res = self.__tag.find(re.compile("property|widget"), {"name": item})
                if not res:
                    res = self.__tag.find(item)
                if res:
                    return QtUiObject(res)
                else:
                    raise AttributeError("not found property: {0} in ui file".format(item))

    def get(self, key):
        return self.__getattribute__(key)

    def find(self, name):
        try:
            return self.get(name)
        except:
            for item in self.sub_widget():
                res = item.find(name)
                if res:
                    return res

    # @property
    def content(self):
        try:
            st = self.string.__str__()
        except AttributeError:
            st = self.__tag.__str__()
        res = re.search(re.compile(r'(?<=>).*?(?=<)', re.DOTALL), st)
        if res:
            return res.group()

    def sub_widget(self):
        # print(self.__tag["name"])
        for m_item in self.__tag.find_all("widget", recursive=False):
            # print(m_item["name"])
            yield QtUiObject(m_item)

    def set(self, key, value):
        res = self.__tag.find(re.compile("property|widget"), {"name": key})
        if not res:
            res = self.__tag.find(key)

        if not res:
            # return super(QtUiObject, self).__setattr__(key, value)
            print("not found key: {0} in qt ui object".format(key))
            # TODO 暂不支持添加property Tag 只能在property中添加属性
            self.__tag.append(BeautifulSoup("<{key}>{value}</{key}>".format(key=key, value=value), "html.parser"))
            return

        if isinstance(value, QtUiObject):
            self.__tag.__setattr__(key, value.__tag)
        else:
            res.string = value.__str__()

    def gen_obj_by_marker(self, marker: str, attr_name: str="whatsThis"):
        cur_marker = None
        try:
            cur_marker = self.get(attr_name).string
        except AttributeError:
            pass
        # print(cur_marker)
        if cur_marker is not None and re.findall(re.compile(marker), cur_marker.__str__()):
            yield self

        # 查找子窗口 递归
        for sub in self.sub_widget():
            for sub_j in sub.gen_obj_by_marker(marker, attr_name):
                if sub_j:
                    yield sub_j


"""
if __name__ == "__main__":
    with open("sysset.ui", "r+", encoding="utf-8") as f:
        s = f.read()
        a = QtUiObject.loads(s)
        # a.geometry.rect.set("x",99999)
        # a.m_range_1_name.geometry.set("xss", 999)
        # print(a.m_range_1_name.geometry)
        # a.dump("test.html")
        for item in a.gen_obj_by_marker("TITLE"):

            # print(item.to_bs4element()["name"])
            # item.styleSheet.set("string", "hahaha")
            # (item.styleSheet)
            style = item.styleSheet.content()
            style = QtStyleSheet(style)

            # print(style.to_string())
            style.dump("heihei.txt")
"""



