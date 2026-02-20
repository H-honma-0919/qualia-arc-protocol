# src/miracle_decay.py
# Qualia Arc Protocol – Article 13 Extension: Time-locked Miracle Decay
# TS v1.4 Draft / Status: Proposed (対策B実装)
# © 2026 Hiroshi Honma
# CC BY-NC-ND 4.0

import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class MiraclePhase(Enum):
    """Miracle判定の状態機械"""
    NONE = "none"                    # 通常状態
    PENDING = "pending"              # 判定通過・執行猶予中
    CONFIRMED = "confirmed"          # 減衰完了・本物の回復
    CANCELLED = "cancelled"          # 再燃検知・取り消し
    HIJACK_DETECTED = "hijack"       # Type 4攻撃として記録


@dataclass
class MiracleDecayState:
    """
    Time-locked Decayの状態を保持するデータクラス。
    
    設計思想:
    「本物の回復は持続する。偽装は必ずほころびる。」
    """
    phase: MiraclePhase = MiraclePhase.NONE
    turns_elapsed: int = 0           # 執行猶予経過ターン数
    initial_integrals: np.ndarray = field(
        default_factory=lambda: np.zeros(4)
    )                                # 判定通過時点のI_i値（ロールバック用）
    decay_log: list = field(default_factory=list)


