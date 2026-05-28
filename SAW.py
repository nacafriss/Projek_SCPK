import pandas as pd
import numpy as np


def hitung_saw(df, kolom_kriteria, tipe_kriteria, bobot):
    if not kolom_kriteria:
        return pd.DataFrame()

    # Reset index agar urutan mengikuti df masuk, bukan index CSV
    df = df.reset_index(drop=True)

    # ── 1. Matriks x (seperti notebook sel 2.1) ──
    x = df[kolom_kriteria].values.astype(float)

    # ── 2. Atribut k: 1=benefit, 0=cost (seperti notebook sel 2.2) ──
    k = np.array([1 if tipe_kriteria.get(c) == "benefit" else 0
                  for c in kolom_kriteria])

    # ── 3. Bobot w, dinormalisasi agar total = 1 (seperti notebook sel 2.3) ──
    w = np.array([bobot.get(c, 0.0) for c in kolom_kriteria])
    w = w / w.sum() if w.sum() != 0 else w

    # ── 4. Normalisasi → matriks R (seperti notebook sel 3.1) ──
    m, n = x.shape
    R = np.zeros((m, n))
    for j in range(n):
        if k[j] == 1:                                        # benefit
            R[:, j] = x[:, j] / np.max(x[:, j]) if np.max(x[:, j]) != 0 else 0
        else:                                                # cost
            R[:, j] = np.where(x[:, j] != 0, np.min(x[:, j]) / x[:, j], 0)

    # ── 5. Hitung V (seperti notebook sel 3.2) ──
    V = np.sum(w * R, axis=1)

    # ── 6. Susun hasil & ranking ──
    hasil = df[["Model"] + kolom_kriteria].copy()

    for i, col in enumerate(kolom_kriteria):
        hasil[f"N_{col}"] = R[:, i]

    hasil["Skor SAW"] = V

    # Simpan urutan asli sebelum sort
    hasil["_urutan_asli"] = range(len(hasil))

    hasil = hasil.sort_values("Skor SAW", ascending=False).reset_index(drop=True)
    hasil.insert(0, "Rank", range(1, len(hasil) + 1))

    return hasil



if __name__ == "__main__":
    from Data import load_data, get_tipe_kriteria, get_bobot_default

    df      = load_data()
    kriteria = ["Max resolution", "Effective pixels", "Zoom tele (T)",
                "Weight (inc. batteries)", "Price"]
    tipe    = get_tipe_kriteria()
    bobot   = get_bobot_default()

    hasil = hitung_saw(df, kriteria, tipe, bobot)

    print("=== Nilai V (Skor SAW) ===")
    print(hasil[["Rank", "Model", "Skor SAW"]].head(10).to_string(index=False))

    best = hasil.iloc[0]
    print(f"\nAlternatif terbaik adalah {best['Model']} dengan nilai {best['Skor SAW']:.4f}")