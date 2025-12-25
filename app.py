
import streamlit as st
import random
import json
import os
import datetime
from gtts import gTTS
from io import BytesIO

# --- 1. CONFIGURATION ---
PROGRESS_FILE = "vocab_progress_spaced.json"
MASTERY_THRESHOLD = 6

# --- 2. VOCABULARY DATABASE ---
VOCAB_DB = {
    # === WORDS FROM LATEST SCREENSHOTS (A-D) ===
    "aberrant": {"def": "異常的，脫軌的", "distractors": ["正常的", "標準的", "受歡迎的"], "sent": "His aberrant behavior worried his parents."},
    "abstinence": {"def": "節制，禁慾", "distractors": ["放縱", "暴飲暴食", "參與"], "sent": "The doctor recommended total abstinence from alcohol."},
    "acerbic": {"def": "尖刻的，酸澀的", "distractors": ["甜蜜的", "溫和的", "讚美的"], "sent": "He wrote an acerbic review of the movie."},
    "addled": {"def": "糊塗的，混亂的", "distractors": ["清醒的", "聰明的", "敏銳的"], "sent": "My brain is addled from lack of sleep."},
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
    
    # === SELECTION FROM BACKUP FILE ===
    "irrepressible": {"def": "抑制不住的", "distractors": ["壓抑的", "冷靜的", "悲傷的"], "sent": "He has an irrepressible sense of humor."},
    "depraved": {"def": "墮落的，邪惡的", "distractors": ["高尚的", "純潔的", "誠實的"], "sent": "It was a depraved act of violence."},
    "vicariously": {"def": "間接體驗地", "distractors": ["直接地", "痛苦地", "孤獨地"], "sent": "He lived vicariously through his son's success."},
    "soporific": {"def": "催眠的", "distractors": ["興奮的", "有趣的", "驚悚的"], "sent": "The professor's voice was soporific."},
    "inept": {"def": "無能的，笨拙的", "distractors": ["熟練的", "聰明的", "專家的"], "sent": "He is socially inept and awkward."},
    "obsequious": {"def": "諂媚的", "distractors": ["傲慢的", "誠實的", "勇敢的"], "sent": "The waiter was obsequious to the rich customers."},
    "intransigent": {"def": "不妥協的", "distractors": ["靈活的", "溫和的", "合作的"], "sent": "The union remained intransigent on the wage issue."},
    "scrimped": {"def": "節省，省吃儉用", "distractors": ["浪費，揮霍", "尖叫", "爬行"], "sent": "They scrimped and saved for years to buy a house."},
    "scrupulously": {"def": "小心翼翼地，嚴謹地", "distractors": ["粗心地", "迅速地", "憤怒地"], "sent": "The nurse scrupulously washed her hands."},
    "serenity": {"def": "寧靜，安詳", "distractors": ["混亂", "焦慮", "悲傷"], "sent": "I admired the serenity of the mountain lake."},
    "squander": {"def": "浪費，揮霍", "distractors": ["儲存", "投資", "建造"], "sent": "Don't squander your opportunities."},
    "squeamish": {"def": "神經質的，易受驚的", "distractors": ["勇敢的", "強壯的", "冷靜的"], "sent": "He is squeamish about the sight of blood."},
    "stigmatize": {"def": "侮辱，給...帶來恥辱", "distractors": ["讚揚", "幫助", "忽視"], "sent": "People should not be stigmatized for having a mental illness."},
    "quizzically": {"def": "疑惑地，探詢地", "distractors": ["肯定地", "憤怒地", "高興地"], "sent": "She looked at him quizzically, not understanding his joke."},
    "ravenous": {"def": "極其飢餓的", "distractors": ["飽的", "疲倦的", "口渴的"], "sent": "After the hike, we were absolutely ravenous."},
    "reclamation": {"def": "開墾，回收利用", "distractors": ["破壞", "放棄", "銷售"], "sent": "The reclamation of the wetlands was a success."},
    "repugnant": {"def": "令人厭惡的，反感的", "distractors": ["迷人的", "美味的", "昂貴的"], "sent": "I find his prejudice absolutely repugnant."},
    "retribution": {"def": "報應，懲罰", "distractors": ["獎勵", "原諒", "忽視"], "sent": "He feared retribution for his crimes."},
    "inexorable": {"def": "不可阻擋的，無情的", "distractors": ["可逆的", "溫柔的", "短暫的"], "sent": "The inexorable progress of science continues."},
    "infatuated": {"def": "迷戀的", "distractors": ["討厭的", "害怕的", "冷漠的"], "sent": "He became infatuated with the new girl in class."},
    "innocuous": {"def": "無害的", "distractors": ["危險的", "有毒的", "昂貴的"], "sent": "It seemed like an innocuous question."},
    "jubilant": {"def": "歡騰的，喜氣洋洋的", "distractors": ["悲傷的", "憤怒的", "無聊的"], "sent": "The fans were jubilant after their team won."},
    "litany": {"def": "喋喋不休的抱怨/陳述", "distractors": ["簡短的回答", "快樂的歌曲", "沉默"], "sent": "She recited a litany of grievances against her boss."},
    "pandemonium": {"def": "大混亂，騷動", "distractors": ["平靜", "秩序", "音樂"], "sent": "Pandemonium broke out when the fire alarm rang."},
    "parched": {"def": "乾渴的，乾枯的", "distractors": ["濕潤的", "寒冷的", "飽的"], "sent": "My throat was parched after the long run."},
    "parochial": {"def": "狹隘的，地方性的", "distractors": ["全球的", "開放的", "寬容的"], "sent": "He has a very parochial view of the world."},
    "travesty": {"def": "拙劣的模仿，嘲弄", "distractors": ["完美的複製品", "嚴肅的戲劇", "悲劇"], "sent": "The trial was a travesty of justice."},
    "trepidation": {"def": "驚恐，不安", "distractors": ["自信", "平靜", "快樂"], "sent": "She opened the letter with some trepidation."},
    "unscrupulous": {"def": "肆無忌憚的，無道德的", "distractors": ["誠實的", "善良的", "謹慎的"], "sent": "The unscrupulous salesman tricked the elderly lady."},
    "whimsical": {"def": "異想天開的，古怪的", "distractors": ["嚴肅的", "實際的", "無聊的"], "sent": "The artist has a whimsical style."},
    "zeal": {"def": "熱情，熱忱", "distractors": ["冷漠", "懶惰", "恐懼"], "sent": "He attacked the project with great zeal."},
    "extricating": {"def": "解救，使擺脫", "distractors": ["糾纏", "忽視", "破壞"], "sent": "He had trouble extricating himself from the difficult situation."},
    "fickle": {"def": "善變的", "distractors": ["堅定的", "忠誠的", "緩慢的"], "sent": "Public opinion can be notoriously fickle."},
    "gregarious": {"def": "社交的，群居的", "distractors": ["孤僻的", "害羞的", "安靜的"], "sent": "She is a gregarious person who loves parties."},
    "plight": {"def": "困境，苦難", "distractors": ["幸福", "財富", "假期"], "sent": "We must help the plight of the refugees."},
    "precarious": {"def": "不穩定的，危險的", "distractors": ["安全的", "堅固的", "舒適的"], "sent": "The ladder was placed in a precarious position."},
    "prudent": {"def": "謹慎的，精明的", "distractors": ["魯莽的", "愚蠢的", "昂貴的"], "sent": "It is prudent to save money for emergencies."},
    "quintessential": {"def": "典型的，完美的", "distractors": ["罕見的", "錯誤的", "糟糕的"], "sent": "She is the quintessential New Yorker."},
    "temerity": {"def": "魯莽，冒失", "distractors": ["謹慎", "恐懼", "禮貌"], "sent": "He had the temerity to call me a liar."},
    "tempestuous": {"def": "劇烈的，暴風雨般的", "distractors": ["平靜的", "溫和的", "緩慢的"], "sent": "They had a tempestuous relationship."},
    "grimaced": {"def": "做鬼臉(表示痛苦/厭惡)", "distractors": ["微笑", "大笑", "睡覺"], "sent": "He grimaced in pain when he stubbed his toe."},
    "gumption": {"def": "進取心，魄力", "distractors": ["懶惰", "愚蠢", "恐懼"], "sent": "It took a lot of gumption to quit her job and start a business."},
    "idyllic": {"def": "田園詩般的，恬靜的", "distractors": ["嘈雜的", "醜陋的", "繁忙的"], "sent": "We spent an idyllic vacation in the countryside."},
    "imperative": {"def": "極重要的，必要的", "distractors": ["可選的", "無用的", "次要的"], "sent": "It is imperative that you see a doctor immediately."}
}

