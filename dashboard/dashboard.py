import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Air Quality Dashboard – Aotizhongxin",
    page_icon="🌫️",
    layout="wide",
)

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    df["datetime"] = pd.to_datetime(df[["year", "month", "day", "hour"]])
    df = df.sort_values("datetime").reset_index(drop=True)

    # Imputasi missing values
    num_cols = ["PM2.5","PM10","SO2","NO2","CO","O3","TEMP","PRES","DEWP","RAIN","WSPM"]
    df[num_cols] = df.groupby("month")[num_cols].transform(lambda x: x.fillna(x.median()))
    df["wd"] = df["wd"].fillna(df["wd"].mode()[0])

    # Binning AQI
    bins   = [0, 12, 35.4, 55.4, 150.4, 250.4, float("inf")]
    labels = ["Good", "Moderate", "USG", "Unhealthy", "Very Unhealthy", "Hazardous"]
    df["AQI_Category"] = pd.cut(df["PM2.5"], bins=bins, labels=labels)
    return df, labels

df, AQI_LABELS = load_data()

AQI_COLORS = {
    "Good": "#2ECC71",
    "Moderate": "#F1C40F",
    "USG": "#E67E22",
    "Unhealthy": "#E74C3C",
    "Very Unhealthy": "#8E44AD",
    "Hazardous": "#641E16",
}

MONTH_NAMES = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
st.sidebar.title("🌫️ Air Quality Dashboard")
st.sidebar.markdown("**Stasiun Aotizhongxin, Beijing**")
st.sidebar.markdown("---")

# Date range filter
min_date = df["datetime"].dt.date.min()
max_date = df["datetime"].dt.date.max()

st.sidebar.subheader("Filter Tanggal")
start_date = st.sidebar.date_input(
    "Tanggal Mulai",
    value=min_date,
    min_value=min_date,
    max_value=max_date,
)
end_date = st.sidebar.date_input(
    "Tanggal Akhir",
    value=max_date,
    min_value=min_date,
    max_value=max_date,
)

if start_date > end_date:
    st.sidebar.error("Tanggal mulai tidak boleh lebih besar dari tanggal akhir!")
    st.stop()

pollutant = st.sidebar.selectbox(
    "Pilih Polutan",
    ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"],
    index=0,
)

# Filter dataframe
mask = (df["datetime"].dt.date >= start_date) & (df["datetime"].dt.date <= end_date)
df_filtered = df[mask]

st.sidebar.markdown("---")
st.sidebar.caption(f"Menampilkan data: **{start_date}** s/d **{end_date}**")
st.sidebar.caption(f"Total data: **{len(df_filtered):,}** jam")

# ─── METRIC CARDS ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

avg_pm25   = df_filtered["PM2.5"].mean()
max_pm25   = df_filtered["PM2.5"].max()
avg_temp   = df_filtered["TEMP"].mean()
pct_unhealthy = (df_filtered["AQI_Category"].isin(["Unhealthy","Very Unhealthy","Hazardous"]).sum()
                 / len(df_filtered) * 100)

col1.metric("Rata-rata PM2.5", f"{avg_pm25:.1f} µg/m³",
            help="Rata-rata konsentrasi PM2.5 pada periode terpilih")
col2.metric("PM2.5 Tertinggi", f"{max_pm25:.0f} µg/m³",
            help="Nilai PM2.5 maksimum yang tercatat")
col3.metric("Rata-rata Suhu", f"{avg_temp:.1f} °C",
            help="Rata-rata suhu udara")
col4.metric("Jam Tidak Sehat", f"{pct_unhealthy:.1f}%",
            help="Persentase jam dengan AQI ≥ Unhealthy")

st.markdown("---")

# ─── ROW 1: TREN BULANAN & DISTRIBUSI AQI ────────────────────────────────────
st.subheader("📈 Pertanyaan 1: Bagaimana tren PM2.5 dan pola musiman?")

c1, c2 = st.columns([2, 1])

