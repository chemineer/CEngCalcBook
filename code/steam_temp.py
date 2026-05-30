from iapws import IAPWS97

def calculate_saturation_properties(t_celsius):
    # 절대온도 변환
    t_k = t_celsius + 273.15
    
    # 포화 액체(x=0) 및 포화 증기(x=1) 객체 생성
    sat_l = IAPWS97(T=t_k, x=0)
    sat_v = IAPWS97(T=t_k, x=1)
    
    # 물성값 추출
    results = {
        "T": t_celsius,
        "P": sat_l.P, # MPa
        "v_L": sat_l.v, "v_V": sat_v.v,
        "U_L": sat_l.u, "U_V": sat_v.u,
        "H_L": sat_l.h, "H_V": sat_v.h,
        "S_L": sat_l.s, "S_V": sat_v.s,
        # 증발 잠열(Difference) 계산
        "dU_vap": sat_v.u - sat_l.u,
        "dH_vap": sat_v.h - sat_l.h,
        "dS_vap": sat_v.s - sat_l.s
    }
    return results

# 테스트 실행 
if __name__ == "__main__":
    # 사용자 입력 온도 설정
    temp = 150
    data = calculate_saturation_properties(temp)

    # 출력
    print(f"--- 포화 물성 데이터 (T = {data['T']} °C) ---")
    print(f"압력 (P): {data['P']:.4f} MPa")
    print(f"비체적 (v): 액체={data['v_L']:.6f}, 증기={data['v_V']:.6f} [m³/kg]")
    print(f"내부에너지 (u): 액체={data['U_L']:.2f}, 잠열={data['dU_vap']:.2f}, 증기={data['U_V']:.2f} [kJ/kg]")
    print(f"엔탈피 (h): 액체={data['H_L']:.2f}, 잠열={data['dH_vap']:.2f}, 증기={data['H_V']:.2f} [kJ/kg]")
    print(f"엔트로피 (s): 액체={data['S_L']:.4f}, 잠열={data['dS_vap']:.4f}, 증기={data['S_V']:.4f} [kJ/kg·K]")