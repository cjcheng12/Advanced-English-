import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import datetime
from gtts import gTTS
from io import BytesIO

# =========================================================
# 1) 配置 (CONFIG)
# =========================================================
MASTERY_THRESHOLD = 6
WORDS_PER_SESSION = 20

# 所有的單字庫 (VOCAB_DB)
VOCAB_DB = {
    "aberrant": {"def": "異常的，脫軌的", "distractors": ["正常的", "標準的", "受歡迎的"], "sent": "His aberrant behavior worried his parents."},
    "abstinence": {"def": "節制，禁慾", "distractors": ["放縱", "暴飲暴食", "參與"], "sent": "The doctor recommended total abstinence from alcohol."},
    "acerbic": {"def": "尖刻的，酸澀的", "distractors": ["甜蜜的", "溫和的", "讚美的"], "sent": "He wrote an acerbic review of the movie."},
    "addled": {"def": "糊塗的，混難的", "distractors": ["清醒的", "聰明的", "敏銳的"], "sent": "My brain is addled from lack of sleep."},
    "alluded": {"def": "暗指，影射", "distractors": ["明說", "否認", "大喊"], "sent": "He alluded to the problem but didn't mention it directly."},
    "allure": {"def": "誘惑力，魅力", "distractors": ["排斥", "醜陋", "無聊"], "sent": "The allure of the big city is strong."},
    "anecdotes": {"def": "軼事，趣聞", "distractors": ["數據", "法律條款", "悲劇"], "sent": "He told funny anecdotes about his travels."},
    "anointed": {"def": "塗油(受洗)，指定", "distractors": ["拒絕", "忽視", "懲罰"], "sent": "He was anointed as the successor."},
    "apathy": {"def": "冷漠，無動於衷", "distractors": ["熱情", "關心", "焦慮"], "sent": "Voter apathy is a problem in this election."},
    "arcane": {"def": "神秘的，晦澀難懂的", "distractors": ["淺顯的", "公開的", "簡單的"], "sent": "The ritual involved arcane symbols."},
    "asbestos": {"def": "石棉", "distractors": ["鋼鐵", "木材", "塑料"], "sent": "Asbestos removal requires safety gear."},
    "ascetic": {"def": "苦行的，禁慾的", "distractors": ["奢華的", "放縱的", "貪婪的"], "sent": "He lived a simple, ascetic life."},
    "astute": {"def": "精明的，敏銳的", "distractors": ["愚蠢的", "遲鈍的", "天真的"], "sent": "She made an astute observation about the market."},
    "atherosclerosis": {"def": "動脈粥樣硬化", "distractors": ["感冒", "骨折", "頭痛"], "sent": "Diet plays a role in atherosclerosis."},
    "auspicious": {"def": "吉利的", "distractors": ["倒霉的", "兇惡的", "悲傷的"], "sent": "It was an auspicious start to the new year."},
    "awe": {"def": "敬畏，驚嘆", "distractors": ["蔑視", "無聊", "憤怒"], "sent": "We watched in awe as the rocket launched."},
    "bane": {"def": "禍根，災星", "distractors": ["福氣", "幸運", "幫手"], "sent": "Plastic waste is the bane of our oceans."},
    "beget": {"def": "招致，產生(子女)", "distractors": ["消滅", "阻止", "隱藏"], "sent": "Violence begets violence."},
    "begrudge": {"def": "嫉妒，吝惜", "distractors": ["給予", "慷慨", "原諒"], "sent": "I don't begrudge him his success."},
    "beguiling": {"def": "迷人的，欺騙性的", "distractors": ["醜陋的", "誠實的", "無聊的"], "sent": "She has a beguiling smile."},
    "bespoke": {"def": "定製的", "distractors": ["批發的", "廉價的", "二手的"], "sent": "He wore a bespoke suit to the wedding."},
    "blight": {"def": "枯萎病，不良影響", "distractors": ["繁榮", "祝福", "健康"], "sent": "Poverty is a blight on the city."},
    "blunder": {"def": "大錯，失誤", "distractors": ["成功", "精確", "計劃"], "sent": "It was a major tactical blunder."},
    "brevity": {"def": "簡潔，短暫", "distractors": ["冗長", "持久", "永恆"], "sent": "I appreciate the brevity of your report."},
    "brim": {"def": "邊緣，充滿", "distractors": ["中心", "空虛", "底部"], "sent": "The cup was filled to the brim."},
    "brusque": {"def": "唐突的，無禮的", "distractors": ["禮貌的", "溫柔的", "耐心的"], "sent": "His manner was brusque and impatient."},
    "bungled": {"def": "搞砸，笨拙地做", "distractors": ["完善", "修復", "成功"], "sent": "They bungled the bank robbery."},
    "candid": {"def": "坦率的，直言不諱的", "distractors": ["虛偽的", "害羞的", "隱瞞的"], "sent": "To be candid, I don't like the plan."},
    "captivated": {"def": "著迷的", "distractors": ["厭惡的", "無聊的", "害怕的"], "sent": "The audience was captivated by the music."},
    "carcinogen": {"def": "致癌物質", "distractors": ["維生素", "藥物", "食物"], "sent": "Tobacco smoke contains many known carcinogens."},
    "careen": {"def": "傾斜，疾駛", "distractors": ["靜止", "爬行", "直立"], "sent": "The car careened off the road."},
    "castoff": {"def": "被遺棄的人/物", "distractors": ["寶藏", "新品", "贏家"], "sent": "He wore castoff clothes from his brother."},
    "caveat": {"def": "警告，限制條款", "distractors": ["獎金", "合同", "自由"], "sent": "There is one caveat to this deal: no refunds."},
    "charade": {"def": "偽裝，看手勢猜字", "distractors": ["真誠", "會議", "悲劇"], "sent": "His anger was just a charade."},
    "chronicling": {"def": "記錄(大事)", "distractors": ["預測", "遺忘", "銷毀"], "sent": "The book is chronicling the history of the war."},
    "clenched": {"def": "緊握，咬緊", "distractors": ["放鬆", "打開", "揮舞"], "sent": "He clenched his fists in anger."},
    "cognoscenti": {"def": "行家，鑑賞家", "distractors": ["外行", "新手", "無知者"], "sent": "The cognoscenti praised the new wine."},
    "commensurate": {"def": "相稱的，相當的", "distractors": ["不相稱的", "過多的", "缺乏的"], "sent": "Salary will be commensurate with experience."},
    "confounded": {"def": "困惑的，驚訝的", "distractors": ["明白的", "無聊的", "平靜的"], "sent": "I was confounded by the difficult puzzle."},
    "conjure": {"def": "變魔術，召喚", "distractors": ["驅散", "隱藏", "遺忘"], "sent": "The magician conjured a rabbit from the hat."},
    "consummate": {"def": "完美的，圓滿的", "distractors": ["有缺陷的", "開始的", "業餘的"], "sent": "He is a consummate professional."},
    "contemplation": {"def": "沈思，凝視", "distractors": ["忽視", "衝動", "睡眠"], "sent": "He sat in deep contemplation."},
    "contentedly": {"def": "滿足地", "distractors": ["憤怒地", "焦慮地", "悲傷地"], "sent": "The cat purred contentedly."},
    "contravened": {"def": "違反，牴觸", "distractors": ["遵守", "同意", "支持"], "sent": "The company contravened safety regulations."},
    "convalescence": {"def": "康復期", "distractors": ["惡化", "生病", "受傷"], "sent": "He needed a long convalescence after surgery."},
    "coping": {"def": "應對，處理", "distractors": ["放棄", "崩潰", "忽視"], "sent": "She is coping well with the stress."},
    "corpulent": {"def": "肥胖的", "distractors": ["瘦弱的", "強壯的", "矮小的"], "sent": "The corpulent man struggled to stand up."},
    "cosseted": {"def": "被寵愛的，嬌養的", "distractors": ["被忽視的", "被虐待的", "獨立的"], "sent": "The child was cosseted by his parents."},
    "covenant": {"def": "盟約，契約", "distractors": ["爭吵", "分歧", "建議"], "sent": "They signed a covenant to protect the land."},
    "crannies": {"def": "裂縫，縫隙", "distractors": ["平原", "山峰", "牆壁"], "sent": "Dust settled in the nooks and crannies."},
    "credulous": {"def": "輕信的，易受騙的", "distractors": ["多疑的", "精明的", "懷疑的"], "sent": "He is so credulous he believes everything."},
    "credulousness": {"def": "輕信", "distractors": ["懷疑", "智慧", "謹慎"], "sent": "His credulousness led him to lose money."},
    "cunningly": {"def": "狡猾地，巧妙地", "distractors": ["笨拙地", "誠實地", "公開地"], "sent": "The trap was cunningly hidden."},
    "curmudgeon": {"def": "脾氣壞的人", "distractors": ["樂天派", "天使", "慈善家"], "sent": "The old man was a lovable curmudgeon."},
    "dearth": {"def": "缺乏，稀少", "distractors": ["豐富", "過剩", "足夠"], "sent": "There is a dearth of good jobs here."},
    "defer": {"def": "推遲，聽從", "distractors": ["加速", "反對", "命令"], "sent": "We will defer the decision until tomorrow."},
    "demeanor": {"def": "行為，風度", "distractors": ["外貌", "衣服", "財富"], "sent": "He has a calm and professional demeanor."},
    "despondency": {"def": "沮喪，洩氣", "distractors": ["快樂", "希望", "興奮"], "sent": "He fell into a state of despondency."},
    "destitute": {"def": "赤貧的，一無所有的", "distractors": ["富有的", "充足的", "奢華的"], "sent": "The war left many families destitute."},
    "diligence": {"def": "勤奮", "distractors": ["懶惰", "疏忽", "休閒"], "sent": "Success requires hard work and diligence."},
    "dinged": {"def": "被撞擊，被扣分", "distractors": ["修復", "獎勵", "清潔"], "sent": "The car door got dinged in the parking lot."},
    # ... 其餘單字可視需要繼續加入
}

