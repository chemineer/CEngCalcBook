import tkinter as tk
from tkinter import ttk, messagebox
from pint import UnitRegistry

# 1. Pint 단위 레지스트리 초기화
ureg = UnitRegistry()

# 2. 카테고리별 지원 단위 정의 (압력 단위 추가 완료)
UNIT_CATEGORIES = {
    "길이 (Length)": ["meter", "centimeter", "millimeter", "kilometer", "inch", "foot", "yard", "mile"],
    "무게 (Mass)": ["gram", "kilogram", "milligram", "pound", "ounce"],
    "면적 (Area)": ["meter ** 2", "centimeter ** 2", "kilometer ** 2", "foot ** 2", "acre", "hectare"],
    "부피 (Volume)": ["liter", "milliliter", "gallon", "quart", "cup"],
    "온도 (Temperature)": ["celsius", "fahrenheit", "kelvin"],
    "속도 (Speed)": ["meter_per_second", "kilometer_per_hour", "mile_per_hour", "knot"],
    "압력 (Pressure)": ["pascal", "atmosphere", "bar", "torr", "psi"]
}

class UnitConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pint 다단계 단위 환산기")
        self.root.geometry("750x450")  # 과정을 길게 표시하기 위해 가로 창 크기를 확장했습니다.
        self.root.resizable(False, False)
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. 카테고리 선택
        ttk.Label(main_frame, text="종류 선택:", font=("맑은 고딕", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.category_combo = ttk.Combobox(main_frame, values=list(UNIT_CATEGORIES.keys()), state="readonly", width=40)
        self.category_combo.grid(row=1, column=0, columnspan=3, pady=5, sticky=tk.W)
        self.category_combo.bind("<<ComboboxSelected>>", self.update_units)
        self.category_combo.current(0)

        # 2. 입력 값 및 원본 단위 선택
        ttk.Label(main_frame, text="변환할 값:", font=("맑은 고딕", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=10)
        self.input_entry = ttk.Entry(main_frame, width=15)
        self.input_entry.grid(row=3, column=0, pady=5, sticky=tk.W)
        self.input_entry.insert(0, "1")

        self.from_unit_combo = ttk.Combobox(main_frame, state="readonly", width=18)
        self.from_unit_combo.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        # 3. 대상 단위 선택
        ttk.Label(main_frame, text="변환할 결과 단위:", font=("맑은 고딕", 10, "bold")).grid(row=2, column=2, sticky=tk.W, pady=10)
        self.to_unit_combo = ttk.Combobox(main_frame, state="readonly", width=18)
        self.to_unit_combo.grid(row=3, column=2, pady=5, sticky=tk.W)

        self.update_units()

        # 4. 변환 버튼
        self.convert_btn = ttk.Button(main_frame, text="단위 변환 및 다단계 과정 출력", command=self.convert_units)
        self.convert_btn.grid(row=4, column=0, columnspan=3, pady=15, sticky="ew")

        # 5. 결과 및 변환 과정 표시창
        result_frame = ttk.LabelFrame(main_frame, text=" 상세 변환 과정 (차원해석 표) ", padding="15")
        result_frame.grid(row=5, column=0, columnspan=3, pady=5, sticky="ew")
        
        # 스크롤 가능한 텍스트 창 형태로 변경하여 긴 과정도 잘리지 않게 처리
        self.process_text_widget = tk.Text(result_frame, font=("Consolas", 10), height=7, width=95, bg="#f9f9f9", bd=1, relief="solid")
        self.process_text_widget.pack(anchor=tk.W, fill=tk.X)
        self.process_text_widget.config(state=tk.DISABLED)
        
        self.result_label = ttk.Label(result_frame, text="결과가 여기에 표시됩니다.", font=("맑은 고딕", 12, "bold"), foreground="blue")
        self.result_label.pack(pady=(10, 0))

    def update_units(self, event=None):
        selected_category = self.category_combo.get()
        units = UNIT_CATEGORIES[selected_category]
        self.from_unit_combo['values'] = units
        self.to_unit_combo['values'] = units
        self.from_unit_combo.current(0)
        if len(units) > 1:
            self.to_unit_combo.current(1)
        else:
            self.to_unit_combo.current(0)

    def convert_units(self):
        try:
            input_value = float(self.input_entry.get())
            from_unit = self.from_unit_combo.get()
            to_unit = self.to_unit_combo.get()

            # Pint 계산
            start_quantity = input_value * ureg(from_unit)
            converted_quantity = start_quantity.to(to_unit)
            
            selected_category = self.category_combo.get()
            
            # 텍스트창 초기화
            self.process_text_widget.config(state=tk.NORMAL)
            self.process_text_widget.delete("1.0", tk.END)

            if "온도" in selected_category:
                self.process_text_widget.insert(tk.END, f"온도 변환은 선형 비례가 아니므로 공식을 적용합니다.")
                if from_unit == "celsius" and to_unit == "fahrenheit":
                    self.process_text_widget.insert(tk.END, f"공식: [°F] = [°C] × 9/5 + 32")
                    self.process_text_widget.insert(tk.END, f"계산: {input_value} × 1.8 + 32 = {converted_quantity.magnitude:.4f}")
                elif from_unit == "fahrenheit" and to_unit == "celsius":
                    self.process_text_widget.insert(tk.END, f"공식: [°C] = ([°F] − 32) × 5/9")
                    self.process_text_widget.insert(tk.END, f"계산: ({input_value} − 32) × 5/9 = {converted_quantity.magnitude:.4f}")
                else:
                    self.process_text_widget.insert(tk.END, f"{from_unit}에서 {to_unit}로의 절대온도 스케일 자동 변환 적용")
            else:
                # Pint의 check() 메서드를 활용해 안전하게 차원을 비교하고 기준 단위를 설정합니다.
                if start_quantity.check('[length]'):
                    base_unit = "meter"
                elif start_quantity.check('[mass]'):
                    base_unit = "gram"
                elif start_quantity.check('[area]'):
                    base_unit = "meter ** 2"
                elif start_quantity.check('[volume]'):
                    base_unit = "liter"
                elif start_quantity.check('[speed]'):
                    base_unit = "meter_per_second"
                elif start_quantity.check('[pressure]'):
                    base_unit = "pascal"
                else:
                    base_unit = from_unit  # 분류가 모호하면 출발 단위를 기준 단위로 삼음
                
                # 다단계 경로 생성
                steps = []
                
                # 1단계: 출발 단위에서 기준 단위로 가는 환산 인자
                if from_unit != base_unit:
                    factor_to_base = (1 * ureg(from_unit)).to(base_unit).magnitude
                    steps.append((f"{factor_to_base:.4f}", base_unit, "1", from_unit))
                
                # 2단계: 기준 단위에서 목적 단위로 가는 환산 인자
                if to_unit != base_unit:
                    factor_from_base = (1 * ureg(base_unit)).to(to_unit).magnitude
                    steps.append((f"{factor_from_base:.4f}", to_unit, "1", base_unit))
                
                # 만약 출발단위와 목적단위가 같거나 바로 연결된다면 1단계만 생성
                if from_unit == base_unit or to_unit == base_unit:
                    steps = []
                    factor_direct = (1 * ureg(from_unit)).to(to_unit).magnitude
                    steps.append((f"{factor_direct:.4f}", to_unit, "1", from_unit))

                # 이미지 스타일의 격자(표) 텍스트 조립
                top_row = f" {input_value} {from_unit} "
                bot_row = f" {' ' * len(str(input_value))} {' ' * len(from_unit)} "
                
                for step in steps:
                    top_row += f"│ {step[0]} {step[1]} "
                    bot_row += f"│ {step[2]} {step[3]} "
                
                # 구분선 정의
                mid_row = "─" * max(len(top_row), len(bot_row))
                
                # 정렬을 맞추기 위해 공백 보정
                top_row = top_row.ljust(len(mid_row))
                bot_row = bot_row.ljust(len(mid_row))
                
                # 텍스트 위젯에 출력
                self.process_text_widget.insert(tk.END, top_row + "\n")
                self.process_text_widget.insert(tk.END, mid_row + "\n")
                self.process_text_widget.insert(tk.END, bot_row + "\n")
                
                self.process_text_widget.insert(tk.END, "\n* 안내: 분모와 분자의 동일 단위들이 연쇄적으로 소거(Cross-out)됩니다.")

            self.process_text_widget.config(state=tk.DISABLED)
            
            # 최종 결과 레이블 업데이트
            result_text = f"= {converted_quantity.magnitude:.4f} {to_unit}"
            self.result_label.config(text=result_text)

        except ValueError:
            messagebox.showerror("입력 오류", "올바른 숫자를 입력해 주세요.")
        except Exception as e:
            messagebox.showerror("오류", f"변환 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = UnitConverterApp(root)
    root.mainloop()
