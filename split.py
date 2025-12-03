#%%
import re
import os
import tqdm

def split_and_save(input_file, encoding, out_dir):
	os.makedirs(out_dir, exist_ok=True)

	with open(input_file, "r", encoding=encoding) as f:
		lines = f.readlines()

	new_lines = []
	chapter_num = 1
	for line in lines:
		# 去除特殊符号
		# line = line.replace("\u3000", "").replace("\xa0", "").replace("\ufeff", "")
		# line = line.strip()
		if line.startswith("第") and re.match(r"第.+?章", line) or \
			line.startswith("完本感言") or \
			line.startswith("番外"):
		# if line.startswith("第") and re.match(r"第.+?章", line):
			if len(new_lines) > 0:
				with open(f"{out_dir}/{chapter_num}.txt", "w", encoding=encoding) as f:
					f.writelines(new_lines)
				chapter_num += 1
			new_lines = [line]
		else:
			new_lines.append(line)
	with open(f"{out_dir}/{chapter_num}.txt", "w", encoding=encoding) as f:
		f.writelines(new_lines)


def split_chapters_and_volumes(input_file, encoding, out_dir):
	os.makedirs(out_dir, exist_ok=True)
	with open(input_file, "r", encoding=encoding) as f:
		lines = f.readlines()
	new_lines = []
	chapter_num = 0
	volume_num = 1
	ttl_num = 0
	first_chapter = False
	for line in tqdm.tqdm(lines):
		if line.startswith("第"):
			if re.match(r"第.卷", line):
				if len(new_lines) > 0:
					# with open(f"{out_dir}/{ttl_num}-{volume_num}-{chapter_num}.txt", "w", encoding=encoding) as f:
					with open(f"{out_dir}/{ttl_num}.txt", "w", encoding=encoding) as f:
						f.writelines(new_lines)
					volume_num += 1
					chapter_num = 1
					ttl_num += 1
				first_chapter = True
				new_lines = [line]
			else:
				if first_chapter:
					new_lines.append(line)
					first_chapter = False
				else:
					# with open(f"{out_dir}/{ttl_num}-{volume_num}-{chapter_num}.txt", "w", encoding=encoding) as f:
					with open(f"{out_dir}/{ttl_num}.txt", "w", encoding=encoding) as f:
						f.writelines(new_lines)
					new_lines = [line]
					chapter_num += 1
					ttl_num += 1
		else:
			if "<img" in line:
				parts = line.split("<img")
				line = parts[0]
			new_lines.append(line)
	
	# with open(f"{out_dir}/{ttl_num}-{volume_num}-{chapter_num}.txt", "w", encoding=encoding) as f:
	with open(f"{out_dir}/{ttl_num}.txt", "w", encoding=encoding) as f:
		f.writelines(new_lines)


#%% 
file_path = "《 》.txt"
out_dir = "《 》"
split_and_save(file_path, "utf-8", out_dir)


# %%
file_path	= ".txt"
out_dir		= ""
split_chapters_and_volumes(file_path, "utf-8", out_dir)



# %%