# =========================================================
# 2) GOOGLE SHEETS 連結與邏輯
# =========================================================
st.set_page_config(page_title="單字學習雲端版", page_icon="☁️")
conn = st.connection("gsheets", type=GSheetsConnection)

def get_all_progress():
    """從 Google Sheets 獲取所有分數，若無則初始化"""
    try:
        df = conn.read(ttl="1s") # 強制不使用緩存，讀取最新數據
        return df.set_index("word").to_dict("index")
    except:
        return {}

def save_word_progress(word, score, last_date):
    """更新單個單字進度到 Google Sheets"""
    df = conn.read(ttl="0")
    if word in df["word"].values:
        df.loc[df["word"] == word, ["score", "last_date"]] = [score, last_date]
    else:
        new_row = pd.DataFrame([{"word": word, "score": score, "last_date": last_date}])
        df = pd.concat([df, new_row], ignore_index=True)
    
    conn.update(data=df)

@st.cache_data(show_spinner=False, ttl=3600)
def tts_mp3_bytes_cached(text: str):
    try:
        tts = gTTS(text, lang="en")
        fp = BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except: return None

# =========================================================
# 3) 遊戲邏輯
# =========================================================
def initialize_game():
    progress = get_all_progress()
    # 篩選未達標單字
    available = [w for w in VOCAB_DB.keys() if progress.get(w, {}).get("score", 0) < MASTERY_THRESHOLD]
    
    if not available:
        st.session_state.game_over = True
        return

    selected = random.sample(available, min(len(available), WORDS_PER_SESSION))
    
    st.session_state.update({
        "game_words": selected,
        "current_index": 0,
        "session_score": 0,
        "game_over": False,
        "progress": progress,
        "answered": False,
        "current_word": None
    })

