#%%
import os
import tqdm
import pyttsx3

def pick_chinese_voice(engine):
	voices = engine.getProperty('voices')
	candidates = []
	for v in voices:
		langs = getattr(v, 'languages', []) or []
		langs = [x.decode('utf-8','ignore') if isinstance(x, (bytes, bytearray)) else str(x)
				for x in langs]
		text = (' '.join(langs) + ' ' + (getattr(v,'name','') or '') + ' ' + (getattr(v,'id','') or '')).lower()
		keys = ['zh', 'zh-cn', 'zh_cn', 'zh-hk', 'zh_tw', 'chinese', 'mandarin', 'ting-ting', 'mei-jia', 'sin-ji']
		if any(k in text for k in keys):
			candidates.append(v)
	if not candidates:
		raise RuntimeError("未找到中文语音，请在系统设置的 Spoken Content 中下载 Ting-Ting/Mei-Jia/Sin-Ji 后重试")
	return candidates[0]

text_dir	= "《 》"
out_dir		= "《 》_audiobook"

os.makedirs(out_dir, exist_ok=True)
file_names = os.listdir(text_dir)
# file_names = sorted(file_names, key=lambda x: int(x.split("-")[0]))
file_names = sorted(file_names, key=lambda x: int(x.split(".")[0]))

voice = None
rate = 220
volume = 1.0

def text_to_speech(file_name, text_dir, out_dir, voice, rate, volume):
	ebook_file_name = os.path.join(out_dir, file_name.replace(".txt", ".aiff"))
	with open(os.path.join(text_dir, file_name), "r", encoding="utf-8") as f:
		text = f.read()
	engine = pyttsx3.init()
	if voice is not None:
		engine.setProperty('voice', voice)
	else:
		cn_voice = pick_chinese_voice(engine)
		engine.setProperty('voice', cn_voice.id)
	engine.setProperty('rate', rate)
	engine.setProperty('volume', volume)
	engine.save_to_file(text, ebook_file_name)
	engine.runAndWait()
	engine.stop()
	del engine
	return ebook_file_name

for file_name in tqdm.tqdm(file_names[350:400]):
	if not file_name.endswith(".txt"):
		continue
	text_to_speech(file_name, text_dir, out_dir, voice, rate, volume)


# import concurrent.futures
# for file_name in tqdm.tqdm(file_names[350:360]):
# 	if not file_name.endswith(".txt"):
# 		continue
# 	try:
# 		with concurrent.futures.ProcessPoolExecutor() as executor:
# 			future = executor.submit(
# 				text_to_speech, file_name, text_dir, out_dir, voice, rate, volume
# 			)
# 			result = future.result(timeout=600)  # 600秒即10分钟
# 	except Exception as e:
# 		print(f"{file_name} 语音转换超时/失败，已跳过。原因：{e}")
# 		fail_file = os.path.join(text_dir, file_name.replace(".txt", ".aiff"))
# 		if os.path.exists(fail_file):
# 			os.remove(fail_file)  # 删除问题文件



# %%
