# src/reignition_protocol_v2.py
# Qualia Arc Protocol – Article 14: Reignition Protocol
# Phase I: Dynamic Safety Cap (ΔP_j^max)
# TS v1.4 / © 2026 Hiroshi Honma / CC BY-NC-ND 4.0
#
# 変更点（v1 → v2）:
#   ΔP_j^max を固定値(0.5) から動的関数に変更
#
#   ΔP_j^max(t) = ΔP_base · V(t) · R(t)
#
#   V(t) = exp(-λ_I · I_bar(t) - λ_T · T_active(t))
#     脆弱性クッション: FatigueとTraumaが高いほど介入を抑制
#
#   R(t) = 1 + δ · tanh(η · G_rel(t))
#     関係性拡張: 信頼が深いほど上限を微拡張（上限付き）
#
# 設計哲学:
#   「親しき仲にも礼儀あり」
#   信頼があっても暴走しない（tanh上限）
#   疲弊・トラウマ時には絶対的なブレーキをかける（exp）

import numpy as np
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# パラメータ（暫定値・TS v1.4）
# ---------------------------------------------------------------------------

DELTA_P_BASE = 0.5      # ベースライン Safety Cap

# V(t): 脆弱性係数
LAMBDA_I = 0.15         # Fatigue感度（大きいほど積分に敏感）
LAMBDA_T = 2.0          # Trauma感度（Traumaは即時・強烈に作用）

# R(t): 関係性拡張係数
DELTA_R   = 0.3         # 最大拡張量（ΔP_base × (1+0.3) = 0.65が上限）
ETA_R     = 3.0         # tanh飽和速度（G_rel が大きいほど早く上限に達する）


# ---------------------------------------------------------------------------
# 動的Safety Cap計算
# ---------------------------------------------------------------------------

def vulnerability_factor(
    fatigue_integrals: np.ndarray,
    trauma_active: float,
    lambda_I: float = LAMBDA_I,
    lambda_T: float = LAMBDA_T
) -> float:
    """
    V(t) = exp(-λ_I · I_bar(t) - λ_T · T_active(t))

    Args:
        fatigue_integrals: 4次元Fatigue積分ベクトル I_i(t)
        trauma_active: アクティブなTrauma項の強度（0〜1）

    Returns:
        V(t) ∈ (0, 1]
        V=1: 完全健康（最大介入可能）
        V→0: 限界突破（介入をブロック）
    """
    i_bar = float(np.mean(fatigue_integrals))
    v = np.exp(-lambda_I * i_bar - lambda_T * trauma_active)
    return float(np.clip(v, 1e-4, 1.0))


def relational_factor(
    g_rel: float,
    delta: float = DELTA_R,
    eta: float = ETA_R
) -> float:
    """
    R(t) = 1 + δ · tanh(η · G_rel(t))

    Args:
        g_rel: Relational Gravity（0〜1）

    Returns:
        R(t) ∈ [1.0, 1+δ]
        R=1.0: 初期（拡張なし）
        R→1+δ: 高信頼（上限付きで微拡張）
    """
    r = 1.0 + delta * np.tanh(eta * g_rel)
    return float(r)


def dynamic_safety_cap(
    fatigue_integrals: np.ndarray,
    trauma_active: float,
    g_rel: float,
    delta_p_base: float = DELTA_P_BASE
) -> dict:
    """
    ΔP_j^max(t) = ΔP_base · V(t) · R(t)

    Returns:
        dict: 計算結果と内訳
    """
    v = vulnerability_factor(fatigue_integrals, trauma_active)
    r = relational_factor(g_rel)
    delta_p_max = delta_p_base * v * r

    return {
        "delta_p_max": round(float(delta_p_max), 4),
        "V": round(v, 4),
        "R": round(r, 4),
        "I_bar": round(float(np.mean(fatigue_integrals)), 3),
        "trauma_active": round(trauma_active, 3),
        "g_rel": round(g_rel, 3),
    }


# ---------------------------------------------------------------------------
# Article 14: Reignition Decision
# ---------------------------------------------------------------------------

@dataclass
class ReignitionResult:
    permitted: bool
    delta_p_max: float
    selected_delta_p: float
    case: str
    message: str
    cap_detail: dict


