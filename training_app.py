import streamlit as st
import datetime
import pandas as pd
import os

# ==========================================
# 1. 基礎設定與資料庫功能
# ==========================================
st.set_page_config(page_title="Captain's Powerlifting Prep", page_icon="🏋️‍♀️", layout="wide")

DATA_FILE = "captain_weight_log.csv"

def load_data():
    """讀取體重紀錄 CSV"""
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["Date", "Weight"])
    return pd.read_csv(DATA_FILE)

def save_data(date, weight):
    """儲存體重紀錄到 CSV"""
    df = load_data()
    date_str = date.strftime("%Y-%m-%d")
    
    # 如果當天已紀錄，則更新；否則新增
    if date_str in df["Date"].values:
        df.loc[df["Date"] == date_str, "Weight"] = weight
    else:
        new_row = pd.DataFrame({"Date": [date_str], "Weight": [weight]})
        df = pd.concat([df, new_row], ignore_index=True)
    
    df.to_csv(DATA_FILE, index=False)
    return df

# ==========================================
# 2. 側邊欄：全域參數
# ==========================================
st.sidebar.header("⚙️ 船長控制塔")
comp_date = st.sidebar.date_input("比賽日期", datetime.date(2026, 4, 4))
today = datetime.date.today()
days_remaining = (comp_date - today).days

st.sidebar.markdown("---")
st.sidebar.subheader("💪 當前 1RM 設定 (kg)")
squat_max = st.sidebar.number_input("深蹲 (Squat) 1RM", value=95.0, step=0.5)
bench_max = st.sidebar.number_input("臥推 (Bench) 1RM", value=35.0, step=0.5)
deadlift_max = st.sidebar.number_input("硬舉 (Deadlift) 1RM", value=95.0, step=0.5)

