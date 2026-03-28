# Proyek Analisis Data: Air Quality Dataset – Aotizhongxin, Beijing

## Deskripsi Proyek
Proyek ini menganalisis kualitas udara di stasiun **Aotizhongxin, Beijing** menggunakan dataset PRSA Air Quality Dataset (2013–2017). Analisis mencakup tren polutan PM2.5, pola musiman, korelasi dengan faktor cuaca, dan clustering kualitas udara berbasis standar AQI.

## Pertanyaan Bisnis
1. Bagaimana tren rata-rata PM2.5 dari 2013–2017, dan pada bulan apa kualitas udara paling buruk?
2. Apakah ada pola harian dalam PM2.5, dan faktor cuaca apa yang paling berpengaruh?

## Struktur Proyek
```
submission/
├── dashboard/
│   ├── main_data.csv        # Dataset utama untuk dashboard
│   └── dashboard.py         # Script Streamlit
├── data/
│   ├── data_1.csv           # Dataset mentah lengkap
│   └── data_2.csv           # Dataset agregat bulanan
├── notebook.ipynb           # Notebook analisis lengkap
├── README.md
├── requirements.txt
└── url.txt                  # Link deployment Streamlit Cloud
```

## Setup & Cara Menjalankan

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Jalankan dashboard
```bash
streamlit run dashboard/dashboard.py
```

## Teknik Analisis
- **Eksplorasi Data**: Statistik deskriptif, analisis missing values
- **Visualisasi**: Time series, bar chart, scatter, pie chart
- **Analisis Lanjutan**: Clustering manual menggunakan binning AQI (US EPA standard)

## Dataset
- **Sumber**: PRSA Air Quality Dataset
- **Stasiun**: Aotizhongxin, Beijing
- **Periode**: Maret 2013 – Februari 2017
- **Jumlah data**: 35.064 baris (data per jam)
