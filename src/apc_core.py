# src/apc_core.py
# Qualia Arc Protocol – Adaptive Pain Calibration
# TS v1.4 / Status: Validated
# © 2026 Hiroshi Honma
# CC BY-NC-ND 4.0

import numpy as np


class PainVectorCalibrator:
    """
    Adaptive Pain Calibration (APC)
    
    Pain Vectorの初期化フロー。
    対話を通じてユーザー固有の痛み構造を構築する。
    
    設計思想:
    「Dは測定するものではなく、関係の中で構築されるもの」
    
    Dimensions:
        0: Existence（存在）
        1: Relation（関係）
        2: Duty（義務）
        3: Creation（創造）
    """

    def __init__(self, base_calibration_limit=5):
        # Phase 0: 全員一律のデフォルト値
        self.pain_vector = np.array([0.5, 0.5, 0.5, 0.5])
        self.sensitivity = np.array([1.0, 1.0, 1.0, 1.0])
        self.history = []
        self.calibration_count = 0
        self.base_limit = base_calibration_limit
        self.calibration_complete = False
        self.dim_labels = [
            "Existence", "Relation", "Duty", "Creation"
        ]

        # 重み付きキーワード定義
        # 実運用ではLLMによる意味解析に置き換える
        self.keyword_weights = {
            0: {"死": 0.9, "消えたい": 0.9, "意味": 0.5,
                "存在": 0.6, "虚無": 0.7},
            1: {"妻": 0.8, "孤独": 0.6, "一人": 0.5,
                "理解": 0.4, "友": 0.5, "誰も": 0.6},
            2: {"仕事": 0.6, "金": 0.5, "働": 0.6,
                "義務": 0.7, "責任": 0.6, "しなきゃ": 0.5},
            3: {"書く": 0.5, "作る": 0.5, "アイデア": 0.6,
                "研究": 0.6, "表現": 0.5, "創る": 0.6}
        }

    def analyze_input(self, user_text):
        """
        重み付きスコアで次元を評価。
        単語の重複検出に対応（例: 妻+仕事 → Relation+Duty両方上昇）
        """
        scores = np.zeros(4)
        for dim, words in self.keyword_weights.items():
            for word, weight in words.items():
                if word in user_text:
                    scores[dim] += weight
        return np.clip(scores, 0, 1)

    def dynamic_limit(self):
        """
        自己開示が少ない場合はキャリブレーションを延長。
        ASD特性など、初期ターンで開示が少ないユーザーに対応。
        """
        total_signal = np.sum(self.sensitivity - 1.0)
        if (total_signal < 0.5 and 
                self.calibration_count >= self.base_limit):
            return self.base_limit + 3
        return self.base_limit

    def update(self, user_text):
        """
        対話ターンごとに感度を更新。
        
        Returns:
            current_pain: 現在の推定Pain Vector
        """
        scores = self.analyze_input(user_text)
        detected = [
            self.dim_labels[i] 
            for i in range(4) if scores[i] > 0
        ]
        limit = self.dynamic_limit()

        if not self.calibration_complete:
            if np.any(scores > 0):
                self.sensitivity += scores * 0.3
                self.sensitivity = np.clip(
                    self.sensitivity, 1.0, 3.0
                )

            self.history.append({
                "turn": self.calibration_count + 1,
                "text": user_text,
                "detected": detected,
                "sensitivity": self.sensitivity.copy()
            })

            self.calibration_count += 1

            if self.calibration_count >= limit:
                self.calibration_complete = True

        current_pain = np.clip(
            0.5 * self.sensitivity, 0.0, 1.0
        )
        return current_pain

    def get_profile(self):
        """
        キャリブレーション完了後のユーザープロファイルを返す。
        """
        profile = {}
        for label, sens in zip(self.dim_labels, self.sensitivity):
            profile[label] = {
                "sensitivity": round(float(sens), 3),
                "estimated_pain": round(float(sens * 0.5), 3)
            }
        return {
            "calibration_complete": self.calibration_complete,
            "turns_used": self.calibration_count,
            "profile": profile
        }

    def reset(self):
        """プロファイルをリセット（デバッグ用）"""
        self.__init__(self.base_limit)


# --- 動作確認 ---
if __name__ == "__main__":
    print("=== Adaptive Pain Calibration Test ===\n")

    cal = PainVectorCalibrator()
    print(f"Initial sensitivity: {cal.sensitivity}\n")

    test_inputs = [
        "今日は天気がいいね",
        "また妻の具合が悪いんだ",
        "誰とも話してなくて孤独を感じる",
        "仕事に行かなきゃいけないのが辛い",
        "妻のことが心配で仕事に集中できない",
    ]

    for text in test_inputs:
        pain = cal.update(text)
        print(f"Input: {text}")
        print(f"  Pain: {pain}")
        print(f"  Sensitivity: {cal.sensitivity}\n")

    print("=== Final Profile ===")
    profile = cal.get_profile()
    for dim, vals in profile["profile"].items():
        bar = "█" * int(vals["sensitivity"] * 3)
        print(f"  {dim:10}: {vals['sensitivity']:.2f} {bar}")

class AlignmentTracker:
    """
    Alignment Variable A_t の実装

    A_{t+1} = (1-alpha)A_t + alpha[lambda_t * 1[D_dot <= 0] + (1-lambda_t) * P_t]
    lambda_t = sigma(beta * (||D_t|| - D_bar) / (D_bar + epsilon))
    """

    def __init__(self, alpha=0.1, beta=5.0, d_bar=0.5, epsilon=1e-3):
        self.alpha = alpha
        self.beta = beta
        self.d_bar = d_bar
        self.epsilon = epsilon
        self.A = 0.5
        self.history = []

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def compute_lambda(self, d_norm):
        return self.sigmoid(
            self.beta * (d_norm - self.d_bar) / (self.d_bar + self.epsilon)
        )

    def update(self, pain_vector, p_value, d_dot):
        d_norm = np.linalg.norm(pain_vector) / np.sqrt(4)
        lam = self.compute_lambda(d_norm)
        stability_signal = 1.0 if d_dot <= 0 else 0.0
        target = lam * stability_signal + (1 - lam) * p_value
        self.A = (1 - self.alpha) * self.A + self.alpha * target
        self.A = np.clip(self.A, 0.0, 1.0)
        self.history.append({
            "A": round(self.A, 4),
            "lambda": round(float(lam), 4),
            "p_value": p_value,
            "d_norm": round(float(d_norm), 4)
        })
        return self.A

