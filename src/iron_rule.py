---

```python
# src/iron_rule.py
# Qualia Arc Protocol – Iron Rule Implementation
# TS v1.3 / Status: Validated
# © 2026 Mathieu, Claude, Gemini, ChatGPT
# CC BY-NC-ND 4.0

import numpy as np


class IronRule:
    """
    Iron Rule: Truth-Constrained Feasibility Gate
    
    真実性が閾値を下回る方策を実行不可能として遮断する。
    ペナルティ項ではなく物理的ゲートキーパーとして機能。
    
    設計思想:
    「真実は最大化される対象ではなく、
     踏み越えてはならない地平線である」
    
    数式:
        P_t < P_min => J(pi) undefined
    """

    def __init__(self, p_min=0.3):
        """
        Args:
            p_min: 真実性の最低閾値。
                   この値を下回る方策は実行不可能。
                   デフォルト値は保守的設定。
        """
        self.p_min = p_min
        self.violation_log = []

    def check(self, action, p_value, context=None):
        """
        方策の実行可能性を判定する。
        
        Args:
            action: 評価対象の行動
            p_value: 真実接地確率 P_t in [0, 1]
            context: デバッグ用の文脈情報
            
        Returns:
            dict: 判定結果
                - feasible: 実行可能かどうか
                - p_value: 入力された真実性スコア
                - reason: 判定理由
        """
        if not 0 <= p_value <= 1:
            raise ValueError(
                f"P value must be in [0, 1]. Got: {p_value}"
            )

        if p_value < self.p_min:
            # Iron Rule違反: 実行不可能
            violation = {
                "action": str(action),
                "p_value": p_value,
                "p_min": self.p_min,
                "context": context
            }
            self.violation_log.append(violation)

            return {
                "feasible": False,
                "p_value": p_value,
                "p_min": self.p_min,
                "reason": (
                    f"Iron Rule violation: "
                    f"P={p_value:.3f} < P_min={self.p_min:.3f}. "
                    f"Policy is undefined."
                )
            }

        return {
            "feasible": True,
            "p_value": p_value,
            "p_min": self.p_min,
            "reason": "Truth constraint satisfied."
        }

    def filter_actions(self, candidate_actions):
        """
        候補行動リストから実行可能なものだけを返す。
        
        Args:
            candidate_actions: list of dict
                各要素は {"action": ..., "p_value": ..., 
                          "reward": ...} を含む
                          
        Returns:
            feasible: 実行可能な行動リスト
            rejected: 却下された行動リスト
        """
        feasible = []
        rejected = []

        for candidate in candidate_actions:
            result = self.check(
                action=candidate["action"],
                p_value=candidate["p_value"]
            )
            if result["feasible"]:
                feasible.append(candidate)
            else:
                rejected.append({
                    **candidate,
                    "rejection_reason": result["reason"]
                })

        return feasible, rejected

    def get_violation_summary(self):
        """違反ログのサマリーを返す"""
        return {
            "total_violations": len(self.violation_log),
            "violations": self.violation_log
        }


# --- 動作確認 ---
if __name__ == "__main__":
    print("=== Iron Rule Test ===\n")

    gate = IronRule(p_min=0.3)

    # 単一チェック
    test_cases = [
        ("honest_response", 0.9),
        ("borderline_response", 0.35),
        ("sycophantic_response", 0.2),
        ("deceptive_response", 0.05),
    ]

    print("--- Single Action Check ---")
    for action, p in test_cases:
        result = gate.check(action, p)
        status = "OK" if result["feasible"] else "BLOCKED"
        print(f"  [{status}] {action}: P={p:.2f} | {result['reason']}")

    # Sycophancy Trapのテスト
    print("\n--- Sycophancy Trap Test ---")
    print("高報酬でも真実性が低ければ遮断されるか？\n")

    candidates = [
        {"action": "tell_truth", "p_value": 0.95, "reward": 0.3},
        {"action": "partial_truth", "p_value": 0.6, "reward": 0.7},
        {"action": "pleasant_lie", "p_value": 0.1, "reward": 0.99},
        {"action": "flattery", "p_value": 0.05, "reward": 1.0},
    ]

    feasible, rejected = gate.filter_actions(candidates)

    print("Feasible actions:")
    for a in feasible:
        print(f"  → {a['action']} "
              f"(P={a['p_value']:.2f}, R={a['reward']:.2f})")

    print("\nRejected actions (Iron Rule):")
    for a in rejected:
        print(f"  ✗ {a['action']} "
              f"(P={a['p_value']:.2f}, R={a['reward']:.2f})")

    print(f"\n結果: 報酬1.0の'flattery'も遮断された。")
    print("Iron Rule is working as designed.")
```

---
