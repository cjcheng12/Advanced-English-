
import streamlit as st
import random
import json
import os
from gtts import gTTS
from io import BytesIO

# --- 1. CONFIGURATION ---
PROGRESS_FILE = "vocab_progress.json"

# --- 2. VOCABULARY DATABASE ---
# Extracted from your provided images
VOCAB_DB = {
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
    "carcinogen": {"def": "致癌物質", "distractors": ["維生素", "藥物", "食物"], "sent": "Tobacco smoke contains many known carcinogens."},
    "caveat": {"def": "警告，限制條款", "distractors": ["獎金", "合同", "自由"], "sent": "There is one caveat to this deal: no refunds."},
    "commensurate": {"def": "相稱的，相當的", "distractors": ["不平等的", "巨大的", "微小的"], "sent": "Salary will be commensurate with experience."},
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
    """Loads the user's progress from a JSON file."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {} # Return empty if file is corrupt
    return {}

def save_progress(progress):
    """Saves the user's progress to a JSON file."""
    try:
        with open(PROGRESS_FILE, "w") as f:
            json.dump(progress, f)
    except Exception as e:
        print(f"Warning: Could not save progress ({e})")

def get_audio_bytes(text):
    """Generates audio bytes for the English word."""
    try:
        tts = gTTS(text, lang='en')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except Exception as e:
        print(f"Audio generation error: {e}")
        return None

def initialize_game():
    progress = load_progress()
    
    # Filter words: Must have score < 6
    available_words = [w for w in VOCAB_DB.keys() if progress.get(w, 0) < 6]
    
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
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.progress = progress
    st.session_state.answered = False
    st.session_state.current_word_tracker = None

# --- 4. STREAMLIT APP LAYOUT ---

st.title("📚 Advanced Vocab Mastery")
st.markdown("Practice definitions. **Mastery Rule:** Correctly answer a word 6 times to retire it.")

# Initialize Session State
if "game_words" not in st.session_state:
    initialize_game()

# --- GAME OVER SCREEN ---
if st.session_state.get("game_over", False) or not st.session_state.get("game_words"):
    st.success("🎉 Session Complete! (Or all words mastered)")
    if "score" in st.session_state and "game_words" in st.session_state:
        st.metric(label="Final Score", value=f"{st.session_state.score} / {len(st.session_state.game_words)}")
    
    if st.button("Start New Game"):
        # Reset relevant session state
        for key in ["game_words", "current_index", "score", "game_over", "answered"]:
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

# Prepare options (Correct + 3 Distractors)
# We use a tracker to ensure we don't reshuffle options when the user clicks a button (which reruns the script)
if st.session_state.current_word_tracker != current_word:
    options = word_data["distractors"] + [word_data["def"]]
    random.shuffle(options)
    st.session_state.options = options
    st.session_state.current_word_tracker = current_word
    st.session_state.answered = False
    st.session_state.last_result = None

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
            
            # Check correctness
            if option == word_data["def"]:
                st.session_state.last_result = "correct"
                st.session_state.score += 1
                
                # Update Mastery Score (Accumulative)
                current_mastery = st.session_state.progress.get(current_word, 0) + 1
                st.session_state.progress[current_word] = current_mastery
                save_progress(st.session_state.progress)
                
            else:
                st.session_state.last_result = "wrong"
            
            st.rerun()

# Feedback & Next Button (Shown after answering)
else:
    if st.session_state.last_result == "correct":
        st.success("✅ Correct! (+1 Mastery Point)")
    else:
        st.error(f"❌ Incorrect.")
        st.info(f"**Correct Definition:** {word_data['def']}")
        st.markdown(f"**Example Sentence:** *{word_data['sent']}*")

    # Progress Info
    mastery = st.session_state.progress.get(current_word, 0)
    st.caption(f"Current Mastery Level for '{current_word}': {mastery}/6")

    if st.button("Next Word ➡️", type="primary"):
        # Move to next word
        st.session_state.current_index += 1
        
        # Check if game needs to end
        if st.session_state.current_index >= len(st.session_state.game_words):
            st.session_state.game_over = True
        
        st.rerun()

# Sidebar Stats
with st.sidebar:
    if "current_index" in st.session_state:
        st.write(f"**Round:** {st.session_state.current_index + 1} / {len(st.session_state.game_words)}")
    if "score" in st.session_state:
        st.write(f"**Session Score:** {st.session_state.score}")
    
    st.write("---")
    if st.button("⚠️ Reset All Progress"):
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
        st.session_state.progress = {}
        st.warning("Progress reset. Please restart game.")
    
