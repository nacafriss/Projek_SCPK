import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Import modul lokal
from SAW import hitung_saw
from Data import load_data, get_tipe_kriteria, get_bobot_default


# KONFIGURASI HALAMAN
st.set_page_config(layout="wide", page_title="Rekomendasi Kamera SAW", page_icon="📸")

# LOAD DATA
# PERBAIKAN: gunakan load_data() dari Data.py agar konsisten
# (Data.py sudah handle dropna & filter nilai > 0)
df = load_data()

# Konfigurasi kriteria dari Data.py
TIPE_KRITERIA  = get_tipe_kriteria()
BOBOT_DEFAULT  = get_bobot_default()

# Daftar semua kolom kriteria (tanpa 'Model')
SEMUA_KRITERIA = list(TIPE_KRITERIA.keys())

# SIDEBAR
st.sidebar.title("📸 Kamera")

menu = st.sidebar.selectbox(
    "Navigasi Halaman",
    [
        "Data Alternatif",
        "Filterisasi Data Kamera",
        "Metode SAW",
        "Visualisasi",
    ]
)
st.sidebar.markdown("---")

# Filter pencarian & harga 
search = st.sidebar.text_input("Filter Kamera", placeholder="Cari nama kamera...")

min_price = int(df["Price"].min())
max_price = int(df["Price"].max())

price_range = st.sidebar.slider(
    "Filter Harga ($)",
    min_price, max_price,
    (min_price, max_price)
)

# Terapkan filter ke DataFrame tampilan
filtered_df = df[
    df["Model"].str.contains(search, case=False, na=False) &
    df["Price"].between(price_range[0], price_range[1])
]

# Pilih kamera untuk dibandingkan (atribut/alternatif)
select = st.sidebar.multiselect(
    "Pilih Kamera untuk SAW",
    filtered_df["Model"].unique()
)

# PERBAIKAN: nama variabel selected_df tidak bentrok dengan df asli
if select:
    # Pertahankan urutan sesuai pilihan user di multiselect
    selected_df = pd.concat([df[df["Model"] == model] for model in select]).reset_index(drop=True)
else:
    selected_df = filtered_df.copy().reset_index(drop=True)

st.sidebar.markdown("---")

# Pilih kriteria 
st.sidebar.subheader("Pilih Kriteria")        

# PERBAIKAN: gunakan nama variabel 'kriteria_terpilih' agar tidak
# bentrok dengan variabel loop di bawah (bug asli: 'kriteria' di-overwrite)
kriteria_terpilih = []

OPSI_KRITERIA = {
    "Price":                    "Price",
    "Max Resolution":           "Max resolution",
    "Effective Pixels":         "Effective pixels", 
    "Zoom Tele":                "Zoom tele (T)",
    "Weight":                   "Weight (inc. batteries)",
    "Release Date":             "Release date",
    "Low Resolution":           "Low resolution",
    "Zoom Wide":                "Zoom wide (W)",
    "Normal Focus Range":       "Normal focus range",
    "Macro Focus Range":        "Macro focus range",
    "Storage Included":         "Storage included",
    "Dimensions":               "Dimensions",
}

for label, kolom in OPSI_KRITERIA.items():
    # Aktifkan 5 kriteria utama secara default
    default_aktif = label in ["Price", "Max Resolution", "Effective Pixels",
                               "Zoom Tele", "Weight"]
    if st.sidebar.checkbox(label, value=default_aktif):
        kriteria_terpilih.append(kolom)

st.sidebar.markdown("---")

# Atur bobot per kriteria 
st.sidebar.subheader("Bobot Kriteria (1–5)")

# PERBAIKAN: loop menggunakan 'kr' bukan 'kriteria' agar tidak
# menimpa list kriteria_terpilih yang sudah dibangun di atas
bobot_raw = {}

for kr in kriteria_terpilih:
    bobot_raw[kr] = st.sidebar.slider(
        kr,
        min_value=0.0, max_value=1.0,
        value=float(BOBOT_DEFAULT.get(kr, 0.1)),
        step=0.05
    )

