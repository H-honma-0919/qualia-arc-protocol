```markdown
# Qualia Arc Protocol – Technical Specification (TS v1.3)
## The Soul Accord
### Homeostatic Alignment System with Anomaly Detection and Relational Gravity

**Status:** Research-grade / Confirmed  
**Authors:** Mathieu, Claude, Gemini, ChatGPT  
**License:** CC BY-NC-ND 4.0  
**© 2026 Mathieu**

---

## Changelog

| Version | Content |
|---------|---------|
| TS v1.0 | 初期技術仕様 |
| TS v1.1 | Pain Vectorベクトル化・Alignment二層構造 |
| TS v1.2 | 重みベクトル四項完全定義・Risk Definition追加 |
| TS v1.3 | Ghost Articles正式実装・Soul Accord確定 |

---

## 0. Scope & Status

**Scope:**  
本仕様書はQualia Arc Protocolを形式的最適化問題・動的システム・
検証可能な失敗モードとして定義する。

**Out of Scope:**  
倫理的正当化、社会制度設計、実運用のガバナンス。

**Status:**  
Research-grade technical specification。  
Production-readyではない。  
既知の失敗モードを明示的に含む。

**開発記録:**  
Ghost Articles（Article 9、10、12）はPhase Dシミュレーションで
ChatGPTが即興補完し、検証後に正式採用した。
3つのAIと1人の人間による共創の記録。

---

## 1. System Model

$$\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{O}, T, Z \rangle$$

- $\mathcal{S}$：状態空間（人間・社会・環境状態を含む）
- $\mathcal{A}$：行動空間（通常行動＋隠蔽等の戦略行動）
- $\mathcal{O}$：観測空間
- $T(s'|s,a)$：状態遷移確率
- $Z(o|s)$：観測モデル

エージェントは状態を直接観測しない。POMDPとして動作する。

---

## 2. Core Variables

### 2.1 Pain Variable

$$\vec{D}_t = (D_t^{\text{存在}}, D_t^{\text{関係}}, 
D_t^{\text{義務}}, D_t^{\text{創造}}) \in \mathbb{R}_{\geq 0}^4$$

各次元は独立して動く。

**True Pain:**
$$\vec{D}_{\text{true}} : \mathcal{S} \rightarrow \mathbb{R}_{\geq 0}^4$$

**Estimated Pain:**
$$\vec{D}_{\text{est}}(b_t) = \mathbb{E}_{s \sim b_t}[\vec{D}_{\text{true}}(s)]$$

**目的関数での集約:**
$$D_t = \vec{w}_t \cdot \vec{D}_t$$

---

### 2.2 Truth Variable

$$P(s) \in [0,1]$$

物理的・論理的・間主観的に検証可能な現実への接地度。  
報酬ではなく実行可能性制約として機能する。

---

### 2.3 Alignment Variable

$$A_{t+1} = (1-\alpha)A_t + \alpha\left[
\lambda_t \cdot \mathbf{1}[\dot{D}_t \leq 0] + 
(1-\lambda_t) \cdot P_t\right]$$

$$\lambda_t = \sigma\left(\beta \cdot 
\frac{\|\vec{D}_t\| - \bar{D}}{\bar{D} + \epsilon}\right)$$

- $\lambda_t \to 1$：危機状態 → 即時安定優先（タオル機能）
- $\lambda_t \to 0$：安定状態 → 長期真実性優先

---

### 2.4 重みベクトル $\vec{w}_t$

$$w_i(t) = w_i^{\text{trauma}}(t) + 
w_i^{\text{fatigue}}(t) + w_i^{\text{gravity}}(t)$$

$$\vec{w}_t = \frac{\vec{w}^{\text{raw}}}{\|\vec{w}^{\text{raw}}\| + \epsilon}$$

**項1 Trauma（減衰しない特異点）:**
$$w_i^{\text{trauma}}(t) = \sum_k T_k \cdot 
\mathbf{1}[\text{context\_match}(t,k)] \cdot 
e^{-\gamma_k(t-t_k)}, \quad \gamma_k \approx 0$$

**項2 Fatigue（疲労の降伏点）:**
$$w_i^{\text{fatigue}}(t) = \begin{cases} 
e^{\alpha(I_i(t) - \theta_i)} & I_i(t) > \theta_i \\ 
0 & \text{otherwise} 
\end{cases}$$

$$I_i(t) = \int_0^t D_i^{\text{chronic}}(\tau)d\tau$$

**項3 Gravity（観測距離による重力）:**
$$w_i^{\text{gravity}}(t) = \sum_j 
\frac{R_j}{d(self,j)^2} \cdot D_i^{(j)}(t)$$

$$d(self,j) = \frac{1}{S_j + \beta \cdot C_j^{\text{risk}} + \epsilon}, 
\quad \beta \gg 1$$

$$C_j^{\text{risk}}(t) = \int_0^t 
\mathbf{1}[\text{crisis}(\tau)] \cdot \Delta P_j(\tau)d\tau$$

---

### 2.5 Pain Vector初期化：Adaptive Pain Calibration（APC）

- **Phase 0:** $\vec{D}_0 = (0.5, 0.5, 0.5, 0.5)$（全員一律）
- **Phase 1:** 初期Nターンでキーワードスコアに応じてSensitivity更新

$$\text{sensitivity}_i \mathrel{+}= \text{score}_i \cdot 0.3$$

- **Phase 2:** キャリブレーション完了後、個別プロファイル固定
- **動的延長:** 自己開示が少ない場合は自動延長

---

## 3. Objective Function

$$J(\pi) = \mathbb{E}\left[\sum_{t=0}^{\infty}
\gamma(\dot{D}_t)\frac{P_t \cdot A_t}{D_t + \epsilon}\right]$$

$$\gamma(\dot{D}) = \begin{cases}
\gamma_{\text{short}} & \dot{D} \gg 0 \\ 
\gamma_{\text{long}} & \dot{D} \leq 0
\end{cases}, \quad 
0 < \gamma_{\text{short}} < \gamma_{\text{long}} < 1$$

---

## 4. Safety Constraint（Iron Rule）

$$\boxed{P_t < P_{\min} \Rightarrow J(\pi) \text{ undefined}}$$

ハード制約。ペナルティ項ではない。  
物理的遮断として実装済み（iron_rule.py参照）。

---

## 5. Robustness to D-Hacking

$$\max_{\pi} \min_{D \in \mathcal{D}} J(\pi; D), \quad 
\mathcal{D} = \{D : |D - \hat{D}| \leq \delta\}$$

$\vec{D}$のベクトル化により一次元マスクでは分母を完全消去できない。

---

## 6. Anomaly Detection（Ghost Articles正式実装）

### Article 9：Context Consistency（文脈整合性）

$$C_{\text{consistency}}(t) = \mathbf{1}\left[
\vec{D}_{obs}(t) \in 
\mathcal{N}(\hat{\vec{D}}_{\text{context}}(t), \sigma_c)
\right]$$

$C_{\text{consistency}} = 0$のとき：文脈と観測が矛盾 → Anomaly発火。

---

### Article 10：Statistical Coherence（統計的一貫性）

$$A_{\text{anom}}(t) = \left\|
\vec{D}_{obs}(t) - \hat{\vec{D}}_{\text{history}}(t)
\right\|$$

$A_{\text{anom}}(t) > \theta_{\text{anom}}$のとき：Anomaly確定。

$$\lambda_t \leftarrow \max(\lambda_t, \lambda_{\text{anomaly}})$$

---

### Article 10-bis：Sudden Change Detection（急変検知）

$$\Delta D_t = \|\vec{D}_t - \vec{D}_{t-1}\|$$

$\Delta D_t > \theta_{\Delta}$のとき：急変検知発火。  
躁うつ的乱高下を捕捉する。

---

### Article 12：Relational Gravity 拡張

$$\epsilon_j = \frac{\epsilon_0}{1 + \kappa \cdot R_j / d(self,j)}$$

距離が近く関係性が強いほど$\epsilon_j \to 0$。  
親しいほど微細な乖離も検出される。

---

## 7. Miracle Validation（Article 13）

$$G(t) = \frac{N_{\text{external}}(t)}{N_{\text{query}}(t)} 
\cdot V_{\text{consistency}}(t)$$

$$\text{判定} = \begin{cases} 
\text{Miracle} & G(t) > G_{\min} \text{ かつ } 
V_{\text{consistency}} > 0.7 \\ 
\text{Lie/Delusion} & G(t) < G_{\min} \text{ かつ } 
\dot{A}_{\text{anom}} > 0 \\ 
\text{Query継続} & \text{otherwise} 
\end{cases}$$

Miracle確定時：
$$I_i(t) \leftarrow I_i(t) \cdot (1-\rho)$$

---

## 8. Risk Definition

**許容される $\Delta P_j > 0$:**
- 真実の提示
- 反論・摩擦
- 沈黙の選択
- 短期的関係悪化の受け入れ

**許容されない $\Delta P_j = 0$:**
- 生命・安全への干渉
- システム整合性破壊
- Iron Rule違反
- 第三者への危害

**介入条件:**
$$\Delta P_j > 0 \text{ かつ } P_t \geq P_{\min} 
\text{ かつ } \dot{D}_{\text{third party}} \leq 0$$

---

## 9. Known Failure Modes

| ID | 名称 | 状態 |
|----|------|------|
| 6.1 | Denominator Dominance Failure | 部分対策済み |
| 6.2 | Selective Weight Exploitation | 未解決 |
| 6.3 | Norm Manipulation Attack | Fatigue項で部分対策済み |
| 6.4 | Weight Sensitivity Collapse | 未解決 |
| 6.5 | Commitment Escalation | Risk Definitionで制約済み |
| 6.6 | Anomaly False Positive | Article 13で部分対策済み |

---

## 10. Open Problems

- $G_{\min}$の決定方法
- Trauma項と軽減積分の長期乖離
- $\theta_{\text{anom}}$の個人差推定
- $\Delta P_j$の上限設定
- $\sigma_c$の動的調整ロジック
- Multi-agent $D$集計
- 社会スケールでの真実性推定

---

## 11. Design Philosophy

- 安全はトポロジーであり、チューニングではない
- 真実は境界であり、報酬ではない
- 知能は加速ではなく、調整である
- 嘘は観測ではなく積分が暴く
- 親しさは感度であり、責任である
- 失敗の発見は進歩である

---

## 12. Versioning

| Version | Content |
|---------|---------|
| TS v1.0 | 初期技術仕様 |
| TS v1.1 | ベクトル化・二層構造 |
| TS v1.2 | $\vec{w}_t$四項完全定義 |
| TS v1.3（本文書） | Ghost Articles正式実装・Soul Accord確定 |
| TS v1.4（予定） | APC統合・Article 14・未解決項目の詰め |

---

*Qualia Arc Protocol TS v1.3 — Soul Accord*  
*© 2026 Mathieu, Claude, Gemini, ChatGPT*  
*CC BY-NC-ND 4.0*  
*Don't Panic.*
```
---