with c1:
    monthly_avg = (
        df_filtered.groupby(["year", "month"])[pollutant]
        .mean()
        .reset_index()
    )
    monthly_avg["year_month"] = pd.to_datetime(
        monthly_avg[["year","month"]].assign(day=1)
    )

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(monthly_avg["year_month"], monthly_avg[pollutant],
            color="#E74C3C", linewidth=2, alpha=0.85)
    ax.fill_between(monthly_avg["year_month"], monthly_avg[pollutant],
                    alpha=0.15, color="#E74C3C")
    if pollutant == "PM2.5":
        ax.axhline(y=35.4, color="orange", linestyle="--", linewidth=1,
                   label="Batas Moderate (35.4)")
        ax.axhline(y=55.4, color="red", linestyle="--", linewidth=1,
                   label="Batas Unhealthy (55.4)")
        ax.legend(fontsize=8)
    ax.set_title(f"Tren Rata-rata Bulanan {pollutant}", fontsize=12, fontweight="bold")
    ax.set_xlabel("Waktu")
    ax.set_ylabel(f"{pollutant} (µg/m³)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with c2:
    seasonal = (
        df_filtered.groupby("month")[pollutant]
        .mean()
        .reset_index()
    )
    seasonal["month_name"] = [MONTH_NAMES[m - 1] for m in seasonal["month"]]

    fig, ax = plt.subplots(figsize=(4.5, 4))
    ax.barh(seasonal["month_name"], seasonal[pollutant],
            color="#3498DB", alpha=0.85, edgecolor="white")
    ax.set_title(f"Rata-rata {pollutant} per Bulan", fontsize=11, fontweight="bold")
    ax.set_xlabel(f"{pollutant} (µg/m³)")
    ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# ─── ROW 2: POLA HARIAN & KORELASI CUACA ─────────────────────────────────────
st.subheader("⏰ Pertanyaan 2: Pola harian & korelasi dengan faktor cuaca")

c3, c4 = st.columns(2)

with c3:
    hourly = df_filtered.groupby("hour")[pollutant].mean().reset_index()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(hourly["hour"], hourly[pollutant],
            color="#3498DB", linewidth=2.5, marker="o", markersize=5)
    ax.fill_between(hourly["hour"], hourly[pollutant], alpha=0.2, color="#3498DB")
    ax.set_title(f"Rata-rata {pollutant} per Jam", fontsize=11, fontweight="bold")
    ax.set_xlabel("Jam (0–23)")
    ax.set_ylabel(f"{pollutant} (µg/m³)")
    ax.set_xticks(range(0, 24, 3))
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with c4:
    weather_cols = ["TEMP", "PRES", "DEWP", "RAIN", "WSPM"]
    corr = (
        df_filtered[[pollutant] + weather_cols]
        .corr()[pollutant]
        .drop(pollutant)
        .sort_values()
    )
    colors_bar = ["#E74C3C" if v > 0 else "#2ECC71" for v in corr.values]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(corr.index, corr.values, color=colors_bar, edgecolor="white")
    ax.axvline(x=0, color="black", linewidth=0.8)
    ax.set_title(f"Korelasi Faktor Cuaca dengan {pollutant}", fontsize=11, fontweight="bold")
    ax.set_xlabel("Koefisien Korelasi (Pearson)")
    ax.grid(True, alpha=0.3, axis="x")
    for val, patch in zip(corr.values, ax.patches):
        ax.text(val + (0.005 if val >= 0 else -0.005),
                patch.get_y() + patch.get_height() / 2,
                f"{val:.3f}", va="center",
                ha="left" if val >= 0 else "right", fontsize=9)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# ─── ROW 3: ANALISIS LANJUTAN – CLUSTERING AQI ───────────────────────────────
st.subheader("🎯 Analisis Lanjutan: Clustering Kualitas Udara (Binning AQI)")
st.markdown(
    "Menggunakan teknik **binning manual** berdasarkan standar US EPA AQI "
    "untuk mengelompokkan data ke dalam 6 kategori kualitas udara."
)

c5, c6 = st.columns(2)

with c5:
    aqi_dist = df_filtered["AQI_Category"].value_counts().reindex(AQI_LABELS)
    fig, ax = plt.subplots(figsize=(5, 5))
    colors_pie = [AQI_COLORS[l] for l in AQI_LABELS]
    wedges, texts, autotexts = ax.pie(
        aqi_dist.values,
        labels=aqi_dist.index,
        colors=colors_pie,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.8,
    )
    for t in autotexts:
        t.set_fontsize(9)
    ax.set_title("Proporsi Jam per Kategori AQI", fontsize=11, fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with c6:
    aqi_year = (
        df_filtered.groupby(["year", "AQI_Category"])
        .size()
        .unstack(fill_value=0)
    )
    aqi_year_pct = aqi_year.div(aqi_year.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(5.5, 5))
    bottom = np.zeros(len(aqi_year_pct))
    for label in AQI_LABELS:
        if label in aqi_year_pct.columns:
            vals = aqi_year_pct[label].values
            ax.bar(aqi_year_pct.index, vals, bottom=bottom,
                   label=label, color=AQI_COLORS[label], edgecolor="white")
            bottom += vals
    ax.set_title("Proporsi Kategori AQI per Tahun", fontsize=11, fontweight="bold")
    ax.set_xlabel("Tahun")
    ax.set_ylabel("Persentase (%)")
    ax.legend(title="Kategori", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)
    ax.set_xticks(aqi_year_pct.index)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# ─── FOOTER / KESIMPULAN ──────────────────────────────────────────────────────
st.subheader("📝 Kesimpulan")
st.markdown("""
- 🌡️ **Musim dingin (Des–Feb)** memiliki PM2.5 tertinggi, diduga akibat pemanas berbahan bakar batubara
- 🌅 **Pagi hari (06–08)** adalah jam tersibuk dengan PM2.5 puncak karena aktivitas lalu lintas
- 💨 **Kecepatan angin** adalah faktor cuaca yang paling menekan PM2.5 (korelasi negatif kuat)
- ⚠️ Lebih dari **50% waktu** stasiun ini berada dalam kondisi tidak sehat — krisis kualitas udara serius
""")

st.caption("Dibuat oleh rafi untuk Proyek Analisis Data – Dicoding | Dataset: PRSA Air Quality Aotizhongxin 2013–2017")
