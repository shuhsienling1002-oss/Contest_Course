import streamlit as st
import datetime
import pandas as pd

# --- 頁面設定 ---
st.set_page_config(page_title="Captain's Powerlifting Prep", page_icon="🏋️‍♀️")

# --- 側邊欄：基本設定 ---
st.sidebar.header("⚙️ 船長基本設定")

# 設定比賽日期
comp_date = st.sidebar.date_input("比賽日期", datetime.date(2026, 4, 4))
today = datetime.date.today()

# 設定目前 PR (用於計算訓練重量)
st.sidebar.subheader("當前 1RM 設定 (kg)")
squat_max = st.sidebar.number_input("深蹲 (Squat) 1RM", value=95.0, step=0.5)
bench_max = st.sidebar.number_input("臥推 (Bench) 1RM", value=35.0, step=0.5)
deadlift_max = st.sidebar.number_input("硬舉 (Deadlift) 1RM", value=95.0, step=0.5)

# --- 邏輯運算：計算週期 ---
# 假設備賽期為 14 週
start_date = comp_date - datetime.timedelta(weeks=14)
days_remaining = (comp_date - today).days
weeks_out = (days_remaining // 7) + 1
current_week_num = 15 - weeks_out

# 簡單的階段判斷
if current_week_num <= 4:
    phase = "Phase 1: 基石期 (肌肥大/適應)"
    phase_note = "RPE 7-8 | 專注動作控制，累積訓練量"
elif 5 <= current_week_num <= 8:
    phase = "Phase 2: 強化期 (拉高強度)"
    phase_note = "RPE 8-9 | 針對黏滯點，重量上升"
elif 9 <= current_week_num <= 12:
    phase = "Phase 3: 專項轉化 (適應大重量)"
    phase_note = "RPE 9 | 模擬比賽口令，適應開把重量"
elif 13 <= current_week_num <= 14:
    phase = "Phase 4: 減量與比賽"
    phase_note = "恢復與超補償 | 準備破 PR"
else:
    phase = "非賽季 / 休息"
    phase_note = "請調整比賽日期"

# --- 主畫面 ---
st.title("🏋️‍♀️ 船長備賽控制台")
st.markdown(f"**目標賽事：** 桃園市市長盃 ({comp_date})")
st.markdown(f"**距離比賽：** 還有 {days_remaining} 天")
st.info(f"📅 **目前進度：第 {current_week_num} 週** / 共 14 週\n\n📌 **{phase}**\n\n📝 *{phase_note}*")

# --- 選擇今天的訓練 ---
st.write("---")
day_selection = st.radio("今天是哪一天？", ["Day 1 (週一: 深蹲主場)", "Day 2 (週三: 臥推主場)", "Day 3 (週五: 硬舉主場)", "休息日"])

# --- 課表邏輯 (根據階段與天數顯示內容) ---

def show_workout(exercise, sets, reps, percentage, note, one_rm=0):
    weight_str = ""
    if one_rm > 0 and percentage > 0:
        weight = one_rm * percentage
        weight_str = f" 🔥 **推薦重量: {weight:.1f} kg**"
    
    st.markdown(f"### {exercise}")
    st.markdown(f"- **{sets} 組 x {reps} 下** {weight_str}")
    st.caption(f"💡 {note}")
    st.checkbox(f"完成 {exercise}", key=exercise)
    st.write("")

if day_selection == "休息日":
    st.success("💤 休息是為了走更長的路。多吃蛋白質，睡飽 8 小時！")

elif "Day 1" in day_selection:
    st.header("🦵 Day 1: 深蹲重點日")
    
    if current_week_num <= 4:
        show_workout("低背槓深蹲 (Low Bar)", 5, 6, 0.70, "RPE 7，專注深度", squat_max)
        show_workout("暫停臥推", 4, 8, 0.65, "胸口停1秒", bench_max)
        show_workout("分腿蹲", 3, 10, 0, "單腳訓練，改善不平衡")
        show_workout("死蟲式/核心", 3, 15, 0, "核心穩定")
    elif current_week_num <= 8:
        show_workout("深蹲", 4, 4, 0.80, "RPE 8，強度提升", squat_max)
        show_workout("地板臥推/啞鈴臥推", 4, 6, 0, "加強三頭與鎖定")
        show_workout("羅馬尼亞硬舉 (RDL)", 3, 8, 0.60, "強化後側鏈", deadlift_max)
    elif current_week_num <= 12:
        show_workout("深蹲 (模擬賽)", 3, 3, 0.90, "RPE 9，適應重量", squat_max)
        show_workout("輕臥推", 3, 5, 0.65, "維持手感", bench_max)
    else:
        st.warning("減量週：重量打8折，組數減半")
        show_workout("深蹲 (減量)", 3, 5, 0.50, "活動關節，練發力", squat_max)

elif "Day 2" in day_selection:
    st.header("💪 Day 2: 臥推重點日")
    
    if current_week_num <= 4:
        show_workout("標準臥推 (Comp Bench)", 5, 5, 0.75, "RPE 7.5，練習起橋", bench_max)
        show_workout("窄握臥推", 3, 8, 0.60, "針對三頭肌", bench_max)
        show_workout("坐姿啞鈴肩推", 3, 12, 0, "肩膀穩定")
        show_workout("臉拉 (Face Pull)", 3, 15, 0, "護肩與上背")
    elif current_week_num <= 8:
        show_workout("臥推", 5, 3, 0.85, "RPE 8.5，重量提升", bench_max)
        show_workout("三頭肌下壓", 4, 10, 0, "孤立訓練")
        show_workout("槓鈴划船", 4, 8, 0, "背部對抗肌")
    elif current_week_num <= 12:
        show_workout("臥推 (模擬賽)", 4, 2, 0.90, "RPE 9，執行比賽口令 Start/Press/Rack", bench_max)
        show_workout("輕輔助項", 2, 10, 0, "輕鬆做")
    else:
        st.warning("減量週：重量打8折，組數減半")
        show_workout("臥推 (減量)", 3, 5, 0.50, "練習口令", bench_max)

elif "Day 3" in day_selection:
    st.header("🚀 Day 3: 硬舉重點日")
    
    if current_week_num <= 4:
        show_workout("硬舉 (Deadlift)", 4, 5, 0.70, "RPE 7，拉緊槓鈴 Slack out", deadlift_max)
        show_workout("暫停深蹲", 3, 5, 0.55, "底部停2秒，約主項的70%", squat_max)
        show_workout("滑輪下拉", 3, 12, 0, "背闊肌")
    elif current_week_num <= 8:
        show_workout("硬舉", 3, 3, 0.85, "RPE 8.5，強度高", deadlift_max)
        show_workout("高背槓深蹲", 3, 6, 0.65, "強化股四頭肌", squat_max)
        show_workout("負重核心", 3, 10, 0, "核心")
    elif current_week_num <= 12:
        show_workout("硬舉 (模擬賽)", 2, 2, 0.90, "RPE 9，注意恢復", deadlift_max)
        show_workout("速度蹲", 3, 3, 0.60, "爆發力", squat_max)
    else:
        st.warning("減量週：重量打8折，組數減半")
        show_workout("硬舉 (減量)", 3, 5, 0.50, "輕重量活動", deadlift_max)

# --- 頁尾 ---
st.write("---")
st.caption("Developed by Monica for Captain. Powered by FP-CRF v6.1")