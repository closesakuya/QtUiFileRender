## Quickstart

**用途**

本工具通过在qt的ui文件中增加标记符号，对控件进行归类后，套用统一模板对同类控件渲染成统一样式。

**使用方法**

```python
python3 main.py renderall --file_dir="my_ui_files_dir" --output="my_result"
```

--help 获取帮助

**renderall**  ->用于渲染整个个文件路径下的所有.ui文件

 | --file_dir:路径地址 

| --output:结果存放路径地址

 | ----stylesheet: 渲染使用的模板文件路径地址



**renderfile** ->用于渲染单个.ui文件 



**关于模板文件格式**

模板文件为python格式，内容如下:

```python
#存放所有模板类的字典，其中key为在ui文件中的标记，默认使用ui中
#的"whatsthis"属性进行标记;value为将该标记渲染的QtStyleSheet文本
#注: 替换不是简单的复制，会与原ui文件进行单条比对，只增改不会删除
__ALL__ = \  
    {
        "TITLE": """
        QFrame{
        background-color: yellow;
        border-image:url(:/images/mytitle.png;
        }
        """,
        "BTN_01": """
        background-color: transparent;
        color:#FFFFFF;
        """
```

在qt中标记位置如图

![hint](res\hint.png)





## **进阶使用**

本模块通过解析qt的ui文件，将其反序列化为xml文件树；同时将qt的StyleSheet文本反序列化为类似字典结构，方便在代码中修改。具体使用方式如下:



```python
from QtType import QtUiObject, QtStyleSheet

# 打开要渲染的ui格式文件
with open("myuifile.ui", "r+", encoding="utf-8") as f: 
    s = f.read()
    # 将文件内容加载，完成反序列化
    obj = QtUiObject.loads(s) 
    
    # 获取到第一个btn_01控件对象的text属性值(只查找第一层)
    print(obj.btn_01.text) 
    
    # 递归查找
    print(obj.find("sub_btn_01").text) 
    
    # 改变对象text属性值
    obj.btn_01.geometry.set("x", 999)
    obj.btn_01.text.set("string", "change")
    
    #将改变后的对象序列化为字符串
    obj_str = obj.btn_01.to_string()
    
    #将修改后的整个对象输出到文件
    obj.dump("result.ui")
    
    #通过标记查找所有该标记为'TITLE'的对象(返回生成器)
    for item in obj.gen_obj_by_marker(marker="TITLE"，
                                     attr_name="whatsThis"):
        print(item)
       
   	#对qtstylesheet文本反序列化为对象
    q_style_text = obj.btn_01.styleSheet.content()
    q_style_obj = QtStyleSheet(q_style_text)
    
    #读取、修改对应属性值
    print(q_style_obj["color"])
    q_style_obj["QButton"]["color"] = "#FFFFFF"
    q_style_obj["QButton:!enable"]["color"] = "#AAAAAA"
    
    #序列化为字符串，并写进ui对象的stylesheet属性
    obj.btn_01.styleSheet.set("string", q_style_obj.to_string())
        
```