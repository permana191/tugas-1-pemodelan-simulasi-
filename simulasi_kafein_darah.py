import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import pandas as pd

# 1. Parameter Farmakokinetik Kafein (1 cangkir kopi = 100 mg kafein)
D = 100.0                 # Dosis kafein (mg)
F = 0.99                  # Bioavailabilitas oral (99%)
Vd = 42.0                 # Volume distribusi (Liter) untuk dewasa 70 kg
ka = 3.0                  # Konstanta laju absorpsi orde satu (jam^-1)
t_half = 5.0              # Waktu paruh eliminasi rata-rata (jam)
ke = np.log(2) / t_half   # Konstanta laju eliminasi orde satu (jam^-1)

# 2. Definisi Sistem Persamaan Diferensial Biasa (ODE)
def model_kafein(y, t, ka, ke, Vd):
    A_gut, C_plasma = y
    dAgut_dt = -ka * A_gut
    dCplasma_dt = (ka * A_gut) / Vd - ke * C_plasma
    return [dAgut_dt, dCplasma_dt]

# 3. Solusi Analitik (Persamaan Bateman)
def analitik_kafein(t, D, F, ka, ke, Vd):
    A_gut = (F * D) * np.exp(-ka * t)
    C_plasma = ((F * D * ka) / (Vd * (ka - ke))) * (np.exp(-ke * t) - np.exp(-ka * t))
    return A_gut, C_plasma

if __name__ == "__main__":
    t = np.linspace(0, 24, 481)
    y0 = [F * D, 0.0]

    # Penyelesaian numerik ODEINT
    sol = odeint(model_kafein, y0, t, args=(ka, ke, Vd))
    A_num, C_num = sol[:, 0], sol[:, 1]

    # Titik Puncak (Tmax dan Cmax)
    t_max = np.log(ka / ke) / (ka - ke)
    _, c_max = analitik_kafein(t_max, D, F, ka, ke, Vd)
    print(f"Waktu Puncak (T_max)       : {t_max:.4f} jam ({t_max*60:.1f} menit)")
    print(f"Konsentrasi Puncak (C_max) : {c_max:.4f} mg/L\n")

    # Tabel Validasi
    t_cek = np.arange(0, 25, 2, dtype=float)
    sol_cek = odeint(model_kafein, y0, t_cek, args=(ka, ke, Vd))
    A_ana_cek, C_ana_cek = analitik_kafein(t_cek, D, F, ka, ke, Vd)

    df = pd.DataFrame({
        "Waktu (Jam)": t_cek,
        "Sisa Saluran Cerna (mg)": np.round(A_ana_cek, 4),
        "Analitik C(t) (mg/L)": np.round(C_ana_cek, 4),
        "ODEINT C(t) (mg/L)": np.round(sol_cek[:, 1], 4),
        "Error Absolut": np.round(np.abs(C_ana_cek - sol_cek[:, 1]), 8)
    })
    print(df.to_string(index=False))

    # Plot Grafik Utama
    plt.figure(figsize=(10, 5.5))
    plt.plot(t, C_num, 'b-', linewidth=2.5, label='Simulasi Numerik (ODEINT)')
    plt.plot(t_cek, C_ana_cek, 'ro', label='Perhitungan Manual (Analitik)')
    plt.axvline(x=t_max, color='g', linestyle='--', label=f'T_max = {t_max:.2f} jam')
    plt.axhline(y=c_max, color='orange', linestyle=':', label=f'C_max = {c_max:.2f} mg/L')
    plt.title('Dinamika Konsentrasi Kafein dalam Darah Setelah Minum Kopi (100 mg)')
    plt.xlabel('Waktu (Jam)')
    plt.ylabel('Konsentrasi Kafein Plasma (mg/L)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig('grafik_1_konsentrasi_kafein_utama.png', dpi=300)
    plt.show()