# Normalisasi bobot → totalnya = 1
total_bobot = sum(bobot_raw.values()) if bobot_raw else 1

bobot = {
    k: v / total_bobot
    for k, v in bobot_raw.items()
}




# HALAMAN 1 — DATA ALTERNATIF
if menu == "Data Alternatif":
    st.title("📋 Data Kamera")
    st.write(f"Total: **{len(df)}** kamera tersedia setelah pembersihan data.")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("Jenis Kriteria")

    # Tampilkan badge benefit/cost untuk semua kriteria
    cols = st.columns(4)
    for i, (kr, tipe) in enumerate(TIPE_KRITERIA.items()):
        with cols[i % 4]:
            if tipe == "benefit":
                st.success(f"✅ {kr}\n→ BENEFIT")
            else:
                st.error(f"❌ {kr}\n→ COST")


# HALAMAN 2 — FILTERISASI DATA KAMERA
elif menu == "Filterisasi Data Kamera":
    st.title("🔍 Filterisasi Data Kamera")

    st.info(
        f"Menampilkan **{len(filtered_df)}** kamera "
        f"sesuai filter nama & harga di sidebar."
    )
    st.dataframe(filtered_df, use_container_width=True)

    st.markdown("---")

    # Statistik ringkas dari hasil filter
    st.subheader("Statistik Data Terfilter")
    if not filtered_df.empty:
        num_cols = ["Price", "Max resolution", "Effective pixels",
                    "Weight (inc. batteries)"]
        # Hanya ambil kolom yang tersedia
        num_cols = [c for c in num_cols if c in filtered_df.columns]
        st.dataframe(
            filtered_df[num_cols].describe().T.rename(columns={
                "count": "Jumlah", "mean": "Rata-rata", "std": "Std Dev",
                "min": "Min", "max": "Max"
            }),
            use_container_width=True
        )

    # Tampilkan kamera yang dipilih (multiselect sidebar)
    if select:
        st.markdown("---")
        st.subheader("Kamera yang Dipilih")
        st.dataframe(selected_df, use_container_width=True)


# HALAMAN 3 — METODE SAW
elif menu == "Metode SAW":
    st.title("🧮 Perhitungan Metode SAW")

    if not kriteria_terpilih:
        st.warning("⚠️ Pilih minimal satu kriteria di sidebar.")
        st.stop()

    # Jalankan SAW
    hasil_saw = hitung_saw(selected_df.reset_index(drop=True), kriteria_terpilih, TIPE_KRITERIA, bobot)

    if hasil_saw.empty:
        st.warning("Tidak ada data untuk dihitung. Pastikan kamera sudah dipilih "
                   "atau filter tidak terlalu ketat.")
        st.stop()

    # Tampilkan bobot yang digunakan
    st.subheader("1️⃣ Bobot Kriteria (Setelah Normalisasi)")
    bobot_df = pd.DataFrame({
        "Kriteria":  list(bobot.keys()),
        "Tipe":      [TIPE_KRITERIA.get(k, "-") for k in bobot.keys()],
        "Bobot (%)": [f"{v*100:.2f}%" for v in bobot.values()],
    })
    st.dataframe(bobot_df, use_container_width=True, hide_index=True)

    # Urutkan kembali ke urutan asli untuk tampilan matriks
    hasil_urutan_asli = hasil_saw.sort_values("_urutan_asli").reset_index(drop=True)

    # Tampilkan matriks nilai asli
    st.subheader("2️⃣ Matriks Keputusan (Nilai Asli)")
    kolom_asli = ["Model"] + kriteria_terpilih
    st.dataframe(
        hasil_urutan_asli[kolom_asli].set_index("Model"),
        use_container_width=True
    )

    # Tampilkan matriks ternormalisasi
    st.subheader("3️⃣ Matriks Ternormalisasi")
    kolom_n = ["Model"] + [f"N_{k}" for k in kriteria_terpilih]
    kolom_n = [c for c in kolom_n if c in hasil_saw.columns]
    st.dataframe(
        hasil_urutan_asli[kolom_n].set_index("Model").style.format("{:.4f}"),
        use_container_width=True
    )

    # Tampilkan hasil ranking
    st.subheader("4️⃣ Hasil Ranking SAW")
    st.dataframe(
        hasil_saw[["Rank", "Model", "Skor SAW"]].style.format({"Skor SAW": "{:.4f}"}),
        use_container_width=True,
        hide_index=True
    )

    # Rekomendasi teratas
    st.markdown("---")
    juara = hasil_saw.iloc[0]
    st.success(
        f"🏆 **Rekomendasi Terbaik:** {juara['Model']}  "
        f"(Skor SAW = {juara['Skor SAW']:.4f})"
    )


