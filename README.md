# simplified_traditional_convert
用于转换中文简繁体转换的小工具
运行环境：window, python3

命令行
python convert.py -i dir -m [zh-hans|zh-hant]
-i 需要进行繁简转换目录路径或文件
-m 转换模式 zh-hans：转换为简体，zh-hant：转换为繁体，默认转换繁体
--ignore 忽略文件或列表，可以是文件名或者目录，如果是目录的话，需要绝对路径

注意:
convert默认支持转换lua和xml文件，如果要支持其他文件可以修改convert.py文件中
suffixs = ('.lua', '.xml');
