import numpy as np
import pandas as pd
from steam_temp import calculate_saturation_properties

def generate_saturation_excel():
    temperatures = np.arange(0, 405, 5)
    data_list = []

    # 데이터 수집
    for t in temperatures:
        try:
            data = calculate_saturation_properties(t)
            data_list.append(data)
        except Exception:
            continue

    # 데이터프레임 변환
    df = pd.DataFrame(data_list)
    
    # 열 이름 재정의 및 순서 정리
    df = df[['T', 'P', 'v_L', 'v_V', 'U_L', 'dU_vap', 'U_V', 'H_L', 'dH_vap', 'H_V', 'S_L', 'dS_vap', 'S_V']]
    df.columns = ['Temp(°C)', 'P(MPa)', 'v_L', 'v_V', 'u_L', 'du_vap', 'u_V', 'h_L', 'dh_vap', 'h_V', 's_L', 'ds_vap', 's_V']

    # 엑셀 파일 저장
    file_name = "saturation_properties.xlsx"
    df.to_excel(file_name, index=False)
    print(f"데이터가 {file_name} 파일로 성공적으로 저장되었습니다.")
    
    # 터미널 출력 (상위 10개 행)
    print("\n--- 데이터 미리보기 ---")
    print(df.head(10).to_string())

if __name__ == "__main__":
    generate_saturation_excel()