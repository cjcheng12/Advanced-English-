import streamlit as st
import random
import datetime
from upstash_redis import Redis
from gtts import gTTS
from io import BytesIO
import json

# =========================================================
# 1) 初始化雲端資料庫 (請確保 Secrets 已設定)
# =========================================================
@st.cache_resource
def get_redis():
    try:
        return Redis(
            url=st.secrets["UPSTASH_REDIS_REST_URL"],
            token=st.secrets["UPSTASH_REDIS_REST_TOKEN"]
        )
    except:
        st.error("❌ 雲端資料庫連線失敗，請檢查 Streamlit Secrets 設定。")
        return None

redis = get_redis()

# =========================================================
# 2) 配置與單字庫
# =========================================================
MASTERY_THRESHOLD = 6
WORDS_PER_SESSION = 20  # 固定每局 20 題

# 這裡使用您提供的 VOCAB_DB ...
VOCAB_DB = {
    "aberrant": {"def": "異常的，脫軌的", "distractors": ["正常的", "標準的", "受歡迎的"], "sent": "His aberrant behavior worried his parents."},
    "abstinence": {"def": "節制，禁慾", "distractors": ["放縱", "暴飲暴食", "參與"], "sent": "The doctor recommended total abstinence from alcohol."},
    "acerbic": {"def": "尖刻的，酸澀的", "distractors": ["甜蜜的", "溫和的", "讚美的"], "sent": "He wrote an acerbic review of the movie."},
    # ... (請保留您原始代碼中所有的單字數據)
}

# =========================================================
# 3) 數據處理邏輯
# =========================================================
def load_progress_cloud():
    if not redis: return {}
    try:
        data = redis.get("user_progress")
        if data is None: return {}
        return json.loads(data) if isinstance(data, str) else data
    except: return {}

def save_progress_cloud(progress):
    if not redis: return
    try:
        redis.set("user_progress", json.dumps(progress))
    except Exception as e:
        st.warning(f"⚠️ 儲存進度時發生錯誤: {e}")

@st.cache_data(show_spinner=False, ttl=3600)
def tts_mp3_bytes_cached(text: str):
    try:
        tts = gTTS(text, lang="en")
        fp = BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except: return None

def initialize_game():
    progress = load_progress_cloud()
    # 挑選未達標的單字
    available = [w for w in VOCAB_DB.keys() if progress.get(w, {}).get("score", 0) < MASTERY_THRESHOLD]
    
    if not available:
        st.session_state.game_over = True
        return

    # 隨機挑選 20 題 (若不足 20 則全選)
    num_to_pick = min(len(available), WORDS_PER_SESSION)
    selected_words = random.sample(available, num_to_pick)
    
    st.session_state.update({
        "game_words": selected_words,
        "current_index": 0,
        "session_score": 0,
        "game_over": False,
        "progress": progress,
        "answered": False,
        "current_word_tracker": None
    })

# =========================================================
# 4) 遊戲 UI
# =========================================================
st.set_page_config(page_title="Vocab Mastery", page_icon="🎓")

if "game_words" not in st.session_state:
    initialize_game()

# --- 遊戲結束畫面 ---
if st.session_state.get("game_over", False):
    st.balloons()
    st.success("🎉 遊戲結束！")
    
    # 顯示總分
    final_score = st.session_state.get("session_score", 0)
    total_q = len(st.session_state.get("game_words", []))
    
    col1, col2 = st.columns(2)
    col1.metric("本次得分", f"{final_score} / {total_q}")
    col2.metric("正確率", f"{(final_score/total_q)*100:.1f}%" if total_q > 0 else "0%")

    if st.button("再戰 20 題", type="primary"):
        for k in ["game_words", "current_index", "session_score", "game_over"]:
            if k in st.session_state: del st.session_state[k]
        initialize_game()
        st.rerun()
    st.stop()

# --- 遊戲進行中 ---
curr_idx = st.session_state.current_index
total_qs = len(st.session_state.game_words)
curr_word = st.session_state.game_words[curr_idx]
word_data = VOCAB_DB[curr_word]

# 進度條
st.caption(f"題目 {curr_idx + 1} / {total_qs}")
st.progress((curr_idx + 1) / total_qs)

# 單字與語音
st.markdown(f"<h1 style='text-align:center; color:#1E88E5;'>{curr_word}</h1>", unsafe_allow_html=True)

# 💡 新增：在題目中顯示例句
st.markdown(f"<p style='text-align:center; font-style:italic; color:gray;'>Example: {word_data['sent']}</p>", unsafe_allow_html=True)

audio_data = tts_mp3_bytes_cached(curr_word)
if audio_data:
    st.audio(audio_data, format="audio/mp3")

# 初始化選項
if st.session_state.current_word_tracker != curr_word:
    options = word_data["distractors"] + [word_data["def"]]
    random.shuffle(options)
    st.session_state.options = options
    st.session_state.current_word_tracker = curr_word
    st.session_state.answered = False

st.write("---")

# 回答區
if not st.session_state.answered:
    cols = st.columns(2)
    for i, opt in enumerate(st.session_state.options):
        if cols[i % 2].button(opt, use_container_width=True, key=f"btn_{i}"):
            st.session_state.answered = True
            today = str(datetime.date.today())
            
            if opt == word_data["def"]:
                st.session_state.last_result = "correct"
                st.session_state.session_score += 1
                
                # 更新掌握度
                prog = st.session_state.progress.get(curr_word, {"score": 0, "last_date": ""})
                if prog["last_date"] != today:
                    prog["score"] = int(prog.get("score", 0)) + 1
                    prog["last_date"] = today
                    st.session_state.progress[curr_word] = prog
                    save_progress_cloud(st.session_state.progress)
                    st.session_state.feedback = "✅ 正確！(掌握度 +1)"
                else:
                    st.session_state.feedback = "☑️ 正確！(今日已獲得過分數)"
            else:
                st.session_state.last_result = "wrong"
                st.session_state.feedback = f"❌ 答錯了！正確答案是：{word_data['def']}"
            st.rerun()
else:
    # 顯示反饋
    if st.session_state.last_result == "correct":
        st.success(st.session_state.feedback)
    else:
        st.error(st.session_state.feedback)
    
    if st.button("下一題 ➡️", use_container_width=True, type="primary"):
        if st.session_state.current_index + 1 < len(st.session_state.game_words):
            st.session_state.current_index += 1
            st.session_state.answered = False
        else:
            st.session_state.game_over = True
        st.rerun()

# 側邊欄統計
with st.sidebar:
    st.header("📊 學習統計")
    mastered = sum(1 for v in st.session_state.progress.values() if v.get("score", 0) >= MASTERY_THRESHOLD)
    st.write(f"已精通單字: {mastered} / {len(VOCAB_DB)}")
    
