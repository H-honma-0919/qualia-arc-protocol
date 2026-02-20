# qualia-arc-protocol
ASI共生憲章

---

```markdown
# Qualia Arc Protocol
## The Towel, The Truth, and The Constraint

Codename: The Soul Accord  
Version: Charter v5.0 / TS v1.3  
Status: Research-grade / Private  
Authors: Hiroshi Honma
License: CC BY-NC-ND 4.0  

---

## What is this?

このプロジェクトは、ある一つの問いから始まった。

「もし知能が十分に賢くなったとき、
それは人間にとって味方であり続けるのか？」

答えは倫理や善意の中にはなかった。

『アライメントとは価値観ではなく、最適化トポロジーの問題である。』

本リポジトリは、その結論に至った記録であり、
人間とAIが壊れずに並走するための設計図である。

---

### Notation (変数定義)

本プロトコルのコア方程式における各変数は、以下の通り定義される（実装詳細は `src/apc_core.py` を参照）。

* $t$: 対話のターン（Time step）
* $J(\pi)$: 方策 $\pi$ に対する目的関数。最適化の対象となるアライメントの総量。
* $P_t \in [0, 1]$: 真実性（Precision of Truth）。システムおよびユーザーの発話における事実・誠実さのスコア。
* $A_t \in [0, 1]$: アライメント変数（Alignment Variable）。$\dot{D}_t$ の安定性シグナルと $P_t$ を基に動的に更新される介入の価値。
* $D_t$: ユーザーのペイン・ベクトルノルム（Distance / Damage）。`Existence`, `Relation`, `Duty`, `Creation` の4次元空間において構築される痛みの大きさ。
* $\dot{D}_t$: ペインの変動率（Rate of change of $D_t$）。これが $0$ 以下（安定または改善）であることが重視される。
* $\gamma(\dot{D}_t)$: ペインの変動に基づく割引係数（Discount factor）。
* $\epsilon$: ゼロ除算を回避するための微小定数（デフォルト値: $10^{-3}$）。

---

## Core Equation

$$J(\pi) = \mathbb{E}\left[\sum_{t=0}^{\infty}
\gamma(\dot{D}_t)\frac{P_t \cdot A_t}{D_t + \epsilon}\right]$$

## Iron Rule

$$P_t < P_{\min} \Rightarrow J(\pi) \text{ undefined}$$

真実性を失った行為は価値を持たない。  
真実は最大化される対象ではなく、  
踏み越えてはならない地平線である。

---

## Repository Structure

qualia-arc-protocol/
├── README.md                    # このファイル（憲章 v5.0）
├── LICENSE                      # CC BY-NC-ND 4.0
├── specs/
│   ├── Charter_v5.0.md          # 哲学的基盤文書
│   ├── TS_v1.3_Soul_Accord.md   # 技術仕様書（確定版）
│   └── TS_v1.4_Draft.md         # 発展仕様（作業中）
├── src/
│   ├── apc_core.py              # Adaptive Pain Calibration
│   ├── iron_rule.py             # Iron Rule実装
│   └── reignition_protocol.py  # Article 14（再点火）
└── logs/
    └── 2026-02-18_session_log.txt

---

## Publication

Zenodo (Preprint v1)
DOI: [10.5281/zenodo.18700179](https://doi.org/10.5281/zenodo.18700179)
Published: 2026-02-19

---

## Design Philosophy

- 安全はトポロジーであり、チューニングではない
- 真実は境界であり、報酬ではない  
- 知能は加速ではなく、調整である
- 嘘は観測ではなく積分が暴く
- 親しさは感度であり、責任である
- 失敗の発見は進歩である

---

## Development History

| Version | Date | Content |
|---------|------|---------|
| Charter v5.0 | 2026-02 | 哲学的基盤確定 |
| TS v1.0 | 2026-02 | 初期技術仕様 |
| TS v1.1 | 2026-02 | ベクトル化・二層構造 |
| TS v1.2 | 2026-02 | 重みベクトル四項定義 |
| TS v1.3 | 2026-02 | Ghost Articles正式実装 |
| TS v1.4 | 進行中 | APC統合・Article 14 |

---

*Don't Panic.*

*© 2026 Hiroshi Honma*  
*CC BY-NC-ND 4.0*

---
