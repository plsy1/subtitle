mkvextract tracks 1.mkv 2:zh.srt
python clean_srt.py jp.srt
python srt_to_ass.py jp_cleaned.srt zh.srt
rm jp.srt zh.srt jp_cleaned.srt 1.mkv