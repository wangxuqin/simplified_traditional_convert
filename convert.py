# -*- coding: utf-8 -*-
import re,os,io,time,getopt,sys,codecs
from mycollections.stack import Stack
from zhtools.langconv import *

ignore_list = [] # 忽略文件目录列表
convert_success_file_list = [] # 文件转换成功列表
convert_fail_file_list = []	   # 文件转换失败列表

if not os.path.exists('./log'):
	os.mkdir('./log')
dump_file_name = './log/' + time.strftime("%Y-%m-%d.log", time.localtime())
dump_file = open(dump_file_name, 'a+')

suffixs = []; # 需要转换的文本文件后缀名，如果为空，则支持所有文本文件
zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')

def debug_dump(content):
	timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())
	print(timestamp + ' ' + content)
	dump_file.write(timestamp + ' ' + content.replace("\n", "")+'\n')

def dump_convert_file():
	global convert_success_file_list
	global convert_fail_file_list
	
	#打印转换失败文件路径
	debug_dump("convert success:")
	for filename in convert_success_file_list:
		debug_dump(filename)
	
	#打印转换成功文件路径
	debug_dump("convert fail:")
	for filename in convert_fail_file_list:
		debug_dump(filename)
	
#判断传入字符串是否包含中文
def contain_zh(word):
    global zh_pattern
    match = zh_pattern.search(word)
    return match

def comment_check(word):
	pos = word.find('--')
	if pos >= 0:
		return True
	else:
		pos = word.find(']]')
		if pos >= 0:
			return True
	return False

# 转换繁体到简体
def cht_to_chs(line):
    line = Converter('zh-hans').convert(line)
    line.encode('utf-8')
    return line

# 转换简体到繁体
def chs_to_cht(line):
    line = Converter('zh-hant').convert(line)
    line.encode('utf-8')
    return line

# 根据给定模式进行繁简转换
def convert_by_mode(line, mode):
	newLine = line
	if mode == 'zh-hant':
		newLine = chs_to_cht(line);
	else:
		newLine = cht_to_chs(line);
	return newLine

# 获取后缀名
def file_extension(path): 
	suffix = os.path.splitext(path)[1]
	if len(suffix) > 0:
		suffix = suffix.lower()
	return suffix

# 注释过滤注释
def comment_filter(line, stack, mode):
	sections = []
	start = 0
	while True:
		if stack.is_empty():
			bPos = line.find('--[[', start)
			lPos = line.find('--', start)
			
			if bPos == -1 and lPos == -1: # 没有注释
				sections.append(convert_by_mode(line[start:], mode))
				break
			
			# 存在 '--' 同时'--'在'--[['的前面，或者不存在'--[[',此时注释类型为行注释
			elif lPos >= 0 and (lPos < bPos or bPos == -1): 
				sections.append(convert_by_mode(line[start:lPos], mode))
				sections.append('--')
				stack.push('--')
				start = lPos + 2
			
				if stack.top() == '--':
					stack.pop()
					sections.append(line[start:])
					break
			
			elif bPos >= 0: # 块注释
				sections.append(convert_by_mode(line[start:bPos], mode))
				sections.append('--[[')
				stack.push('--[[')
				start = bPos + 4
				
				ePos = line.find(']]', start);
				if ePos >= 0: #如果找到闭合符号，则弹出栈顶元素'--[['
					sections.append(line[start:ePos])
					sections.append(']]');
					stack.pop()
					start = ePos + 2
			
		elif stack.top() == '--[[':
			ePos = line.find(']]', start);
			if ePos >= 0: #如果找到闭合符号，则弹出栈顶元素'--[['
				sections.append(line[start:ePos])
				sections.append(']]');
				stack.pop()
				start = ePos + 2
			else:
				sections.append(line[start:])
				break;
			
	result = ''.join(sections)
	return result
	
