import QtType


class Render:
    def __init__(self, stylesheet: str):
        self.env = {}
        try:
            with open(stylesheet, "r+", encoding="utf8") as f:
                s = f.read()
                try:
                    l_env = {}
                    exec(s, l_env)
                    if isinstance(l_env.get("__ALL__", None), dict):
                        self.env.update(l_env["__ALL__"])
                except Exception as e:
                    print("exec ", stylesheet, "failed, E: ", e)
        except FileNotFoundError:
            pass
        # print("use render script", self.env)

    def do_render(self, src: str, dst: str):
        print("render ", src, " to ", dst)
        ori_s = None
        with open(src, "r", encoding="utf-8") as f:
            ori_s = f.read()
        if ori_s is None:
            raise Exception("open {0} failed !\n".format(src))
        qt_obj = QtType.QtUiObject.loads(ori_s)

        for k, v in self.env.items():
            self.render_stylesheet_by_format(qt_obj, k, v)

        qt_obj.dump(dst)
        return True

    @staticmethod
    def render_stylesheet_by_format(obj: QtType.QtUiObject, obj_marker: str,
                                    fmt_style: str, marker_key: str = "whatsThis"):
        fmt_style = QtType.QtStyleSheet(fmt_style)

        for item in obj.gen_obj_by_marker(obj_marker, marker_key):
            inst_style = QtType.QtStyleSheet(item.styleSheet.content())
            for k, v in fmt_style.items():
                if isinstance(v, dict):
                    if inst_style.get(k, None) is None:
                        inst_style[k] = {}
                    for sub_k, sub_v in v.items():
                        inst_sub_v = inst_style[k].get(sub_k, None)
                        if inst_sub_v is None:
                            continue
                        assert isinstance(sub_v, str)
                        inst_style[k][sub_k] = sub_v
                elif isinstance(v, str):
                    if inst_style.get(k, None) is None:  # 不允许{}外部添加属性
                        continue
                    inst_style[k] = v
                else:
                    raise Exception("not support type {0} of {1}".format(type(v), k))

            item.styleSheet.set("string", inst_style.to_string())

