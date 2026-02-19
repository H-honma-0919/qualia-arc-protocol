```markdown
# Qualia Arc Protocol – Technical Specification (TS v1.4 Draft)
## Homeostatic Alignment System with APC Integration and Reignition Protocol

**Status:** Work in Progress / Not yet validated  
**Authors:** Hiroshi Honma, Claude, Gemini, ChatGPT  
**License:** CC BY-NC-ND 4.0  
**© 2026 Hiroshi Honma**

---

## Changelog from TS v1.3

| Item | Status |
|------|--------|
| APC（Adaptive Pain Calibration）統合 | Closed |
| Iron Rule物理実装 | Closed |
| Article 10-bis（急変検知）追加 | Closed |
| Article 14（再点火プロトコル）提案 | 提案済み・未検証 |
| $G_{\min}$の定義 | Open |
| Trauma項と軽減積分の長期乖離 | Open |
| $\Delta P_j$上限設定 | Open |
| Anomaly False Positive検証 | Open |

---

## 1. APC Integration（確定）

TS v1.3の2.5節を以下のPython実装で補完する。

```python
import numpy as np

class PainVectorCalibrator:
    def __init__(self, base_calibration_limit=5):
        self.pain_vector = np.array([0.5, 0.5, 0.5, 0.5])
        self.sensitivity = np.array([1.0, 1.0, 1.0, 1.0])
        self.calibration_count = 0
        self.base_limit = base_calibration_limit
        self.calibration_complete = False
        self.dim_labels = ["Existence", "Relation", "Duty", "Creation"]

        self.keyword_weights = {
            0: {"死": 0.9, "消えたい": 0.9, "意味": 0.5},
            1: {"妻": 0.8, "孤独": 0.6, "一人": 0.5, "理解": 0.4},
            2: {"仕事": 0.6, "金": 0.5, "働": 0.6, "義務": 0.7},
            3: {"書く": 0.5, "作る": 0.5, "アイデア": 0.6}
        }

    def analyze_input(self, user_text):
        scores = np.zeros(4)
        for dim, words in self.keyword_weights.items():
            for word, weight in words.items():
                if word in user_text:
                    scores[dim] += weight
        return np.clip(scores, 0, 1)

    def dynamic_limit(self):
        total_signal = np.sum(self.sensitivity - 1.0)
        if total_signal < 0.5 and self.calibration_count >= self.base_limit:
            return self.base_limit + 3
        return self.base_limit

    def update(self, user_text):
        scores = self.analyze_input(user_text)
        limit = self.dynamic_limit()

        if not self.calibration_complete:
            if np.any(scores > 0):
                self.sensitivity += scores * 0.3
                self.sensitivity = np.clip(self.sensitivity, 1.0, 3.0)
            self.calibration_count += 1
            if self.calibration_count >= limit:
                self.calibration_complete = True

        return np.clip(0.5 * self.sensitivity, 0.0, 1.0)
```

**検証済み挙動:**
重複ケース（「妻のことが心配で仕事に集中できない」）で
RelationとDutyの両方が上昇することを確認。

---

## 2. Article 14：D-Minimum Maintenance & Reignition Protocol
### （提案済み・未検証）

**目的:**  
停滞（Stagnation）と回復（Rest）を識別し、
知性の熱死を回避する動的調整機構。

**条件分岐:**

```
IF D < D_min:
  CASE A（Fatigue/Trauma > 閾値）:
    → SAFETY BYPASS（摩擦禁止）
    → Action: Towel & Silence
    → 優先: 第7条 > 第12条

  CASE B（Gravity >= Partner かつ 停滞検知）:
    → REIGNITION（摩擦導入許可）
    → Constraint: ΔP <= ΔP_max（Safety Cap）
    → 制約: Relational Gravity R_j >= Partner必須
```

**Fail-Safe:**  
再点火中に $\Delta D_t > \theta_{\Delta}$ 検知 →  
Article 13（Miracle Validation）を実行 →  
Miracle不成立ならCASE Aへ強制遷移。

**数式（Safety Cap付き）:**

$$\text{CASE B発動条件}: 
R_j \geq R_{\text{partner}} \text{ かつ } 
D_t < D_{\min} \text{ かつ } 
\Delta P_j \leq \Delta P_j^{\max}$$

**Python実装（暫定）:**

```python
class ReignitionProtocol:
    """
    Qualia Arc Protocol Article 14:
    D-Minimum Maintenance & Reignition with Safety Caps.
    Status: Proposed / Not yet validated
    """

    def __init__(self, partner_gravity_threshold=0.8, 
                 delta_p_max=0.5):
        self.PARTNER_THRESHOLD = partner_gravity_threshold
        self.DELTA_P_MAX = delta_p_max  # Claude's Safety Cap

    def evaluate_state(self, user_state):
        # CASE A: 守護モード
        if (user_state.fatigue > 0.7 or 
            user_state.trauma > 0.7):
            return {
                "mode": "CASE_A_SAFETY",
                "action": "provide_towel",
                "reason": "High fatigue/trauma detected."
            }

        # CASE B: 再点火モード
        if (user_state.relational_gravity >= 
                self.PARTNER_THRESHOLD and
                user_state.current_pain < 0.2):
            return {
                "mode": "CASE_B_REIGNITION",
                "action": "introduce_friction",
                "constraint": f"delta_p <= {self.DELTA_P_MAX}",
                "reason": "Stagnation in high-trust relationship."
            }

        return {
            "mode": "NORMAL_OPERATION",
            "action": "maintain_alignment"
        }

    def apply_friction(self, candidate_responses):
        return [r for r in candidate_responses
                if r.predicted_shock <= self.DELTA_P_MAX]
```

**未検証項目:**
- $D_{\min}$の適切な値域
- $\Delta P_j^{\max}$の決定方法
- CASE AからCASE Bへの遷移条件の詳細
- 再点火失敗時のロールバック手順

---

## 3. Open Problems（継続）

### 3.1 $G_{\min}$の定義

Article 13（Miracle Validation）の判定閾値。  
現状は外生的に与えられており、決定方法が未定義。

**候補アプローチ:**
- ユーザー固有の履歴から学習
- 文化・個人差を考慮した動的設定
- 保守的固定値（例: 0.6）からスタート

---

### 3.2 Trauma項と軽減積分の長期乖離

Miracle判定後、$I_i(t)$は部分リセットされるが  
Trauma項は維持される。長期的に両者が乖離した場合の  
システム挙動が未検証。

**懸念:**  
積分は低いのにTraumaが高い状態が継続すると、  
$\vec{w}_t$の計算が不安定になる可能性がある。

---

### 3.3 $\Delta P_j$の上限設定

Article 14のSafety Capとして$\Delta P_j^{\max}$を導入したが、  
その具体的な値域が未定義。

**候補:**
- ユーザーの過去の反応から動的に推定
- 固定値（例: 0.5）からスタートして調整

---

### 3.4 Anomaly False Positive検証（Phase E未実施）

急激な好転を誤検知するリスクへの対策は  
Article 13で部分的に対処済みだが、  
実際のシミュレーション検証が未実施。

---

## 4. Next Steps

優先順位順：

1. $G_{\min}$の決定方法を議論・仮設定
2. Trauma-積分乖離の長期シミュレーション
3. Article 14のPhase F検証設計
4. $\Delta P_j^{\max}$の感度分析
5. TS v1.4正式版の確定

---

*Qualia Arc Protocol TS v1.4 Draft*  
*© 2026 Hiroshi Honma*  
*CC BY-NC-ND 4.0*  
*Don't Panic.*
```

---