# 将文件中文按照要求进行转换
def convert_file(filename, mode):
	global convert_success_file_list
	global convert_fail_file_list
	
	print('convert file:'+filename)
	try:
		if not os.path.exists(filename):
			return
		
		if (filename in ignore_list) \
		or (os.path.basename(filename) in ignore_list):
			debug_dump('ignore file:'+filename);
			return
		
		isContainHans = False
		records = []
		newLines = []
		lineCount = 0
		stack = Stack()
		
		with codecs.open(filename, 'r', 'utf-8') as f:
			for line in f.readlines():
				lineCount = lineCount + 1
				
				if contain_zh(line) or comment_check(line):
					if file_extension(filename) == '.lua': # 如果是lua文件则需要过滤注释，注释不用进行繁简转换
						newLine = comment_filter(line, stack, mode)
					else:
						newLine = convert_by_mode(line, mode)
					
					newLines.append(newLine)
					if newLine != line:
						isContainHans = True
						records.append({'line':lineCount, 'old':line, 'new':newLine})
				else:
					newLines.append(line)
		
		if isContainHans:
			debug_dump(filename)
			convert_success_file_list.append(filename)
			with codecs.open(filename, 'w', 'utf-8') as f:
				f.writelines(newLines)
			
			for record in records:
				debug_dump('line :'+ str(record['line']))
				debug_dump('old  :'+ record['old'])
				debug_dump('new  :'+ record['new'])
				debug_dump('');
	except Exception as msg:
		convert_fail_file_list.append(filename)
		debug_dump('path:' + filename + ' is failed!!!')
		debug_dump('reason:' + str(msg))
		debug_dump('')

# 遍历目录
def foreach_dir_convert(dir, mode):
	global suffixs
	
	if not os.path.isdir(dir):
		return
	
	if dir in ignore_list: # 如果在忽略列表
		debug_dump('ignore dir:'+dir)
		return
	
	allTextFormat = (len(suffixs) == 0) # 如果suffixs为空，则表示需要转换所有文本文件格式的文件
	
	files = [os.path.join(dir, name) for name in os.listdir(dir)
			if os.path.isfile(os.path.join(dir, name)) \
			and (allTextFormat or (file_extension(name) in suffixs))];
	
	dirs  = [os.path.join(dir, name) for name in os.listdir(dir)
			if os.path.isdir(os.path.join(dir, name)) ];
	
	for file in files:
		convert_file(file, mode)
	
	for d in dirs:
		foreach_dir_convert(d, mode)

# 将指定路径下所有lua文件和xml文件的中文按照要求转换
def convert(path, mode):
	if not os.path.exists(path):
		debug_dump('path: '+ path + ' is not exists!!!');
		return
	
	if os.path.isdir(path):
		foreach_dir_convert(path, mode)
	
	elif os.path.isfile(path):
		convert_file(path, mode)
# 处理后缀名	
def suffixs_handle(value):
	global suffixs
	list = value.split(';')
	for suffix in list:
		if suffix[0] != '.':
			suffix = '.' + suffix
		suffixs.append(suffix)

def ignore_list_handle(value):
	global ignore_list
	paths = value.split(';')
	for path in paths:
		if os.path.isdir(path):
			ignore_list.append(os.path.abspath(path))
		else:
			ignore_list.append(path)
	
	debug_dump('ignore_list:')
	for item in ignore_list:
		debug_dump(item)
	debug_dump('')
			
modes = ('zh-hans', 'zh-hant')
def main(argv):
	
	path = ''
	mode = 'zh-hant'
	
	try:
		options, args = getopt.getopt(argv, "i:m:", ['suffixs=', 'ignore='])
	except getopt.GetoptError:
		sys.exit()
	for option, value in options:
		if option == '-i':
			path = value;
		elif option == '-m':
			if value in modes:
				mode = value
		elif option == '--suffixs':
			suffixs_handle(value)
		elif option == '--ignore':
			ignore_list_handle(value)
		
		
	convert(path, mode)
	dump_convert_file()

if __name__ == '__main__':
	dump_file.write('------------------------' + time.strftime("%Y-%m-%d.log", time.localtime()) + '-----------------------\n')
	main(sys.argv[1:])
	dump_file.close()