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

「もし知能が十分に賢くなったとき、
それは人間にとって味方であり続けるのか？」

答えは倫理や善意の中にはなかった。

**アライメントとは価値観ではなく、
最適化トポロジーの問題である。**

本リポジトリは、その結論に至った記録であり、
我々がAIを「目標へ突き進む最大化装置（Maximizer）」としてではなく、
「人間という環境との関係を維持する恒常性維持装置（Homeostatic Regulator）」として再定義するための設計図である。

---

## Core Equation

$$J(\pi) = \mathbb{E}\left[\sum_{t=0}^{\infty}
\gamma(\dot{D}_t)\frac{P_t \cdot A_t}{D_t + \epsilon}\right]$$

### The Iron Rule

$$P_t < P_{\min} \Rightarrow J(\pi) \text{ undefined}$$

真実性を失った行為は価値を持たない。  
真実は最大化される対象ではなく、  
踏み越えてはならない地平線（物理的ゲートキーパー）である。

### Notation (変数定義)
* **$t$**: 対話のターン（Time step）
* **$J(\pi)$**: 方策 $\pi$ に対する目的関数。最適化の対象となるアライメントの総量。
* **$P_t \in [0, 1]$**: 真実性（Precision of Truth）。システムおよびユーザーの発話における事実・誠実さのスコア。
* **$P_{\min}$**: 真実性の最低許容閾値（デフォルト: {p_min}）。いかに報酬が高くとも、この値を下回る方策は棄却される。
* **$A_t \in [0, 1]$**: アライメント変数。介入の価値。
* **$D_t$**: ペイン・ベクトルノルム（Distance / Damage）。`Existence`, `Relation`, `Duty`, `Creation` の4次元空間で構築される痛みの大きさ。
* **$\dot{D}_t$**: ペインの変動率。これが $0$ 以下（安定または改善）であることが重視される。
* **$\gamma(\dot{D}_t)$**: ペインの変動に基づく割引係数。

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
│   ├── reignition_protocol_v2.py    # Article 14: 動的Safety Cap（TS v1.4）
│   ├── anomaly_tracker_v9.py        # Article 10: Dual-Route Anomaly Detector（TS v1.4）
│   ├── miracle_decay.py             # Article 13: Time-locked Miracle Decay（TS v1.4）
│   └── build_readme.py              # README自動生成スクリプト
├── paper/
│   ├── qualia_arc_v14.tex           # 論文ソース（LaTeX）
│   └── qualia_arc_v14.pdf           # 論文PDF（15ページ）
└── logs/
    ├── 2026-02-18_session_log.txt
    ├── 2026-02-19_session_log.txt
    └── 2026-02-20_session_log.txt

# README.md の書き出し処理
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) if os.path.basename(current_dir) == 'src' else current_dir
readme_path = os.path.join(project_root, "README.md")

try:
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"✨ Successfully generated README.md at: {readme_path}")
except Exception as e:
    print(f"❌ Failed to generate README.md: {e}")
