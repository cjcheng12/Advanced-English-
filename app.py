import streamlit as st
import random
import json
import os
import datetime
import base64
from gtts import gTTS
from io import BytesIO

# --- 1. CONFIGURATION ---
PROGRESS_FILE = "vocab_progress_spaced.json"
MASTERY_THRESHOLD = 6

# --- 2. VOCABULARY DATABASE (保持不變) ---
VOCAB_DB = {
    # ... (此處省略您原本長長的單字表以節省空間，請直接延用原本的資料庫內容) ...
    "aberrant": {"def": "異常的，脫軌的", "distractors": ["正常的", "標準的", "受歡迎的"], "sent": "His aberrant behavior worried his parents."},
    # 這裡請保留您原本的所有單字數據
}

# --- 3. HELPER FUNCTIONS ---

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}

def save_progress(progress):
    try:
        with open(PROGRESS_FILE, "w") as f:
            json.dump(progress, f)
    except Exception as e:
        st.error(f"存檔失敗: {e}")

def get_audio_html(text):
    """保證 iPad 相容的音訊嵌入法"""
    try:
        tts = gTTS(text, lang='en')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_bytes = fp.read()
        b64 = base64.b64encode(audio_bytes).decode()
        # 建立 HTML5 音訊標籤
        audio_html = f"""
            <div style="text-align: center; margin: 10px 0;">
                <audio controls style="width: 80%;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    您的瀏覽器不支援音訊播放。
                </audio>
            </div>
        """
        return audio_html
    except Exception as e:
        return f"<p style='color:red;'>音訊生成錯誤: {e}</p>"

def initialize_game():
    progress = load_progress()
    available_words = [w for w in VOCAB_DB.keys() if progress.get(w, {'score': 0})['score'] < MASTERY_THRESHOLD]
    
    if not available_words:
        st.session_state.game_over = True
        st.session_state.game_words = []
        return

    game_words = random.sample(available_words, min(len(available_words), 20))
    st.session_state.game_words = game_words
    st.session_state.current_index = 0
    st.session_state.session_score = 0
    st.session_state.game_over = False
    st.session_state.progress = progress
    st.session_state.answered = False
    st.session_state.current_word_tracker = None

# --- 4. STREAMLIT APP LAYOUT ---

st.set_page_config(page_title="AI 背單字神器", page_icon="📖")
st.title("📚 Spaced Repetition Vocab")
st.markdown("針對 iPad 優化版。**規則：** 每個單字每天僅限獲得 +1 熟練度。")

if "game_words" not in st.session_state:
    initialize_game()

# --- GAME OVER SCREEN ---
if st.session_state.get("game_over", False) or not st.session_state.get("game_words"):
    st.balloons() # 所有的都背完時噴氣球
    st.success("🎉 太棒了！本輪練習已完成（或所有單字皆已達標）")
    if "session_score" in st.session_state:
        st.metric(label="本輪得分", value=f"{st.session_state.session_score} / {len(st.session_state.game_words)}")
    
    if st.button("開始新一輪練習"):
        for key in ["game_words", "current_index", "session_score", "game_over", "answered"]:
            if key in st.session_state: del st.session_state[key]
        st.rerun()
    st.stop()

# --- GAME LOGIC ---
try:
    current_word = st.session_state.game_words[st.session_state.current_index]
    word_data = VOCAB_DB[current_word]
except IndexError:
    st.session_state.game_over = True
    st.rerun()

# 初始化當前題目
if st.session_state.current_word_tracker != current_word:
    options = word_data["distractors"] + [word_data["def"]]
    random.shuffle(options)
    st.session_state.options = options
    st.session_state.current_word_tracker = current_word
    st.session_state.answered = False
    st.session_state.result_msg = ""

# 顯示單字與音訊
st.markdown(f"<h1 style='text-align: center; color: #4CAF50;'>{current_word}</h1>", unsafe_allow_html=True)

# iPad 相容音訊
st.markdown(get_audio_html(current_word), unsafe_allow_html=True)

st.write("---")

# 選項按鈕
if not st.session_state.answered:
    cols = st.columns(2)
    for i, option in enumerate(st.session_state.options):
        if cols[i % 2].button(option, key=f"btn_{i}", use_container_width=True):
            st.session_state.answered = True
            if option == word_data["def"]:
                st.session_state.last_result = "correct"
                st.session_state.session_score += 1
                
                today_str = str(datetime.date.today())
                w_prog = st.session_state.progress.get(current_word, {'score': 0, 'last_date': ''})
                
                if w_prog['last_date'] != today_str:
                    w_prog['score'] += 1
                    w_prog['last_date'] = today_str
                    st.session_state.result_msg = "✅ 回答正確！熟練度 +1"
                else:
                    st.session_state.result_msg = "☑️ 回答正確！（今日已獲得過分數）"
                
                st.session_state.progress[current_word] = w_prog
                save_progress(st.session_state.progress)
            else:
                st.session_state.last_result = "wrong"
                st.session_state.result_msg = "❌ 答錯了，再接再厲！"
            st.rerun()

# 反饋介面
else:
    if st.session_state.last_result == "correct":
        st.success(st.session_state.result_msg)
    else:
        st.error(st.session_state.result_msg)
        st.info(f"**正確定義：** {word_data['def']}")
        st.markdown(f"**例句：** *{word_data['sent']}*")

    curr_score = st.session_state.progress.get(current_word, {'score': 0})['score']
    st.progress(min(curr_score / MASTERY_THRESHOLD, 1.0))
    st.caption(f"目前熟練度: {curr_score}/{MASTERY_THRESHOLD}")

    if st.button("下一個單字 ➡️", type="primary"):
        st.session_state.current_index += 1
        if st.session_state.current_index >= len(st.session_state.game_words):
            st.session_state.game_over = True
        st.rerun()

# 側邊欄
with st.sidebar:
    st.header("學習進度")
    st.write(f"題目： {st.session_state.current_index + 1} / {len(st.session_state.game_words)}")
    st.write(f"本輪得分： {st.session_state.session_score}")
    
    st.divider()
    
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            st.download_button("💾 下載進度備份", f, file_name=PROGRESS_FILE)
            
    if st.button("⚠️ 重置所有學習紀錄"):
        if os.path.exists(PROGRESS_FILE): os.remove(PROGRESS_FILE)
        st.session_state.progress = {}
        st.warning("進度已清除")
