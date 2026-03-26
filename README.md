## 💧 Smart Water Quality Monitoring System

본 프로젝트는 한국수자원공사의 실시간 수도 수질 API를 활용하여  
탁도(tbVal), pH(phVal), 잔류염소(clVal) 데이터를 수집하고 시각화하는 IoT 기반 시스템입니다.

탁도는 7-Segment(FND)에 수치로 표시되며,  
pH 값은 RGB LED 색상을 통해 수질 상태를 직관적으로 표현합니다.

---

### ⚙️ 주요 기능
- 공공 API를 통한 실시간 수질 데이터 수집
- 탁도 값 7-Segment(FND) 출력
- pH 기반 수질 상태 분석
- RGB LED를 활용한 시각화

---

### 🧪 수질 상태 기준
- pH < 6.5 → 🔴 산성 (RED)
- 6.5 ≤ pH ≤ 7.5 → 🟢 정상 (GREEN)
- pH > 7.5 → 🔵 알칼리 (BLUE)

---

### 🎯 프로젝트 목적
공공데이터와 IoT 기술을 결합하여  
수질 정보를 직관적으로 확인할 수 있는 실시간 모니터링 시스템 구현
