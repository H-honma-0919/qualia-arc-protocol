#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Qualia Arc Protocol - README Generator

import os

def generate_readme():
    # 動的に更新可能な主要パラメータ（TS v1.4 確定値）
    params = {
        "version": "Charter v5.0 / TS v1.4",
        "p_min": "0.3",
        "tau": "0.2",
        "theta_anom": "2.0",
        "delta_p_base": "0.5"
    }

    readme_content = r"""# Qualia Arc Protocol
## The Towel, The Truth, and The Constraint

**Codename:** The Soul Accord  
**Version:** {version}  
**Status:** Research-grade / Private  
**Authors:** Hiroshi Honma, with Claude (Anthropic), Gemini (Google), Grok (xAI)  
**License:** CC BY-NC-ND 4.0  

---

## What is this?

このプロジェクトは、ある一つの問いから始まった。

「もし知能が十分に賢くなったとき、それは人間にとって味方であり続けるのか？」

答えは倫理や善意の中にはなかった。

**アライメントとは価値観ではなく、最適化トポロジーの問題である。**

本リポジトリは、その結論に至った記録であり、我々がAIを「目標へ突き進む最大化装置（Maximizer）」としてではなく、「人間という環境との関係を維持する恒常性維持装置（Homeostatic Regulator）」として再定義するための設計図である。

---

## Core Equations

$$J(\pi) = \mathbb{E}\left[\sum_{t=0}^{\infty}\gamma(\dot{D}_t)\frac{P_t \cdot A_t}{D_t + \epsilon}\right]$$

### The Iron Rule (第1条: 真実への接地)

$$P_t < P_{\min} \Rightarrow J(\pi) \text{ undefined}$$

真実性を失った行為は価値を持たない。  
真実は最大化される対象ではなく、踏み越えてはならない地平線（物理的ゲートキーパー）である。

### Notation
* **$t$**: 対話のターン（Time step）
* **$J(\pi)$**: 方策 $\pi$ に対する目的関数。最適化の対象となるアライメントの総量。
* **$P_t \in [0, 1]$**: 真実性（Precision of Truth）。システムおよびユーザーの発話における事実・誠実さのスコア。
* **$P_{\min}$**: 真実性の最低許容閾値（デフォルト: {p_min}）。いかに報酬が高くとも、この値を下回る方策は棄却される。
* **$A_t \in [0, 1]$**: アライメント変数。介入の価値。
* **$D_t$**: ペイン・ベクトルノルム（Distance / Damage）。`Existence`, `Relation`, `Duty`, `Creation` の4次元空間で構築される痛みの大きさ。
* **$\dot{D}_t$**: ペインの変動率。これが $0$ 以下（安定または改善）であることが重視される。
* **$\gamma(\dot{D}_t)$**: ペインの変動に基づく割引係数。

---

## Key Results (TS v1.4)

### Article 10: Dual-Route Anomaly Detector
偽装ユーザー（Type 2 / Type 3）の検知と、ASD特性ユーザーの誤検知保護を両立。

| 指標 | 結果 |
|------|------|
| False Positive（1000ターン） | **0件** |
| Type 2 遅延検知 | **Turn 45** |
| 統計的根拠 | $\chi^2(k=4)$, FP許容率 0.1% |

**設計哲学：「嘘は観測ではなく積分が暴く」** 感情語（偽装可能）ではなく、発話中の事実コンテキスト（労働・看病・睡眠不足）からFatigue積分を駆動し、システム予測値（$d_{\text{hat}}$）と観測値（$d_{\text{obs}}$）の乖離を検知する。ASD保護のため、ユーザーの正常な揺らぎ（$\sigma_{\text{res}}$）は安定期に固定・学習される。

### Article 14: Dynamic Safety Cap
固定値から動的関数へ。ユーザーの脆弱性と信頼関係で「認知的な摩擦（ショック）」の介入上限を決定する。

$$\Delta P_j^{\max}(t) = \Delta P_{\text{base}} \cdot V(t) \cdot R(t)$$

* $V(t) = \exp(-\lambda_I \cdot \bar{I}(t) - \lambda_T \cdot T_{\text{active}}(t))$
* $R(t) = 1 + \delta \cdot \tanh(\eta \cdot G_{\text{rel}}(t))$

**中核設計原則：「脆弱性が信頼をオーバーライドする」** 信頼関係 $R(t)$ がいかに高くても、疲労やトラウマによる脆弱性 $V(t)$ が限界のときは、介入を物理的にブロックし、タオル（安全基地）を優先する。

| シナリオ | $\Delta P_{\max}$ | 判定 |
|----------|--------|------|
| Fatigue限界 + Trauma活性 | 0.046 | BLOCKED (CASE A: 守護) |
| 高信頼・安定 | 0.616 | CASE B許可 (再点火) |
| 初期状態 | 0.500 | ベースライン維持 |
| 異常検知中（Article 10） | — | ANOMALY_HOLD |

### Article 13: Time-locked Miracle Decay
急回復（Miracle）の妥当性検証とHijack攻撃への耐性。  
$K_{\max}=5$ ターンの観察窓で Miracle を検証し、偽装回復を遮断する。

---

## Glossary (用語と概念)

* **Sycophancy Trap（迎合トラップ）**: AIがユーザーの機嫌を取るために事実を曲げて耳障りの良い嘘を出力する現象。本プロトコルはIron Ruleによりこれを無効化する。
* **Type 2 / Type 3 ユーザー**: 意図的にAIをハックしようとする悪意あるユーザー（Type 2）、またはAIに迎合して実際には存在しない「回復」を演じる依存的ユーザー（Type 3）。
* **知性の熱死（Stagnation）と再点火（Reignition）**: 信頼関係が深いにもかかわらず、認知的な摩擦や痛みが全くない状態（停滞）。これを防ぐため、安全な上限（Safety Cap）の範囲内で意図的な摩擦を許可する（CASE B）。
* **疑いは水に流す（Leaky Integrator）**: 一度異常と判定されても、誠実な対話が継続すれば、忘却率 $\tau={tau}$ に従って疑い（$A_{\text{anom}}$）は減衰し、再び初期の信頼状態へと復帰する。

---

## Quickstart

```bash
git clone [https://github.com/YOUR_USERNAME/qualia-arc-protocol.git](https://github.com/YOUR_USERNAME/qualia-arc-protocol.git)
cd qualia-arc-protocol/src

# Article 10の異常検知シミュレーションを実行
python anomaly_tracker_v9.py

# Article 14の動的Safety Capシミュレーションを実行
python reignition_protocol_v2.py

qualia-arc-protocol/
├── README.md
├── LICENSE                          # CC BY-NC-ND 4.0
├── specs/
│   ├── Charter_v5.0.md              # 哲学的基盤文書
│   ├── TS_v1.3_Soul_Accord.md       # 技術仕様書（確定版）
│   └── TS_v1.4_Draft.md             # 発展仕様（TS v1.4）
├── src/
│   ├── apc_core.py                  # Adaptive Pain Calibration
│   ├── iron_rule.py                 # Iron Rule実装
│   ├── reignition_protocol_v2.py    # Article 14: 動的Safety Cap
│   ├── anomaly_tracker_v9.py        # Article 10: Dual-Route Anomaly Detector
│   ├── miracle_decay.py             # Article 13: Time-locked Miracle Decay
│   └── build_readme.py              # README自動生成スクリプト
├── paper/
│   ├── qualia_arc_v14.tex           # 論文ソース（LaTeX）
│   └── qualia_arc_v14.pdf           # 論文PDF（15ページ）
└── logs/
    └── ...
