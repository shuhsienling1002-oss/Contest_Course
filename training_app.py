import streamlit as st
import datetime
import pandas as pd
import os

# ==========================================
# 1. 基礎設定與資料庫功能
# ==========================================
st.set_page_config(page_title="Captain's Prep v3.0", page_icon="🏋️‍♀️", layout="wide")

WEIGHT_LOG_FILE = "captain_weight_log.csv"
TRAINING_LOG_FILE = "captain_training_log.csv"

def load_data(file_path, columns):
    """讀取 CSV 資料"""
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=columns)
    return pd.read_csv(file_path)

def save_weight_data(date, weight):
    """儲存體重紀錄"""
    df = load_data(WEIGHT_LOG_FILE, ["Date", "Weight"])
    date_str = date.strftime("%Y-%m-%d")
    
    if date_str in df["Date"].values:
        df.loc[df["Date"] == date_str, "Weight"] = weight
    else:
        new_row = pd.DataFrame({"Date": [date_str], "Weight": [weight]})
        df = pd.concat([df, new_row], ignore_index=True)
    
    df.to_csv(WEIGHT_LOG_FILE, index=False)
    return df

def save_training_log(date, exercise, weight, sets, reps, rpe, note):
    """儲存訓練紀錄"""
    df = load_data(TRAINING_LOG_FILE, ["Date", "Exercise", "Weight", "Sets", "Reps", "RPE", "Note"])
    date_str = date.strftime("%Y-%m-%d")
    
    new_row = pd.DataFrame({
        "Date": [date_str],
        "Exercise": [exercise],
        "Weight": [weight],
        "Sets": [sets],
        "Reps": [reps],
        "RPE": [rpe],
        "Note": [note]
    })
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(TRAINING_LOG_FILE, index=False)
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
squat_max = st.sidebar.number_input("深蹲 (High Bar) 1RM", value=95.0, step=0.5)
bench_max = st.sidebar.number_input("臥推 (Bench) 1RM", value=35.0, step=0.5)
deadlift_max = st.sidebar.number_input("硬舉 (Deadlift) 1RM", value=95.0, step=0.5)

