import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import sys  # 윈도우 프로세스 강제 종료용

# 1. 엑셀 데이터 로드
file_name = "Antoine_Equation_Constants_Table.xlsx"

try:
    df = pd.read_excel(file_name, skiprows=3)
except FileNotFoundError:
    print(f"[{file_name}] 파일을 찾을 수 없습니다. 엑셀 파일을 확인해주세요.")
    exit()

df.columns = df.columns.str.strip()
df = df.dropna(subset=["Substance Name", "A", "B", "C"])

df["Display Name"] = df["Substance Name"] + " (" + df["Formula"].astype(str) + ")"
substance_list = df["Display Name"].tolist()


# 2. 앙투안 식 계산 함수
def calculate_vapor_pressure(T_K, A, B, C):
    ln_p = A - (B / (C + T_K))
    return np.exp(ln_p)


# 3. 메인 GUI 창 설정
root = tk.Tk()
root.title("Antoine Vapor Pressure Curve Tracker")
root.geometry("1100x800")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int((screen_width - 1100) / 2)
center_y = int((screen_height - 800) / 2)
root.geometry(f"1100x800+{center_x}+{center_y}")


# --- 레이아웃 설정 ---
top_frame = ttk.LabelFrame(root, text=" 물질 선택 및 상수 정보 ", padding=15)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=5)

coord_frame = ttk.Frame(root, padding=10)
coord_frame.pack(side=tk.TOP, fill=tk.X, padx=15)

bottom_frame = ttk.Frame(root, padding=10)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=15, pady=5)


# --- 상단 컨트롤 요소 ---
lbl_select = ttk.Label(top_frame, text="물질 선택:", font=("Malgun Gothic", 10, "bold"))
lbl_select.grid(row=0, column=0, padx=(0, 10), sticky="w")

combo_substance = ttk.Combobox(top_frame, values=substance_list, width=40, state="readonly")
combo_substance.grid(row=0, column=1, padx=(0, 20), sticky="w")
if substance_list:
    combo_substance.current(0)

info_frame = ttk.Frame(top_frame)
info_frame.grid(row=0, column=2, sticky="w")

lbl_info_text = tk.StringVar(value="정보를 불러오는 중...")
lbl_info = ttk.Label(info_frame, textvariable=lbl_info_text, font=("Consolas", 10), justify=tk.LEFT)
lbl_info.pack(anchor="w")


# --- 중단 선상 좌표 표시 라벨 ---
lbl_coord_text = tk.StringVar(value="[데이터 추적] 그래프 위에 마우스를 올려보세요.")
lbl_coord = ttk.Label(coord_frame, textvariable=lbl_coord_text, font=("Malgun Gothic", 11, "bold"), foreground="#0078d7")
lbl_coord.pack(anchor="center")


# --- 하단 그래프 설정 ---
fig, ax = plt.subplots(figsize=(9, 5))
plot_canvas = FigureCanvasTkAgg(fig, master=bottom_frame)
plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

current_xs = np.array([])
current_ys = np.array([])
trace_marker, = ax.plot([], [], 'ro', markersize=8, visible=False)


# --- 4. 그래프 선상 좌표 추적 콜백 함수 ---
def on_mouse_move(event):
    global current_xs, current_ys
    
    if event.inaxes != ax or current_xs.size == 0:
        trace_marker.set_visible(False)
        lbl_coord_text.set("[데이터 추적] 그래프 위에 마우스를 올려보세요.")
        plot_canvas.draw_idle()
        return

    mouse_x = event.xdata
    idx = (np.abs(current_xs - mouse_x)).argmin()
    
    actual_x = current_xs[idx]
    actual_y = current_ys[idx]
    
    lbl_coord_text.set(f"📊 곡선 데이터 ➡️  온도: {actual_x:.2f} °C  |  실제 증기압: {actual_y:.2f} mm Hg")
    
    trace_marker.set_data([actual_x], [actual_y])
    trace_marker.set_visible(True)
    plot_canvas.draw_idle()


# --- 5. 그래프 및 데이터 갱신 함수 ---
def update_plot(event=None):
    global current_xs, current_ys
    
    selected_name = combo_substance.get()
    if not selected_name:
        return
        
    selected_row = df[df["Display Name"] == selected_name].iloc[0]
    
    substance_name = selected_row["Substance Name"]
    formula = selected_row["Formula"]
    A = float(selected_row["A"])
    B = float(selected_row["B"])
    C = float(selected_row["C"])
    temp_range_str = str(selected_row["Temperature Range (K)"])
    
    try:
        t_min, t_max = map(float, temp_range_str.split("-"))
    except ValueError:
        t_min, t_max = 273.15, 373.15
        
    info_string = (
        f"Valid Range: {temp_range_str} K  |  "
        f"Constants: A = {A:.4f},  B = {B:.2f},  C = {C:.2f}"
    )
    lbl_info_text.set(info_string)
    
    temperatures_K = np.linspace(t_min, t_max, 500)
    vapor_pressures_mmHg = calculate_vapor_pressure(temperatures_K, A, B, C)
    temperatures_C = temperatures_K - 273.15
    
    current_xs = temperatures_C
    current_ys = vapor_pressures_mmHg
    
    ax.clear()
    ax.plot(temperatures_C, vapor_pressures_mmHg, 
            label=f"{substance_name} ({formula})", 
            color="crimson", 
            linewidth=2.5)
    
    global trace_marker
    trace_marker, = ax.plot([], [], 'ro', markersize=8, zorder=5) 
    trace_marker.set_visible(False)
    
    ax.set_title(f"Vapor Pressure Curve: {substance_name} ({formula})", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Temperature (°C)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Vapor Pressure (mm Hg)", fontsize=10, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=10, loc="upper left")
    
    plot_canvas.draw()


# --- 6. 윈도우 종료 핸들러 함수 (추가된 핵심 기능) ---
def on_closing():
    """창을 닫을 때 백그라운드 프로세스까지 완전히 청소하는 함수"""
    # 1. Matplotlib에 열려있는 피겨(Figure) 메모리 해제
    plt.close(fig)
    plt.close('all')
    
    # 2. Tkinter 위젯 파괴 및 메인 루프 탈출
    root.quit()
    root.destroy()
    
    # 3. 간혹 남아있을 수 있는 가비지 컬렉션 및 프로세스 강제 종료 인터럽트
    sys.exit(0)


# --- 7. 이벤트 및 프로토콜 바인딩 ---
combo_substance.bind("<<ComboboxSelected>>", update_plot)
fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)

# 윈도우 창의 'X' 버튼 클릭 이벤트 가로채기
root.protocol("WM_DELETE_WINDOW", on_closing)

# 최초 실행
update_plot()

root.mainloop()