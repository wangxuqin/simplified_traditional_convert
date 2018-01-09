# simplified_traditional_convert
用于转换中文简繁体转换的小工具  
运行环境：window, python3  

命令行  
python convert.py -i dir -m [zh-hans|zh-hant] --ignore[file|dir] --suffixs[format]
*-i 需要进行繁简转换目录路径或文件
*-m 转换模式 zh-hans：转换为简体，zh-hant：转换为繁体，默认转换繁体
*--ignore 忽略文件或列表，可以是文件名或者目录，如果是目录的话，需要绝对路径(多个文件目录使用';'分割)
*--suffixs 需要转换的文本文件格式，如果为空则会转换所有文本文件(多个文件格式使用';'分割)
例子:
python convert.py -i C:\Users\KimWang\Desktop\test --ignore test.txt;test.xml --suffixs txt;xml;json