# 初始化 Session
if "game_words" not in st.session_state:
    initialize_game()

st.title("📚 單字間隔重複 (雲端版)")
st.info("數據已與 Google Sheets 同步，進度不會遺失。")

# --- 側邊欄 ---
with st.sidebar:
    st.header("📊 學習統計")
    all_prog = get_all_progress()
    mastered_count = sum(1 for v in all_prog.values() if v.get("score", 0) >= MASTERY_THRESHOLD)
    st.write(f"已精通單字數: {mastered_count} / {len(VOCAB_DB)}")
    if st.button("重新整理數據"):
        st.rerun()

# --- 遊戲結束 ---
if st.session_state.get("game_over", False):
    st.success("🎉 本輪完成！所有進度已安全儲存。")
    if st.button("開始下一輪"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
    st.stop()

# --- 題目顯示 ---
curr_word = st.session_state.game_words[st.session_state.current_index]
data = VOCAB_DB[curr_word]

if st.session_state.get("current_word") != curr_word:
    opts = data["distractors"] + [data["def"]]
    random.shuffle(opts)
    st.session_state.options = opts
    st.session_state.current_word = curr_word
    st.session_state.answered = False

st.markdown(f"<h1 style='text-align:center;'>{curr_word}</h1>", unsafe_allow_html=True)
audio = tts_mp3_bytes_cached(curr_word)
if audio: st.audio(audio, format="audio/mp3")

# --- 回答邏輯 ---
if not st.session_state.answered:
    cols = st.columns(2)
    for i, opt in enumerate(st.session_state.options):
        if cols[i%2].button(opt, use_container_width=True):
            st.session_state.answered = True
            today = str(datetime.date.today())
            
            if opt == data["def"]:
                st.session_state.last_res = "correct"
                st.session_state.session_score += 1
                # 間隔重複：讀取舊分數並更新
                prog = st.session_state.progress.get(curr_word, {"score": 0, "last_date": ""})
                if prog["last_date"] != today:
                    new_score = int(prog["score"]) + 1
                    save_word_progress(curr_word, new_score, today)
                    st.session_state.msg = f"✅ 正確！掌握度上升至 {new_score}"
                else:
                    st.session_state.msg = "☑️ 正確！(今日分數已拿過)"
            else:
                st.session_state.last_res = "wrong"
                st.session_state.msg = "❌ 答錯了！"
            st.rerun()
else:
    if st.session_state.last_res == "correct":
        st.success(st.session_state.msg)
    else:
        st.error(st.session_state.msg)
        st.info(f"正確定義: {data['def']}")
    
    st.write(f"📖 例句: {data['sent']}")
    
    if st.button("下一題 ➡️"):
        st.session_state.current_index += 1
        if st.session_state.current_index >= len(st.session_state.game_words):
            st.session_state.game_over = True
        st.rerun()





    

       

  

         
            


 
