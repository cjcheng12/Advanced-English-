import streamlit as st
import random
import json
import os
from gtts import gTTS
from io import BytesIO

# --- 1. DATA PREPARATION (Words from your images) ---
# Format: "Word": {"def": "Correct Chinese", "distractors": ["Wrong1", "Wrong2", "Wrong3"], "sent": "Example Sentence"}
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

PROGRESS_FILE = "vocab_progress.json"

# --- 2. HELPER FUNCTIONS ---

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "
                  