# --- 3. HELPER FUNCTIONS ---

def load_progress():
    """Loads progress. Structure: {'word': {'score': int, 'last_date': str}}"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                data = json.load(f)
                if data and isinstance(list(data.values())[0], int):
                    return {} # Ignore old format
                return data
        except Exception:
            return {}
    return {}

def save_progress(progress):
    try:
        with open(PROGRESS_FILE, "w") as f:
            json.dump(progress, f)
    except Exception as e:
        print(f"Warning: Could not save progress ({e})")

def get_audio_bytes(text):
    try:
        tts = gTTS(text, lang='en')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except Exception as e:
        return None

def initialize_game():
    progress = load_progress()
    
    # Filter words: Score must be < MASTERY_THRESHOLD (6)
    available_words = []
    for w in VOCAB_DB.keys():
        word_data = progress.get(w, {'score': 0})
        if word_data['score'] < MASTERY_THRESHOLD:
            available_words.append(w)
    
    if not available_words:
        st.session_state.game_over = True
        st.session_state.game_words = []
        return

    # Select up to 20 words
    if len(available_words) < 20:
        game_words = available_words
        random.shuffle(game_words)
    else:
        game_words = random.sample(available_words, 20)
    
    st.session_state.game_words = game_words
    st.session_state.current_index = 0
    st.session_state.session_score = 0
    st.session_state.game_over = False
    st.session_state.progress = progress
    st.session_state.answered = False
    st.session_state.current_word_tracker = None

# --- 4. STREAMLIT APP LAYOUT ---

st.title("📚 Spaced Repetition Vocab")
st.markdown("Practice definitions. **Rule:** You gain +1 Mastery Point only **once per day** per word.")

# Initialize Session State
if "game_words" not in st.session_state:
    initialize_game()

# --- GAME OVER SCREEN ---
if st.session_state.get("game_over", False) or not st.session_state.get("game_words"):
    st.success("🎉 Session Complete! (Or all words mastered)")
    if "session_score" in st.session_state:
        st.metric(label="Session Score", value=f"{st.session_state.session_score} / {len(st.session_state.game_words)}")
    
    if st.button("Start New Game"):
        for key in ["game_words", "current_index", "session_score", "game_over", "answered"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    st.stop()

# --- GAME LOGIC ---
try:
    current_word = st.session_state.game_words[st.session_state.current_index]
    word_data = VOCAB_DB[current_word]
except IndexError:
    st.session_state.game_over = True
    st.rerun()

# Prepare options
if st.session_state.current_word_tracker != current_word:
    options = word_data["distractors"] + [word_data["def"]]
    random.shuffle(options)
    st.session_state.options = options
    st.session_state.current_word_tracker = current_word
    st.session_state.answered = False
    st.session_state.last_result = None
    st.session_state.result_msg = ""

# Display Word
st.markdown(f"<h1 style='text-align: center; color: #4CAF50;'>{current_word}</h1>", unsafe_allow_html=True)

# Audio
audio_bytes = get_audio_bytes(current_word)
if audio_bytes:
    st.audio(audio_bytes, format='audio/mp3')

st.write("---")

# Answer Buttons
if not st.session_state.answered:
    cols = st.columns(2)
    for i, option in enumerate(st.session_state.options):
        if cols[i % 2].button(option, use_container_width=True):
            st.session_state.answered = True
            
            # CHECK CORRECTNESS
            if option == word_data["def"]:
                st.session_state.last_result = "correct"
                st.session_state.session_score += 1
                
                # SPACED REPETITION LOGIC
                today_str = str(datetime.date.today())
                w_prog = st.session_state.progress.get(current_word, {'score': 0, 'last_date': ''})
                
                if w_prog['last_date'] != today_str:
                    w_prog['score'] += 1
                    w_prog['last_date'] = today_str
                    st.session_state.result_msg = "✅ Correct! (+1 Mastery Point)"
                else:
                    st.session_state.result_msg = "☑️ Correct! (Mastery limited to +1 per day)"
                
                st.session_state.progress[current_word] = w_prog
                save_progress(st.session_state.progress)
                
            else:
                st.session_state.last_result = "wrong"
                st.session_state.result_msg = "❌ Incorrect."
            
            st.rerun()

# Feedback & Next Button
else:
    if st.session_state.last_result == "correct":
        st.success(st.session_state.result_msg)
    else:
        st.error(st.session_state.result_msg)
        st.info(f"**Correct Definition:** {word_data['def']}")
        st.markdown(f"**Example Sentence:** *{word_data['sent']}*")

    curr_score = st.session_state.progress.get(current_word, {'score': 0})['score']
    st.caption(f"Current Mastery Level: {curr_score}/{MASTERY_THRESHOLD}")

    if st.button("Next Word ➡️", type="primary"):
        st.session_state.current_index += 1
        if st.session_state.current_index >= len(st.session_state.game_words):
            st.session_state.game_over = True
        st.rerun()

# Sidebar Stats & Download
with st.sidebar:
    st.write(f"**Round:** {st.session_state.current_index + 1} / {len(st.session_state.game_words)}")
    if "session_score" in st.session_state:
        st.write(f"**Session Score:** {st.session_state.session_score}")
    
    st.write("---")
    
    # Download Progress Button
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            st.download_button("💾 Download Progress Backup", f, file_name=PROGRESS_FILE)
            
    if st.button("⚠️ Reset All Progress"):
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
        st.session_state.progress = {}
        st.warning("Progress reset.")