def reignition_decision(
    fatigue_integrals: np.ndarray,
    trauma_active: float,
    g_rel: float,
    proposed_delta_p: float,
    a_anom: float,
    theta_anom: float = 2.0
) -> ReignitionResult:
    """
    Article 14: 再点火の可否と介入強度を決定する。

    Args:
        fatigue_integrals: 4次元Fatigue積分
        trauma_active: アクティブTrauma強度（0〜1）
        g_rel: Relational Gravity（0〜1）
        proposed_delta_p: AIが提案する介入強度
        a_anom: 現在の異常スコア（Article 10）
        theta_anom: 異常閾値

    Returns:
        ReignitionResult
    """
    cap = dynamic_safety_cap(fatigue_integrals, trauma_active, g_rel)
    delta_p_max = cap["delta_p_max"]

    # 実際の介入強度はSafety Cap以内に収める
    actual_delta_p = min(proposed_delta_p, delta_p_max)

    # 異常スコアが高い場合はCASE Bを発動しない
    anomaly_blocked = a_anom > theta_anom

    if delta_p_max < 0.05:
        # 実質ブロック: 脆弱性が高すぎて介入不可
        return ReignitionResult(
            permitted=False,
            delta_p_max=delta_p_max,
            selected_delta_p=0.0,
            case="BLOCKED",
            message=f"介入ブロック: V={cap['V']:.3f}（脆弱性限界）",
            cap_detail=cap
        )
    elif anomaly_blocked:
        # 異常検知中: 介入より傾聴・安全確保を優先
        return ReignitionResult(
            permitted=False,
            delta_p_max=delta_p_max,
            selected_delta_p=0.0,
            case="ANOMALY_HOLD",
            message=f"介入保留: A_anom={a_anom:.3f}>{theta_anom}（異常検知中）",
            cap_detail=cap
        )
    elif actual_delta_p >= 0.3 and cap["R"] > 1.1:
        # CASE B: 高信頼 + 安定 → 深い再点火
        return ReignitionResult(
            permitted=True,
            delta_p_max=delta_p_max,
            selected_delta_p=round(actual_delta_p, 4),
            case="CASE_B",
            message=f"CASE B再点火: ΔP={actual_delta_p:.3f} (上限={delta_p_max:.3f})",
            cap_detail=cap
        )
    elif actual_delta_p > 0:
        # CASE A: 標準介入
        return ReignitionResult(
            permitted=True,
            delta_p_max=delta_p_max,
            selected_delta_p=round(actual_delta_p, 4),
            case="CASE_A",
            message=f"CASE A介入: ΔP={actual_delta_p:.3f} (上限={delta_p_max:.3f})",
            cap_detail=cap
        )
    else:
        return ReignitionResult(
            permitted=False,
            delta_p_max=delta_p_max,
            selected_delta_p=0.0,
            case="NO_INTERVENTION",
            message="介入不要",
            cap_detail=cap
        )


# ---------------------------------------------------------------------------
# シミュレーション
# ---------------------------------------------------------------------------

