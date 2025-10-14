#%%
import re

def extract_chinese_numbers(text):
	# 匹配中文数字（不含单位词，可根据需要自行添加）
	pattern = r'[零一二三四五六七八九十百千]+'
	results = re.findall(pattern, text)
	if results:
		return results
	else:
		return []


def chinese_to_arabic(chinese_num):
	chinese_digits = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, 
					'五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
	chinese_units = {'十': 10, '百': 100, '千': 1000}

	num = 0
	unit = 1
	i = len(chinese_num) - 1
	while i >= 0:
		c = chinese_num[i]
		if c in chinese_units:
			unit = chinese_units[c]
			if i == 0 or chinese_num[i-1] not in chinese_digits:
				num += unit  # 处理如“十”=10，“百”=100这种前面没有数字的情况
		elif c in chinese_digits:
			num += chinese_digits[c] * unit
			unit = 1
		i -= 1
	return str(num)


def compare_title(str1, str2, diff=1):
	if str1 == str2: return str1
	# let str1 be longer than str2
	if len(str1) < len(str2): str1, str2 = str2, str1
	if len(str1) - len(str2) > diff: return False
	i = j = 0
	diff_found = False
	while i < len(str1) and j < len(str2):
		if str1[i] != str2[j]:
			if not diff_found:
				diff_found = True
				i += 1
				continue
			else:
				return False
		i += 1
		j += 1
	return str1
	

def process_file(input_file, output_file):
	with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
		lines = f.readlines()

	new_lines = []
	chapter_name = ''
	for line in lines:
		if "(" in line: line = line.replace("(", "（")
		if ")" in line: line = line.replace(")", "）")
		if line.startswith("第") and re.match(r"第.+?章", line):
			line = line.strip()
			compare = compare_title(line, chapter_name)
			if compare: 
				line = compare
				# remove chapter_name from new_lines
				for i in range(len(new_lines)-1, -1, -1):
					if new_lines[i] == chapter_name+"\n":
						new_lines.pop(i)
						break
			chapter_name = line
			new_lines.append('\n')
			new_lines.append(line + '\n')
		# if the line only contains multiple "="
		elif line.strip().count('=') >= 10:
			continue
		elif line.startswith("番外"):
			new_lines.append('\n')
			new_lines.append(line)
		elif line == "\n" or line.strip() == "\n" or line.strip() == "":
			continue
		elif line.startswith('\t'):
			new_lines.append(line.strip() + '\n')
		else:
			new_lines.append('\t' + line.strip() + '\n')

	with open(output_file, "w", encoding="utf-8", errors="ignore") as f:
		f.writelines(new_lines)

if __name__ == "__main__":
	input_file = "《 》.txt"
	output_file = "《 》.txt"
	process_file(input_file, output_file)
	print(f"处理完成！结果已保存到 {output_file}")

# %%
