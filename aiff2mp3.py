#%%
import os
import tqdm
from pydub import AudioSegment

aiff_dir	= "《 》_audiobook"
mp3_dir		= "《 》_audiobook_mp3"

os.makedirs(mp3_dir, exist_ok=True)

file_names = os.listdir(aiff_dir)
# file_names = sorted(file_names, key=lambda x: int(x.split("-")[0]))
# file_names = sorted(file_names, key=lambda x: int(x.split(".")[0]))

for file in tqdm.tqdm(file_names):
	if file.endswith(".aiff"):
		aiff_path = os.path.join(aiff_dir, file)
		mp3_path = os.path.join(mp3_dir, file.replace(".aiff", ".mp3"))
		audio = AudioSegment.from_file(aiff_path, format="aiff")
		audio.export(mp3_path, format="mp3")
		del audio

# %%