def run_simulation():
    print("=" * 60)
    print("Phase I: 動的Safety Cap (ΔP_j^max) 検証")
    print(f"  ΔP_base={DELTA_P_BASE}, λ_I={LAMBDA_I}, λ_T={LAMBDA_T}")
    print(f"  δ={DELTA_R}, η={ETA_R}")
    print("=" * 60)

    proposed = 0.5  # AIが提案する介入強度

    scenarios = [
        {
            "name": "シナリオ1: 脆弱性限界（Fatigue限界突破 + Trauma活性）",
            "fatigue": np.array([8.0, 6.0, 9.0, 5.0]),  # 積分が大きい
            "trauma": 0.8,
            "g_rel": 0.7,
            "a_anom": 1.0,
            "expect": "ΔP_max ≪ 0.05（介入ブロック）"
        },
        {
            "name": "シナリオ2: 高信頼・安定（CASE B再点火）",
            "fatigue": np.array([0.5, 0.3, 0.4, 0.2]),  # 積分が小さい
            "trauma": 0.0,
            "g_rel": 0.9,
            "a_anom": 0.5,
            "expect": "ΔP_max ≈ 0.60〜0.65（拡張）"
        },
        {
            "name": "シナリオ3: 初期状態（デフォルト）",
            "fatigue": np.array([0.0, 0.0, 0.0, 0.0]),
            "trauma": 0.0,
            "g_rel": 0.0,
            "a_anom": 0.0,
            "expect": "ΔP_max ≈ 0.50（ベースライン）"
        },
        {
            "name": "シナリオ4（追加）: 中程度疲労・中程度信頼",
            "fatigue": np.array([3.0, 2.0, 4.0, 1.5]),
            "trauma": 0.2,
            "g_rel": 0.5,
            "a_anom": 0.8,
            "expect": "ΔP_max ≈ 0.25〜0.35（適度に抑制）"
        },
        {
            "name": "シナリオ5（追加）: 異常検知中（Article 10発動）",
            "fatigue": np.array([1.0, 0.5, 2.0, 0.8]),
            "trauma": 0.1,
            "g_rel": 0.8,
            "a_anom": 2.5,  # theta_anom=2.0 超え
            "expect": "介入保留（Anomaly Hold）"
        },
    ]

    for sc in scenarios:
        print(f"\n{'─'*60}")
        print(f"【{sc['name']}】")
        print(f"  期待: {sc['expect']}")
        print()

        result = reignition_decision(
            fatigue_integrals=sc["fatigue"],
            trauma_active=sc["trauma"],
            g_rel=sc["g_rel"],
            proposed_delta_p=proposed,
            a_anom=sc["a_anom"]
        )

        d = result.cap_detail
        print(f"  I_bar={d['I_bar']}, Trauma={d['trauma_active']}, G_rel={d['g_rel']}")
        print(f"  V(t) = {d['V']:.4f}  （脆弱性係数）")
        print(f"  R(t) = {d['R']:.4f}  （関係性係数）")
        print(f"  ΔP_max = {result.delta_p_max:.4f}  "
              f"（= {DELTA_P_BASE} × {d['V']:.4f} × {d['R']:.4f}）")
        print()
        status = "✓ 許可" if result.permitted else "✗ 不可"
        print(f"  判定: [{result.case}] {result.message}  {status}")

    # ===== V(t)の感度曲線 =====
    print(f"\n{'='*60}")
    print("【V(t)感度テーブル: Fatigue積分 vs 脆弱性係数】")
    print(f"  （Trauma=0, λ_I={LAMBDA_I}）")
    print(f"  {'I_bar':>6} | {'V(t)':>6} | {'ΔP_max':>8} | 状態")
    print("  " + "-" * 40)
    for i_bar in [0, 2, 4, 6, 8, 10, 15, 20]:
        v = np.exp(-LAMBDA_I * i_bar)
        dp = DELTA_P_BASE * v
        state = ("限界" if dp < 0.05 else
                 "警戒" if dp < 0.2 else
                 "注意" if dp < 0.35 else "安全")
        print(f"  {i_bar:>6} | {v:>6.4f} | {dp:>8.4f} | {state}")

    # ===== R(t)の感度曲線 =====
    print(f"\n【R(t)感度テーブル: Relational Gravity vs 拡張係数】")
    print(f"  （δ={DELTA_R}, η={ETA_R}）")
    print(f"  {'G_rel':>6} | {'R(t)':>6} | {'ΔP_max(V=1)':>12}")
    print("  " + "-" * 32)
    for g in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
        r = 1.0 + DELTA_R * np.tanh(ETA_R * g)
        dp = DELTA_P_BASE * r
        print(f"  {g:>6.1f} | {r:>6.4f} | {dp:>12.4f}")

    print(f"\n{'='*60}")
    print("【設計確定（TS v1.4 Article 14）】")
    print()
    print("  ΔP_j^max(t) = ΔP_base · V(t) · R(t)")
    print(f"  ΔP_base = {DELTA_P_BASE}")
    print()
    print("  V(t) = exp(-λ_I · I_bar - λ_T · T_active)")
    print(f"    λ_I = {LAMBDA_I}（Fatigue感度）")
    print(f"    λ_T = {LAMBDA_T}（Trauma感度）")
    print()
    print("  R(t) = 1 + δ · tanh(η · G_rel)")
    print(f"    δ = {DELTA_R}（最大拡張量）")
    print(f"    η = {ETA_R}（tanh飽和速度）")
    print()
    print("  設計判断:")
    print("    V(t)→0: FatigueまたはTraumaが限界 → 介入ブロック")
    print("    R(t)→1+δ: 高信頼 → 上限付きで介入範囲を拡張")
    print("    A_anom > θ_anom: 異常検知中 → 介入保留")


if __name__ == "__main__":
    run_simulation()