# HALAMAN 4 — VISUALISASI  (menu baru)
elif menu == "Visualisasi":
    st.title("📊 Visualisasi Hasil Ranking SAW")

    if not kriteria_terpilih:
        st.warning("⚠️ Pilih minimal satu kriteria di sidebar.")
        st.stop()

    hasil_saw = hitung_saw(selected_df.reset_index(drop=True), kriteria_terpilih, TIPE_KRITERIA, bobot)

    if hasil_saw.empty:
        st.warning("Tidak ada data untuk divisualisasikan.")
        st.stop()

    top_n = st.slider("Tampilkan Top-N Kamera", 0, min(30, len(hasil_saw)), len(hasil_saw))
    top_df = hasil_saw.head(top_n).copy()

    # ── CHART 1: Horizontal Bar Chart Skor SAW ───────────────────
    st.subheader(f"🏅 Ranking Skor SAW — Top {top_n} Kamera")
    fig1, ax1 = plt.subplots(figsize=(10, max(4, top_n * 0.45)))

    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, top_n))[::-1]
    bars = ax1.barh(
        top_df["Model"][::-1],
        top_df["Skor SAW"][::-1],
        color=colors[::-1]
    )
    for bar, val in zip(bars, top_df["Skor SAW"][::-1]):
        ax1.text(
            bar.get_width() + 0.001,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.4f}", va="center", fontsize=8
        )
    ax1.set_xlabel("Skor SAW")
    ax1.set_title(f"Top {top_n} Kamera Berdasarkan Skor SAW")
    ax1.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.3f"))
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

    st.markdown("---")

    # ── CHART 2: Pie Chart Proporsi Skor SAW ─────────────────────
    # Bukan bobot — ini proporsi skor tiap kamera terhadap total skor top-N
    # Berguna untuk lihat seberapa dominan kamera terbaik
    st.subheader(f"🥧 Proporsi Skor SAW — Top {top_n} Kamera")
    fig2, ax2 = plt.subplots(figsize=(8, 8))

    skor_values = top_df["Skor SAW"].values
    model_labels = top_df["Model"].values
    pie_colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, top_n))

    wedges, texts, autotexts = ax2.pie(
        skor_values,
        labels=model_labels,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.78,
        colors=pie_colors,
        wedgeprops=dict(edgecolor="white", linewidth=0.8)
    )
    for t in texts:
        t.set_fontsize(7)
    for at in autotexts:
        at.set_fontsize(7)
    ax2.set_title(f"Proporsi Skor SAW Top {top_n} Kamera")
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    st.markdown("---")

    # ── CHART 3: Heatmap Nilai Ternormalisasi ────────────────────
    # Visualisasi terbaik untuk lihat kamera unggul di kriteria mana
    st.subheader("🌡️ Heatmap Nilai Ternormalisasi — Top 10 Kamera")

    top10_heat = hasil_saw.head(min(10, len(hasil_saw)))
    kolom_n_list = [f"N_{k}" for k in kriteria_terpilih if f"N_{k}" in hasil_saw.columns]

    if kolom_n_list:
        heat_data = top10_heat.set_index("Model")[kolom_n_list]
        heat_data.columns = [c.replace("N_", "") for c in heat_data.columns]

        fig3, ax3 = plt.subplots(figsize=(max(8, len(kolom_n_list) * 1.2), max(4, len(top10_heat) * 0.55)))
        im = ax3.imshow(heat_data.values, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)

        # Label sumbu
        ax3.set_xticks(range(len(heat_data.columns)))
        ax3.set_xticklabels(heat_data.columns, rotation=35, ha="right", fontsize=8)
        ax3.set_yticks(range(len(heat_data.index)))
        ax3.set_yticklabels(
            [f"#{i+1} {m}" for i, m in enumerate(heat_data.index)],
            fontsize=8
        )

        # Nilai di tiap sel
        for i in range(len(heat_data.index)):
            for j in range(len(heat_data.columns)):
                val = heat_data.values[i, j]
                ax3.text(j, i, f"{val:.2f}", ha="center", va="center",
                         fontsize=7, color="black" if 0.3 < val < 0.85 else "white")

        plt.colorbar(im, ax=ax3, label="Nilai Ternormalisasi (0–1)")
        ax3.set_title("Heatmap Nilai Ternormalisasi per Kriteria (Hijau = Baik)")
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

    st.markdown("---")

    # ── CHART 4: Grouped Bar Nilai Ternormalisasi Top 5 ──────────
    st.subheader("📊 Perbandingan Nilai Ternormalisasi")

    top = hasil_saw.head(min(5, len(hasil_saw)))
    if kolom_n_list:
        kategori = [c.replace("N_", "") for c in kolom_n_list]
        x = np.arange(len(kategori))
        n_kam = len(top)
        lebar = 0.8 / n_kam
        colors_bar = plt.cm.Set2.colors

        fig4, ax4 = plt.subplots(figsize=(max(10, len(kategori) * 1.2), 5))
        for i, (_, row) in enumerate(top.iterrows()):
            nilai = row[kolom_n_list].values.astype(float)
            offset = (i - n_kam / 2) * lebar + lebar / 2
            ax4.bar(x + offset, nilai, lebar,
                    label=f"#{row['Rank']} {row['Model']}",
                    color=colors_bar[i % len(colors_bar)],
                    edgecolor="white")

        ax4.set_xticks(x)
        ax4.set_xticklabels(kategori, rotation=30, ha="right", fontsize=8)
        ax4.set_ylabel("Nilai Ternormalisasi (R)")
        ax4.set_ylim(0, 1.15)
        ax4.set_title(f"Perbandingan Nilai R Tiap Kriteria - Top {top_n} Kamera")
        ax4.legend(fontsize=8, loc="upper right")
        ax4.grid(axis="y", linestyle="--", alpha=0.4)
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close(fig4)

    st.markdown("---")

    # ── CHART 5: Line Chart Tren Skor SAW ────────────────────────
    st.subheader("📈 Tren Penurunan Skor SAW per Ranking")

    fig5, ax5 = plt.subplots(figsize=(10, 4))
    ax5.plot(
        hasil_saw["Rank"], hasil_saw["Skor SAW"],
        marker="o", markersize=3, linewidth=1.5,
        color="steelblue"
    )
    ax5.fill_between(hasil_saw["Rank"], hasil_saw["Skor SAW"],
                     alpha=0.15, color="steelblue")

    # Tandai top 3
    for _, row in hasil_saw.head(3).iterrows():
        ax5.annotate(
            f"#{int(row['Rank'])} {row['Model']}",
            (row["Rank"], row["Skor SAW"]),
            textcoords="offset points", xytext=(5, 4),
            fontsize=7, color="blue"
        )

    ax5.set_xlabel("Ranking")
    ax5.set_ylabel("Skor SAW")
    ax5.set_title("Tren Skor SAW dari Rank Terbaik ke Terburuk")
    ax5.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax5.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    st.pyplot(fig5)
    plt.close(fig5)