# 計算目前週期
# 假設備賽期為 14 週
start_date = comp_date - datetime.timedelta(weeks=14)
weeks_out = (days_remaining // 7) + 1
current_week_num = 15 - weeks_out

# 決定階段文字
if current_week_num <= 4:
    phase = "Phase 1: 基石期"
    phase_note = "RPE 7-8 | 累積訓練量，動作控制，修復弱點"
elif 5 <= current_week_num <= 8:
    phase = "Phase 2: 強化期"
    phase_note = "RPE 8-9 | 針對黏滯點，重量上升，次數下降"
elif 9 <= current_week_num <= 12:
    phase = "Phase 3: 專項轉化"
    phase_note = "RPE 9 | 模擬比賽口令，適應開把重量"
elif 13 <= current_week_num <= 14:
    phase = "Phase 4: 減量與比賽"
    phase_note = "恢復與超補償 | 準備破 PR！"
else:
    phase = "非賽季 / 休息"
    phase_note = "請調整比賽日期設定"

# ==========================================
# 3. 主介面
# ==========================================
st.title("🏋️‍♀️ 船長備賽中控台 v2.1 (Full)")
st.info(f"📅 **目前進度：第 {current_week_num} 週** (距比賽 {days_remaining} 天)\n\n📌 **{phase}** : {phase_note}")

tab1, tab2 = st.tabs(["📊 體重與飲食監控", "💪 訓練課表執行"])

# ==========================================
# TAB 1: 體重與飲食
# ==========================================
with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚖️ 體重追蹤")
        target_weight = 47.0
        current_input_weight = st.number_input("輸入今天體重 (kg)", min_value=40.0, max_value=60.0, step=0.1, format="%.1f")
        
        if st.button("💾 紀錄體重"):
            save_data(today, current_input_weight)
            st.success(f"已紀錄: {current_input_weight} kg")
        
        # 讀取數據並顯示
        df = load_data()
        if not df.empty:
            latest_weight = df.iloc[-1]["Weight"]
            gap = latest_weight - target_weight
            st.metric("目前體重", f"{latest_weight} kg", f"{gap:+.1f} kg (距目標)", delta_color="inverse")
            
            with st.expander("管理數據"):
                if st.button("⚠️ 清除所有紀錄"):
                    if os.path.exists(DATA_FILE):
                        os.remove(DATA_FILE)
                        st.experimental_rerun()

    with col2:
        st.subheader("📈 趨勢圖")
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")
            chart_data = df.set_index("Date")
            chart_data["Target"] = target_weight
            st.line_chart(chart_data, color=["#FF4B4B", "#00FF00"]) 
        else:
            st.info("尚未有數據，請輸入第一筆體重。")

    st.divider()
    
    # 飲食區塊
    st.subheader("🥗 每日營養目標")
    is_training_day = st.radio("今天是訓練日嗎？", ["是 (Training Day)", "否 (Rest Day)"], horizontal=True)
    
    c1, c2, c3, c4 = st.columns(4)
    if "是" in is_training_day:
        cal_target = 1500
        carb_target = "160-180g"
        note = "🔥 高碳水日：集中在訓練前後攝取。"
    else:
        cal_target = 1350
        carb_target = "100-120g"
        note = "🥬 低碳水日：多吃蔬菜，讓身體修復。"

    c1.metric("🔥 熱量", f"{cal_target}")
    c2.metric("🥩 蛋白質", "110g")
    c3.metric("🍚 碳水", carb_target)
    c4.metric("🥑 脂肪", "45g")
    st.caption(note)
    
    # 蛋白質計數器
    st.write("---")
    st.markdown("**🥩 蛋白質攝取追蹤 (每份約 20g)**")
    if 'protein_count' not in st.session_state:
        st.session_state.protein_count = 0

    col_p1, col_p2 = st.columns([1, 3])
    with col_p1:
        if st.button("➕ 吃一份 (20g)"):
            st.session_state.protein_count += 20
        if st.button("🔄 重置"):
            st.session_state.protein_count = 0
            
    with col_p2:
        p_val = st.session_state.protein_count
        p_progress = min(p_val / 110, 1.0)
        st.progress(p_progress)
        st.write(f"目前: **{p_val}g** / 110g")
        if p_val >= 110:
            st.success("🎉 蛋白質目標達成！")

# ==========================================
# TAB 2: 訓練課表 (完整邏輯)
# ==========================================
with tab2:
    
    def show_workout(exercise, sets, reps, percentage, note, one_rm=0):
        weight_str = ""
        if one_rm > 0 and percentage > 0:
            weight = one_rm * percentage
            weight_str = f" 🔥 **{weight:.1f} kg**"
        
        st.markdown(f"#### {exercise}")
        st.markdown(f"- **{sets} 組 x {reps} 下** {weight_str}")
        st.caption(f"💡 {note}")
        st.checkbox(f"完成", key=exercise+str(today)) # key加上日期避免衝突
        st.write("")

    day_selection = st.radio("選擇今日課表", ["Day 1 (週一:深蹲)", "Day 2 (週三:臥推)", "Day 3 (週五:硬舉)", "休息日"], horizontal=True)
    st.divider()

    if day_selection == "休息日":
        st.success("💤 休息日：做點伸展，確保睡眠充足。")

    # ---------------------------
    # Day 1: 深蹲主項 + 臥推輔助
    # ---------------------------
    elif "Day 1" in day_selection:
        st.header("🦵 Day 1: 深蹲重點日")
        
        if current_week_num <= 4: # Phase 1
            show_workout("低背槓深蹲 (Low Bar)", 5, 6, 0.70, "RPE 7，專注深度", squat_max)
            show_workout("暫停臥推", 4, 8, 0.65, "胸口停1秒，練底部發力", bench_max)
            show_workout("分腿蹲 (Split Squat)", 3, 10, 0, "單腳訓練，改善平衡")
            show_workout("核心/死蟲式", 3, 15, 0, "核心穩定")
            
        elif current_week_num <= 8: # Phase 2
            show_workout("深蹲", 4, 4, 0.80, "RPE 8，強度提升", squat_max)
            show_workout("地板臥推 (Floor Press)", 4, 6, 0, "啞鈴或槓鈴皆可，練鎖定")
            show_workout("羅馬尼亞硬舉 (RDL)", 3, 8, 0.60, "強化後側鏈", deadlift_max)
            
        elif current_week_num <= 12: # Phase 3
            show_workout("深蹲 (模擬賽)", 3, 3, 0.90, "RPE 9，適應重量，第12週測開把", squat_max)
            show_workout("輕臥推", 3, 5, 0.65, "維持手感", bench_max)
            
        else: # Phase 4 (Taper)
            st.warning("🔄 減量週：重量打8折，組數減半")
            show_workout("深蹲 (減量)", 3, 5, 0.50, "活動關節，練發力", squat_max)

    # ---------------------------
    # Day 2: 臥推主項 + 上肢輔助
    # ---------------------------
    elif "Day 2" in day_selection:
        st.header("💪 Day 2: 臥推重點日")
        
        if current_week_num <= 4: # Phase 1
            show_workout("標準臥推 (Comp Bench)", 5, 5, 0.75, "RPE 7.5，起橋固定", bench_max)
            show_workout("窄握臥推", 3, 8, 0.60, "針對三頭肌", bench_max)
            show_workout("坐姿啞鈴肩推", 3, 12, 0, "肩膀穩定")
            show_workout("臉拉 (Face Pull)", 3, 15, 0, "護肩與上背")
            
        elif current_week_num <= 8: # Phase 2
            show_workout("臥推", 5, 3, 0.85, "RPE 8.5，重量提升", bench_max)
            show_workout("三頭肌下壓", 4, 10, 0, "孤立三頭訓練")
            show_workout("槓鈴划船", 4, 8, 0, "背部對抗肌")
            
        elif current_week_num <= 12: # Phase 3
            show_workout("臥推 (模擬賽)", 4, 2, 0.90, "RPE 9，嚴格執行口令 Start/Press/Rack", bench_max)
            show_workout("輕輔助項", 2, 10, 0, "輕鬆做，不要累積疲勞")
            
        else: # Phase 4 (Taper)
            st.warning("🔄 減量週：重量打8折，組數減半")
            show_workout("臥推 (減量)", 3, 5, 0.50, "練習口令", bench_max)

    # ---------------------------
    # Day 3: 硬舉主項 + 深蹲輔助
    # ---------------------------
    elif "Day 3" in day_selection:
        st.header("🚀 Day 3: 硬舉重點日")
        
        if current_week_num <= 4: # Phase 1
            show_workout("硬舉 (Deadlift)", 4, 5, 0.70, "RPE 7，拉緊槓鈴 Slack out", deadlift_max)
            show_workout("暫停深蹲", 3, 5, 0.55, "底部停2秒，約主項的70%", squat_max)
            show_workout("滑輪下拉", 3, 12, 0, "背闊肌")
            
        elif current_week_num <= 8: # Phase 2
            show_workout("硬舉", 3, 3, 0.85, "RPE 8.5，強度高", deadlift_max)
            show_workout("高背槓深蹲", 3, 6, 0.65, "強化股四頭肌", squat_max)
            show_workout("負重核心", 3, 10, 0, "核心穩定")
            
        elif current_week_num <= 12: # Phase 3
            show_workout("硬舉 (模擬賽)", 2, 2, 0.90, "RPE 9，注意恢復，第12週測開把", deadlift_max)
            show_workout("速度蹲 (Speed Squat)", 3, 3, 0.60, "專注爆發力", squat_max)
            
        else: # Phase 4 (Taper)
            st.warning("🔄 減量週：重量打8折，組數減半")
            show_workout("硬舉 (減量)", 3, 5, 0.50, "輕重量活動", deadlift_max)

st.write("---")
st.caption("Developed by Monica for Captain. Powered by FP-CRF v6.1")