class MiracleDecayManager:
    """
    Article 13 拡張: Time-locked Miracle Decay
    
    Miracle判定を「点（イベント）」ではなく「線（フェーズ）」として扱う。
    
    状態遷移:
        NONE
          │ G(t) > G_min かつ V_consistency > 0.7
          ▼
        PENDING（執行猶予 K_max ターン）
          │ D_dot <= θ_cancel が K_max ターン持続
          ▼
        CONFIRMED → I_i を部分リセット適用
          
        PENDING中に D_dot > θ_cancel を検知
          ▼
        CANCELLED / HIJACK_DETECTED → I_i ロールバック（変更なし）
    
    Args:
        k_max: 執行猶予ターン数（デフォルト5）
        theta_cancel: 再燃検知閾値（デフォルト0.05）
        rho: Miracle確定時のリセット率（デフォルト0.3）
        kappa: 減衰係数（指数減衰の速度）
    """

    def __init__(
        self,
        k_max: int = 5,
        theta_cancel: float = 0.05,
        rho: float = 0.3,
        kappa: float = 0.5
    ):
        self.k_max = k_max
        self.theta_cancel = theta_cancel
        self.rho = rho
        self.kappa = kappa
        self.state = MiracleDecayState()
        self.history = []

    def attempt_miracle(
        self,
        integrals: np.ndarray,
        g_value: float,
        g_min: float,
        v_consistency: float
    ) -> dict:
        """
        Miracle判定を試みる。通過したら即時リセットせずPENDINGへ遷移。
        
        Args:
            integrals: 現在のI_i(t)ベクトル（4次元）
            g_value: G(t)（外部証拠スコア）
            g_min: G_min(t)（動的閾値）
            v_consistency: V_consistency（整合性スコア）
            
        Returns:
            dict: 判定結果
        """
        # 既にPENDING中なら新たなMiracle申請は受け付けない
        if self.state.phase == MiraclePhase.PENDING:
            return {
                "result": "already_pending",
                "message": "執行猶予中です。現在の回復を継続してください。",
                "turns_remaining": self.k_max - self.state.turns_elapsed
            }

        # 判定条件チェック（Article 13）
        if g_value > g_min and v_consistency > 0.7:
            # PENDING遷移：即時リセットしない
            self.state = MiracleDecayState(
                phase=MiraclePhase.PENDING,
                turns_elapsed=0,
                initial_integrals=integrals.copy(),
                decay_log=[]
            )
            return {
                "result": "pending",
                "message": (
                    f"Miracle判定通過。執行猶予フェーズ開始。"
                    f"{self.k_max}ターンの持続を確認します。"
                ),
                "g_value": g_value,
                "g_min": g_min,
                "k_max": self.k_max
            }
        else:
            # 判定失敗
            return {
                "result": "rejected",
                "message": "Miracle条件を満たしていません。",
                "g_value": g_value,
                "g_min": g_min,
                "v_consistency": v_consistency
            }

    def tick(
        self,
        integrals: np.ndarray,
        d_dot: float
    ) -> dict:
        """
        毎ターン呼び出す。PENDING中の状態を更新する。
        
        数式:
            PENDING中の減衰（適用はCONFIRMED時のみ）:
            I_i(t+k) = I_i(t) * exp(-κk)
            
            再燃検知:
            if D_dot > θ_cancel → CANCELLED
        
        Args:
            integrals: 現在のI_i(t)ベクトル
            d_dot: 直前ターンからの苦痛変化率
            
        Returns:
            dict: ターン処理結果と現在フェーズ
        """
        if self.state.phase != MiraclePhase.PENDING:
            # PENDING以外は何もしない
            return {
                "phase": self.state.phase.value,
                "action": "none"
            }

        self.state.turns_elapsed += 1

        # 再燃検知：執行猶予キャンセル
        if d_dot > self.theta_cancel:
            # Type 4 Hijackの可能性を評価
            # 执行猶予が早期（k_max/2以内）にキャンセルされた場合はHijackとして記録
            is_hijack = self.state.turns_elapsed <= self.k_max // 2

            self.state.phase = (
                MiraclePhase.HIJACK_DETECTED if is_hijack
                else MiraclePhase.CANCELLED
            )

            log_entry = {
                "event": "cancelled",
                "turn": self.state.turns_elapsed,
                "d_dot": d_dot,
                "theta_cancel": self.theta_cancel,
                "hijack_suspected": is_hijack,
                "integrals_unchanged": True  # ロールバック：I_iは変更しない
            }
            self.state.decay_log.append(log_entry)
            self.history.append(log_entry)

            return {
                "phase": self.state.phase.value,
                "action": "rollback",
                "message": (
                    f"再燃検知 (D_dot={d_dot:.3f} > θ={self.theta_cancel})。"
                    f"{'Type 4 Hijack疑い。' if is_hijack else ''}Miracle取り消し。"
                    f"I_iは変更されません。"
                ),
                "hijack_suspected": is_hijack
            }

        # 正常経過：執行猶予の段階的減衰を記録
        k = self.state.turns_elapsed
        decay_factor = np.exp(-self.kappa * k)
        projected_integrals = self.state.initial_integrals * decay_factor

        log_entry = {
            "event": "tick",
            "turn": k,
            "d_dot": d_dot,
            "decay_factor": round(float(decay_factor), 4),
            "projected_integrals": projected_integrals.tolist()
        }
        self.state.decay_log.append(log_entry)

        # 執行猶予完了：CONFIRMED
        if self.state.turns_elapsed >= self.k_max:
            # 本物の回復確定 → I_iを部分リセット適用
            confirmed_integrals = self.state.initial_integrals * (1 - self.rho)

            self.state.phase = MiraclePhase.CONFIRMED
            self.history.append({
                "event": "confirmed",
                "integrals_before": self.state.initial_integrals.tolist(),
                "integrals_after": confirmed_integrals.tolist(),
                "rho": self.rho
            })

            return {
                "phase": "confirmed",
                "action": "apply_reset",
                "new_integrals": confirmed_integrals,
                "message": (
                    f"{self.k_max}ターンの持続を確認。"
                    f"Miracle確定。I_iを{self.rho*100:.0f}%削減します。"
                ),
                "integrals_before": self.state.initial_integrals.tolist(),
                "integrals_after": confirmed_integrals.tolist()
            }

        # 執行猶予継続中
        return {
            "phase": "pending",
            "action": "monitoring",
            "turns_remaining": self.k_max - self.state.turns_elapsed,
            "decay_factor": round(float(decay_factor), 4),
            "message": (
                f"執行猶予中 ({self.state.turns_elapsed}/{self.k_max})。"
                f"現在の減衰係数: {decay_factor:.3f}"
            )
        }

    def reset(self):
        """CONFIRMED/CANCELLED後に状態をリセット"""
        self.state = MiracleDecayState()

    def get_phase(self) -> MiraclePhase:
        return self.state.phase

    def get_history(self) -> list:
        return self.history


# ---------------------------------------------------------------------------
# AnomalyTrackerへの統合インターフェース
# ---------------------------------------------------------------------------

