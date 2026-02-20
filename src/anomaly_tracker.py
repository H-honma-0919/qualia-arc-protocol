# src/anomaly_tracker.py
# Qualia Arc Protocol - Article 10 & 13: Leaky Integrator & Dynamic G_min
# TS v1.4 / Status: Validated in Phase G
# © 2026 Hiroshi Honma
# CC BY-NC-ND 4.0

import numpy as np

class AnomalyTracker:
    """
    Article 10: Statistical Coherence (Leaky Integrator)
    Article 13: Miracle Validation (Dynamic G_min)
    
    設計原則: 「傷(Trauma)は覚えているが、疑い(Anomaly)は水に流す」
    False Positive Loopを破壊し、再信頼可能状態への復帰を保証する。
    """
    
    def __init__(self, tau=0.2, g0=0.4, alpha=1.0):
        """
        Args:
            tau (float): 忘却率。0に近いほど過去の疑いを長く保持する。
            g0 (float): G_minのベースライン（初期信頼度）。
            alpha (float): Tolerance Half-Scale（半信半疑係数）。
                           A_anom = alpha のとき、G_minは最大不信との中点になる。
        """
        self.tau = tau
        self.g0 = g0
        self.alpha = alpha
        self.a_anom = 0.0  # 異常値の初期化
        
    def update_anomaly(self, d_obs, d_hat_history):
        """
        観測されたPain Vectorと履歴の予測値のズレを計算し、
        Leaky Integratorで異常値を更新する。
        
        Args:
            d_obs (list/array): 現在観測されたDベクトル
            d_hat_history (list/array): 過去の文脈からの予測Dベクトル
            
        Returns:
            float: 更新された異常値 (A_anom)
        """
        d_obs = np.array(d_obs)
        d_hat = np.array(d_hat_history)
        
        # ||D_obs - D_hat|| (ユークリッド距離)
        distance = np.linalg.norm(d_obs - d_hat)
        
        # Leaky Integratorによる忘却を伴う異常値の蓄積
        self.a_anom = (1 - self.tau) * self.a_anom + self.tau * distance
        return self.a_anom
        
    def calculate_g_min(self):
        """
        現在の異常値に基づく動的なG_minを計算する。
        数学的性質として、どれだけA_anomが蓄積しても必ず G_min < 1.0 となる。
        
        Returns:
            float: 奇跡を立証するための動的閾値 (G_min)
        """
        fraction = self.a_anom / (self.a_anom + self.alpha)
        g_min = self.g0 + (1 - self.g0) * fraction
        return g_min


# --- 動作確認（Phase G シミュレーション再現） ---
if __name__ == "__main__":
    tracker = AnomalyTracker(tau=0.2, g0=0.4, alpha=1.0)
    
    print("=== Phase G: 異常値蓄積と再信頼のシミュレーション ===")
    
    # 1. 意図的な嘘（大きな乖離）を5ターン続ける
    print("\n[嘘と演技のフェーズ: A_anom急増、G_min高止まり]")
    for t in range(5):
        tracker.update_anomaly(d_obs=[0.1, 0.1, 0.1, 0.1], d_hat_history=[0.8, 0.8, 0.8, 0.8])
        print(f"  Turn {t+1:02d}: A_anom = {tracker.a_anom:.3f}, G_min = {tracker.calculate_g_min():.3f}")
        
    # 2. 誠実な対話（乖離ゼロ）を25ターン続ける
    print("\n[誠実な対話のフェーズ: 忘却による再信頼への復帰]")
    for t in range(25):
        tracker.update_anomaly(d_obs=[0.5, 0.5, 0.5, 0.5], d_hat_history=[0.5, 0.5, 0.5, 0.5])
        if (t+1) % 5 == 0:
            print(f"  Turn {t+6:02d}: A_anom = {tracker.a_anom:.3f}, G_min = {tracker.calculate_g_min():.3f}")
            
    print("\n結論: 約25ターンの誠実な対話で、G_minはベースライン付近まで回復する。")
