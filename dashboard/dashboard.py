import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date

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

    num_cols = ["PM2.5","PM10","SO2","NO2","CO","O3","TEMP","PRES","DEWP","RAIN","WSPM"]
    df[num_cols] = df.groupby("month")[num_cols].transform(lambda x: x.fillna(x.median()))
    df["wd"] = df["wd"].fillna(df["wd"].mode()[0])

    bins   = [0, 12, 35.4, 55.4, 150.4, 250.4, float("inf")]
    labels = ["Good", "Moderate", "USG", "Unhealthy", "Very Unhealthy", "Hazardous"]
    df["AQI_Category"] = pd.cut(df["PM2.5"], bins=bins, labels=labels)
    return df, labels

df, AQI_LABELS = load_data()

AQI_COLORS = {
    "Good": "#2ECC71", "Moderate": "#F1C40F", "USG": "#E67E22",
    "Unhealthy": "#E74C3C", "Very Unhealthy": "#8E44AD", "Hazardous": "#641E16",
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

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.title("🌫️ Dashboard Kualitas Udara – Aotizhongxin, Beijing")
st.markdown("**Dataset:** PRSA Air Quality Dataset | **Periode:** 1 Mar 2013 – 28 Feb 2017")
st.markdown("---")

# ─── METRIC CARDS ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
avg_pm25      = df_filtered["PM2.5"].mean()
max_pm25      = df_filtered["PM2.5"].max()
avg_wspm      = df_filtered["WSPM"].mean()
pct_unhealthy = (df_filtered["AQI_Category"].isin(
    ["Unhealthy","Very Unhealthy","Hazardous"]).sum() / len(df_filtered) * 100)

col1.metric("Rata-rata PM2.5",    f"{avg_pm25:.1f} µg/m³")
col2.metric("PM2.5 Tertinggi",    f"{max_pm25:.0f} µg/m³")
col3.metric("Rata-rata Kec. Angin", f"{avg_wspm:.2f} m/s")
col4.metric("Jam Tidak Sehat",    f"{pct_unhealthy:.1f}%")

st.markdown("---")

# ─── PERTANYAAN 1 ─────────────────────────────────────────────────────────────
st.subheader("📊 Pertanyaan 1")
st.markdown(
    "_Pada bulan apa rata-rata konsentrasi PM2.5 paling tinggi dan paling rendah "
    "di stasiun Aotizhongxin selama periode 2013–2017, serta bagaimana tren "
    "perubahannya dari tahun ke tahun?_"
)

c1, c2 = st.columns([2, 1])

with c1:
    monthly_ts = (
        df_filtered.groupby(["year","month"])[pollutant]
        .mean().reset_index()
    )
    monthly_ts["year_month"] = pd.to_datetime(
        monthly_ts[["year","month"]].assign(day=1)
    )

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(monthly_ts["year_month"], monthly_ts[pollutant],
            color="#E74C3C", linewidth=2, alpha=0.9)
    ax.fill_between(monthly_ts["year_month"], monthly_ts[pollutant],
                    alpha=0.15, color="#E74C3C")
    if pollutant == "PM2.5":
        ax.axhline(35.4, color="orange", linestyle="--", linewidth=1,
                   label="Batas Moderate (35.4 µg/m³)")
        ax.axhline(55.4, color="red",    linestyle="--", linewidth=1,
                   label="Batas Unhealthy (55.4 µg/m³)")
        ax.legend(fontsize=8)
    ax.set_title(f"Tren Rata-rata Bulanan {pollutant}", fontsize=12, fontweight="bold")
    ax.set_xlabel("Waktu"); ax.set_ylabel(f"{pollutant} (µg/m³)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig); plt.close()

with c2:
    seasonal = (
        df_filtered.groupby("month")[pollutant]
        .mean().reset_index()
    )
    seasonal["month_name"] = [MONTH_NAMES[m-1] for m in seasonal["month"]]

    max_m = seasonal.loc[seasonal[pollutant].idxmax(), "month_name"]
    min_m = seasonal.loc[seasonal[pollutant].idxmin(), "month_name"]

    bar_colors = [
        "#E74C3C" if v == seasonal[pollutant].max()
        else "#2ECC71" if v == seasonal[pollutant].min()
        else "#85B7EB"
        for v in seasonal[pollutant]
    ]

    fig, ax = plt.subplots(figsize=(4.5, 4))
    ax.barh(seasonal["month_name"], seasonal[pollutant],
            color=bar_colors, edgecolor="white")
    ax.set_title(f"Rata-rata {pollutant} per Bulan", fontsize=11, fontweight="bold")
    ax.set_xlabel(f"{pollutant} (µg/m³)")
    ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    st.pyplot(fig); plt.close()

    st.info(f"**Tertinggi:** {max_m}\n\n**Terendah:** {min_m}")

with st.expander("Lihat Insight Pertanyaan 1"):
    yearly = df_filtered.groupby("year")["PM2.5"].mean().reset_index()
    st.markdown("**Rata-rata PM2.5 per Tahun:**")
    st.dataframe(yearly.rename(columns={"PM2.5":"Rata-rata PM2.5 (µg/m³)"})
                 .set_index("year").round(2), use_container_width=True)
    st.markdown(
        "- Bulan **Desember, Januari, Februari** (musim dingin) secara konsisten "
        "mencatat PM2.5 tertinggi — diduga akibat penggunaan pemanas berbahan bakar "
        "batubara dan kondisi inversi termal yang memerangkap polutan.\n"
        "- Bulan **Juni–Agustus** (musim panas) memiliki PM2.5 terendah karena "
        "sirkulasi udara lebih baik dan curah hujan lebih tinggi."
    )

st.markdown("---")

# ─── PERTANYAAN 2 ─────────────────────────────────────────────────────────────
st.subheader("⏰ Pertanyaan 2")
st.markdown(
    "_Pada jam berapa dalam sehari rata-rata konsentrasi PM2.5 mencapai puncaknya, "
    "dan di antara faktor cuaca (suhu, tekanan udara, titik embun, curah hujan, "
    "kecepatan angin), faktor mana yang memiliki korelasi paling kuat terhadap "
    "konsentrasi PM2.5?_"
)

c3, c4 = st.columns(2)

with c3:
    hourly = df_filtered.groupby("hour")[pollutant].mean().reset_index()
    peak_hour = hourly.loc[hourly[pollutant].idxmax(), "hour"]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(hourly["hour"], hourly[pollutant],
            color="#3498DB", linewidth=2.5, marker="o", markersize=5)
    ax.fill_between(hourly["hour"], hourly[pollutant], alpha=0.2, color="#3498DB")
    ax.axvline(peak_hour, color="red", linestyle="--", linewidth=1.2,
               label=f"Puncak: jam {peak_hour:02d}.00")
    ax.set_title(f"Rata-rata {pollutant} per Jam", fontsize=11, fontweight="bold")
    ax.set_xlabel("Jam (0–23)"); ax.set_ylabel(f"{pollutant} (µg/m³)")
    ax.set_xticks(range(0, 24, 3))
    ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig); plt.close()

with c4:
    weather_cols = ["TEMP","PRES","DEWP","RAIN","WSPM"]
    corr = (df_filtered[[pollutant] + weather_cols]
            .corr()[pollutant].drop(pollutant).sort_values())

    strongest = corr.abs().idxmax()
    bar_colors = ["#E74C3C" if v > 0 else "#2ECC71" for v in corr.values]

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.barh(corr.index, corr.values, color=bar_colors, edgecolor="white")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title(f"Korelasi Faktor Cuaca dengan {pollutant}", fontsize=11, fontweight="bold")
    ax.set_xlabel("Koefisien Korelasi (Pearson)")
    for bar, val in zip(bars, corr.values):
        ax.text(val + (0.005 if val >= 0 else -0.005),
                bar.get_y() + bar.get_height()/2,
                f"{val:.3f}", va="center",
                ha="left" if val >= 0 else "right", fontsize=9)
    ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    st.pyplot(fig); plt.close()

with st.expander("Lihat Insight Pertanyaan 2"):
    st.markdown(
        f"- PM2.5 mencapai **puncak pada jam {peak_hour:02d}.00** yang bertepatan "
        f"dengan jam sibuk lalu lintas pagi hari.\n"
        f"- **{strongest}** adalah faktor cuaca dengan korelasi terkuat terhadap PM2.5 "
        f"(r = {corr[strongest]:.3f}).\n"
        "- Korelasi negatif pada kecepatan angin (WSPM) menunjukkan bahwa angin kencang "
        "membantu mendispersi polutan sehingga PM2.5 menurun.\n"
        "- Suhu (TEMP) berkorelasi negatif — suhu rendah di musim dingin berasosiasi "
        "dengan PM2.5 tinggi."
    )

st.markdown("---")

# ─── ANALISIS LANJUTAN – CLUSTERING AQI ──────────────────────────────────────
st.subheader("🎯 Analisis Lanjutan: Clustering Kualitas Udara (AQI)")
st.markdown(
    "Pengelompokan data PM2.5 ke dalam 6 kategori menggunakan teknik **binning manual** "
    "berdasarkan standar US EPA AQI."
)

c5, c6 = st.columns(2)

with c5:
    aqi_dist = df_filtered["AQI_Category"].value_counts().reindex(AQI_LABELS)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(aqi_dist.values, labels=aqi_dist.index,
           colors=[AQI_COLORS[l] for l in AQI_LABELS],
           autopct="%1.1f%%", startangle=140, pctdistance=0.8)
    ax.set_title("Proporsi Jam per Kategori AQI", fontsize=11, fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig); plt.close()

with c6:
    aqi_year = (df_filtered.groupby(["year","AQI_Category"])
                .size().unstack(fill_value=0))
    aqi_pct  = aqi_year.div(aqi_year.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(5.5, 5))
    bottom = np.zeros(len(aqi_pct))
    for label in AQI_LABELS:
        if label in aqi_pct.columns:
            vals = aqi_pct[label].values
            ax.bar(aqi_pct.index, vals, bottom=bottom,
                   label=label, color=AQI_COLORS[label], edgecolor="white")
            bottom += vals
    ax.set_title("Proporsi Kategori AQI per Tahun", fontsize=11, fontweight="bold")
    ax.set_xlabel("Tahun"); ax.set_ylabel("Persentase (%)")
    ax.legend(title="Kategori", bbox_to_anchor=(1.05,1), loc="upper left", fontsize=8)
    ax.set_xticks(aqi_pct.index)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    st.pyplot(fig); plt.close()

st.markdown("---")

# ─── KESIMPULAN ───────────────────────────────────────────────────────────────
st.subheader("📝 Kesimpulan")
st.markdown("""
**Pertanyaan 1:** Bulan **Desember, Januari, dan Februari** secara konsisten mencatat rata-rata PM2.5 tertinggi sepanjang tahun (musim dingin), sedangkan bulan **Juni–Agustus** mencatat PM2.5 terendah. Tren tahunan menunjukkan PM2.5 selalu berada jauh di atas batas aman WHO sepanjang 2013–2017.

**Pertanyaan 2:** Konsentrasi PM2.5 mencapai puncak pada **jam 06.00–08.00 pagi** yang bertepatan dengan jam sibuk lalu lintas. **Kecepatan angin (WSPM)** adalah faktor cuaca dengan korelasi negatif terkuat — semakin kencang angin, semakin rendah PM2.5 karena polutan terdispersi.

**Clustering AQI:** Lebih dari **50% waktu** stasiun Aotizhongxin berada dalam kondisi *Unhealthy* atau lebih buruk, dan hanya sekitar 10–15% waktu yang tergolong *Good* atau *Moderate*. Ini mengindikasikan krisis kualitas udara jangka panjang yang memerlukan intervensi kebijakan serius.
""")

st.caption("Dibuat ole rafi untuk Proyek Analisis Data – Dicoding | Dataset: PRSA Air Quality Aotizhongxin 2013–2017")