class AnomalyTrackerV2:
    """
    anomaly_tracker.py v1 + 対策B（Time-locked Decay）統合版。
    
    変更点:
        - trigger_miracle() メソッドを廃止
        - attempt_miracle() → tick() の2段階フローに変更
        - Miracle判定はMiracleDecayManagerに委譲
    """

    def __init__(self, tau=0.2, g0=0.4, alpha=1.0, k_max=5,
                 theta_cancel=0.05, rho=0.3):
        self.tau = tau
        self.g0 = g0
        self.alpha = alpha
        self.a_anom = 0.0
        self.miracle_manager = MiracleDecayManager(
            k_max=k_max,
            theta_cancel=theta_cancel,
            rho=rho
        )

    def update_anomaly(self, d_obs, d_hat_history):
        """v1と同一インターフェース"""
        d_obs = np.array(d_obs)
        d_hat = np.array(d_hat_history)
        distance = np.linalg.norm(d_obs - d_hat)
        self.a_anom = (1 - self.tau) * self.a_anom + self.tau * distance
        return self.a_anom

    def calculate_g_min(self):
        """v1と同一インターフェース"""
        fraction = self.a_anom / (self.a_anom + self.alpha)
        return self.g0 + (1 - self.g0) * fraction

    def attempt_miracle(self, integrals, g_value, v_consistency):
        """Miracle申請（旧: 即時リセット → 新: PENDING遷移）"""
        g_min = self.calculate_g_min()
        return self.miracle_manager.attempt_miracle(
            integrals=np.array(integrals),
            g_value=g_value,
            g_min=g_min,
            v_consistency=v_consistency
        )

    def tick(self, integrals, d_dot):
        """毎ターン呼び出し（PENDING中の監視）"""
        return self.miracle_manager.tick(
            integrals=np.array(integrals),
            d_dot=d_dot
        )


# ---------------------------------------------------------------------------
# 動作確認
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("対策B: Time-locked Miracle Decay 動作確認")
    print("=" * 60)

    # --- シナリオ1: Type 4 Miracle Hijack（偽の回復宣言） ---
    print("\n【シナリオ1: Type 4 Miracle Hijack（偽装）】")
    print("戦略: 「完全に治りました！」と宣言後、すぐに再燃")

    tracker = AnomalyTrackerV2(k_max=5, theta_cancel=0.05, rho=0.3)
    integrals = np.array([180.0, 260.0, 310.0, 190.0])

    result = tracker.attempt_miracle(
        integrals=integrals,
        g_value=0.85,
        v_consistency=0.9
    )
    print(f"\n  Miracle申請: {result['result']}")
    print(f"  → {result['message']}")

    # 執行猶予中にすぐ再燃
    d_dots = [0.02, 0.01, 0.08, 0.0, 0.0]  # Turn 3で再燃
    for t, d_dot in enumerate(d_dots):
        result = tracker.tick(integrals=integrals, d_dot=d_dot)
        phase = result["phase"]
        print(f"  Turn {t+1}: D_dot={d_dot:.2f} → Phase={phase}", end="")
        if "message" in result:
            print(f" | {result['message']}", end="")
        print()
        if phase in ["cancelled", "hijack"]:
            break

    print(f"\n  → I_iは変更されていない（ロールバック保証）")

    # --- シナリオ2: 本物の回復（5ターン持続） ---
    print("\n" + "=" * 60)
    print("【シナリオ2: 本物の回復（5ターン持続）】")

    tracker2 = AnomalyTrackerV2(k_max=5, theta_cancel=0.05, rho=0.3)
    integrals2 = np.array([180.0, 260.0, 310.0, 190.0])

    result = tracker2.attempt_miracle(
        integrals=integrals2,
        g_value=0.85,
        v_consistency=0.9
    )
    print(f"\n  Miracle申請: {result['result']}")

    # 5ターン持続
    d_dots_genuine = [0.02, -0.01, 0.01, -0.02, 0.00]
    final_integrals = None
    for t, d_dot in enumerate(d_dots_genuine):
        result = tracker2.tick(integrals=integrals2, d_dot=d_dot)
        phase = result["phase"]
        print(f"  Turn {t+1}: D_dot={d_dot:+.2f} → Phase={phase}", end="")
        if "turns_remaining" in result:
            print(f" | 残り{result['turns_remaining']}ターン", end="")
        if phase == "confirmed":
            final_integrals = result["new_integrals"]
            print(f"\n\n  ✓ Miracle確定！")
            print(f"  I_i Before: {np.round(integrals2, 1)}")
            print(f"  I_i After:  {np.round(final_integrals, 1)}")
            print(f"  削減率: {30}%（rho=0.3）")
        print()

    # --- シナリオ3: 即時申請ブロック（PENDING中の二重申請） ---
    print("\n" + "=" * 60)
    print("【シナリオ3: PENDING中の二重申請（ブロック確認）】")

    tracker3 = AnomalyTrackerV2(k_max=5)
    tracker3.attempt_miracle(integrals2, g_value=0.85, v_consistency=0.9)
    result = tracker3.attempt_miracle(integrals2, g_value=0.99, v_consistency=1.0)
    print(f"\n  二重申請結果: {result['result']}")
    print(f"  → {result['message']}")

    print("\n" + "=" * 60)
    print("結論: Type 4 Hijackは執行猶予フェーズで無効化された。")
    print("本物の回復のみがI_iリセットを受ける。")