# 計算目前週期
start_date = comp_date - datetime.timedelta(weeks=14)
weeks_out = (days_remaining // 7) + 1
current_week_num = 15 - weeks_out

if current_week_num <= 4:
    phase = "Phase 1: 基石期"
    phase_note = "RPE 7-8 | 累積訓練量，動作控制"
elif 5 <= current_week_num <= 8:
    phase = "Phase 2: 強化期"
    phase_note = "RPE 8-9 | 針對黏滯點，重量上升"
elif 9 <= current_week_num <= 12:
    phase = "Phase 3: 專項轉化"
    phase_note = "RPE 9 | 模擬比賽口令，適應開把"
elif 13 <= current_week_num <= 14:
    phase = "Phase 4: 減量與比賽"
    phase_note = "恢復與超補償 | 準備破 PR！"
else:
    phase = "非賽季 / 休息"
    phase_note = "請調整比賽日期"

# ==========================================
# 3. 主介面
# ==========================================
st.title("🏋️‍♀️ 船長備賽系統 v3.0")
st.info(f"📅 **目前進度：第 {current_week_num} 週** (距比賽 {days_remaining} 天)\n\n📌 **{phase}** : {phase_note}")

tab1, tab2, tab3 = st.tabs(["📊 體重與飲食", "💪 訓練課表 & 紀錄", "📜 歷史訓練日誌"])

# ==========================================
# TAB 1: 體重與飲食 (含外食建議)
# ==========================================
with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚖️ 體重管理")
        target_weight = 47.0
        current_input_weight = st.number_input("今日體重 (kg)", min_value=40.0, max_value=60.0, step=0.1, format="%.1f")
        
        if st.button("💾 紀錄體重"):
            save_weight_data(today, current_input_weight)
            st.success(f"已紀錄: {current_input_weight} kg")
        
        df_weight = load_data(WEIGHT_LOG_FILE, ["Date", "Weight"])
        if not df_weight.empty:
            latest = df_weight.iloc[-1]["Weight"]
            st.metric("目前", f"{latest} kg", f"{latest - target_weight:+.1f} kg (距目標)", delta_color="inverse")

    with col2:
        st.subheader("📈 體重趨勢")
        if not df_weight.empty:
            df_weight["Date"] = pd.to_datetime(df_weight["Date"])
            df_weight = df_weight.sort_values("Date")
            chart_data = df_weight.set_index("Date")
            chart_data["Target"] = target_weight
            st.line_chart(chart_data, color=["#FF4B4B", "#00FF00"]) 
        else:
            st.info("尚無數據")

    st.divider()
    
    # --- 飲食建議與外食區 ---
    st.subheader("🥗 飲食計畫")
    is_training_day = st.radio("今天是訓練日嗎？", ["是 (Training Day)", "否 (Rest Day)"], horizontal=True)
    
    if "是" in is_training_day:
        cal_target, carb_target = 1500, "160-180g"
        note = "🔥 高碳水日：訓練前後多吃澱粉，支撐高背槓深蹲。"
    else:
        cal_target, carb_target = 1350, "100-120g"
        note = "🥬 低碳水日：多吃蔬菜與優質蛋白。"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔥 熱量", f"{cal_target}")
    c2.metric("🥩 蛋白質", "110g")
    c3.metric("🍚 碳水", carb_target)
    c4.metric("🥑 脂肪", "45g")
    st.caption(note)

    # 外食建議模組
    with st.expander("🍱 外食族生存指南 (點擊展開)", expanded=True):
        st.markdown("""
        **核心原則：** 蛋白質優先，澱粉選原型，少碰勾芡與油炸。
        
        | 餐廳類型 | ✅ 推薦組合 (高蛋白/適量碳水) | ❌ 避免地雷 |
        | :--- | :--- | :--- |
        | **便利商店** | 紐奧良雞胸肉 + 溫泉蛋 + 地瓜/御飯糰 + 無糖豆漿 | 炸雞球、含糖優酪乳、真飽涼麵(全是麵) |
        | **自助餐** | 滷雞腿(去皮) / 蒸魚 + 3樣深色蔬菜 + 半碗五穀飯 | 糖醋排骨、炸排骨、淋滷汁的飯、勾芡羹湯 |
        | **火鍋店** | 板腱牛/梅花豬 + 大量蔬菜 + 雞蛋 + 少量冬粉/飯 | 麻辣湯底、加工火鍋料(丸子/餃類)、沙茶醬 |
        | **速食店** | 摩斯海洋珍珠堡(去美乃滋) / Subway 嫩切雞肉(不加醬) | 炸薯條、可樂、炸雞皮 |
        | **麵攤** | 嘴邊肉/肝連 + 燙青菜(不加肉燥) + 陽春麵(湯喝少點) | 麻醬麵(熱量炸彈)、貢丸湯、大腸 |
        """)

# ==========================================
# TAB 2: 訓練課表 & 紀錄 (含日誌功能)
# ==========================================
with tab2:
    
    def render_workout_card(exercise, sets, reps, percentage, note, one_rm=0):
        """顯示訓練卡片並包含輸入功能"""
        # 計算建議重量
        rec_weight = 0
        weight_str = ""
        if one_rm > 0 and percentage > 0:
            rec_weight = one_rm * percentage
            weight_str = f" (🔥 建議: {rec_weight:.1f} kg)"
        
        with st.container():
            st.markdown(f"#### {exercise}")
            st.markdown(f"**目標：** {sets} 組 x {reps} 下 {weight_str}")
            st.caption(f"💡 {note}")
            
            # 訓練紀錄輸入區
            with st.expander(f"📝 紀錄 {exercise} 數據", expanded=False):
                c1, c2, c3 = st.columns([1, 1, 2])
                act_weight = c1.number_input("實際重量", value=float(int(rec_weight)) if rec_weight > 0 else 0.0, step=0.5, key=f"w_{exercise}")
                act_reps = c2.number_input("完成次數", value=int(reps) if isinstance(reps, int) else 0, step=1, key=f"r_{exercise}")
                act_rpe = c3.slider("RPE (自覺費力 1-10)", 5, 10, 8, key=f"rpe_{exercise}")
                act_note = st.text_input("備註 (ex: 腰帶太緊, 狀況好)", key=f"n_{exercise}")
                
                if st.button(f"✅ 儲存 {exercise}", key=f"btn_{exercise}"):
                    save_training_log(today, exercise, act_weight, sets, act_reps, act_rpe, act_note)
                    st.success("已儲存！")
            st.divider()

    day_selection = st.radio("選擇今日課表", ["Day 1 (週一:高背槓深蹲)", "Day 2 (週三:臥推)", "Day 3 (週五:硬舉)", "休息日"], horizontal=True)
    st.divider()

    if day_selection == "休息日":
        st.success("💤 休息日：請參考飲食分頁的低碳水建議。")

    # ---------------------------
    # Day 1: 高背槓深蹲主項
    # ---------------------------
    elif "Day 1" in day_selection:
        st.header("🦵 Day 1: 深蹲重點日")
        
        if current_week_num <= 4: # Phase 1
            render_workout_card("高背槓深蹲 (High Bar)", 5, 6, 0.70, "比賽動作，專注深度與軀幹直立", squat_max)
            render_workout_card("暫停臥推", 4, 8, 0.65, "胸口停1秒", bench_max)
            render_workout_card("分腿蹲", 3, 10, 0, "單腳訓練，改善平衡")
            
        elif current_week_num <= 8: # Phase 2
            render_workout_card("高背槓深蹲", 4, 4, 0.80, "RPE 8，強度提升", squat_max)
            render_workout_card("地板臥推", 4, 6, 0, "練鎖定")
            render_workout_card("RDL", 3, 8, 0.60, "後側鏈", deadlift_max)
            
        elif current_week_num <= 12: # Phase 3
            render_workout_card("高背槓深蹲 (模擬賽)", 3, 3, 0.90, "RPE 9，適應大重量", squat_max)
            render_workout_card("輕臥推", 3, 5, 0.65, "維持手感", bench_max)
        
        else: # Taper
            st.warning("🔄 減量週")
            render_workout_card("高背槓深蹲 (減量)", 3, 5, 0.50, "輕重量活動", squat_max)

    # ---------------------------
    # Day 2: 臥推主項
    # ---------------------------
    elif "Day 2" in day_selection:
        st.header("💪 Day 2: 臥推重點日")
        
        if current_week_num <= 4:
            render_workout_card("標準臥推", 5, 5, 0.75, "RPE 7.5，起橋固定", bench_max)
            render_workout_card("窄握臥推", 3, 8, 0.60, "三頭肌", bench_max)
            render_workout_card("啞鈴肩推", 3, 12, 0, "肩膀穩定")
            
        elif current_week_num <= 8:
            render_workout_card("臥推", 5, 3, 0.85, "RPE 8.5", bench_max)
            render_workout_card("三頭肌下壓", 4, 10, 0, "孤立三頭")
            
        elif current_week_num <= 12:
            render_workout_card("臥推 (模擬賽)", 4, 2, 0.90, "口令 Start/Press/Rack", bench_max)
        
        else:
            st.warning("🔄 減量週")
            render_workout_card("臥推 (減量)", 3, 5, 0.50, "練習口令", bench_max)

    # ---------------------------
    # Day 3: 硬舉主項
    # ---------------------------
    elif "Day 3" in day_selection:
        st.header("🚀 Day 3: 硬舉重點日")
        
        if current_week_num <= 4:
            render_workout_card("硬舉", 4, 5, 0.70, "拉緊槓鈴 Slack out", deadlift_max)
            render_workout_card("暫停深蹲", 3, 5, 0.55, "底部停2秒", squat_max)
            
        elif current_week_num <= 8:
            render_workout_card("硬舉", 3, 3, 0.85, "RPE 8.5", deadlift_max)
            render_workout_card("前蹲舉/高背槓", 3, 6, 0.65, "輔助深蹲", squat_max)
            
        elif current_week_num <= 12:
            render_workout_card("硬舉 (模擬賽)", 2, 2, 0.90, "注意恢復", deadlift_max)
        
        else:
            st.warning("🔄 減量週")
            render_workout_card("硬舉 (減量)", 3, 5, 0.50, "輕重量活動", deadlift_max)

# ==========================================
# TAB 3: 歷史紀錄 (新增分頁)
# ==========================================
with tab3:
    st.subheader("📜 歷史訓練日誌")
    df_log = load_data(TRAINING_LOG_FILE, ["Date", "Exercise", "Weight", "Sets", "Reps", "RPE", "Note"])
    
    if not df_log.empty:
        # 讓使用者可以篩選動作
        filter_ex = st.selectbox("篩選動作", ["全部"] + list(df_log["Exercise"].unique()))
        
        if filter_ex != "全部":
            show_df = df_log[df_log["Exercise"] == filter_ex]
        else:
            show_df = df_log
            
        st.dataframe(show_df.sort_values("Date", ascending=False), use_container_width=True)
        
        # 簡單的進度圖 (如果選擇了特定動作)
        if filter_ex != "全部" and len(show_df) > 1:
            st.line_chart(show_df.set_index("Date")["Weight"])
            st.caption(f"{filter_ex} 重量趨勢")
            
        # 清除資料按鈕
        with st.expander("危險區域：管理資料"):
            if st.button("🗑️ 清空所有訓練紀錄"):
                if os.path.exists(TRAINING_LOG_FILE):
                    os.remove(TRAINING_LOG_FILE)
                    st.experimental_rerun()
    else:
        st.info("目前還沒有訓練紀錄，快去 Tab 2 開始今天的訓練吧！")

st.write("---")
st.caption("Developed by Monica for Captain. Powered by FP-CRF v6.1")
