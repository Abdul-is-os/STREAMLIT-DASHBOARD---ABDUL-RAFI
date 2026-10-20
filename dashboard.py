import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi Halaman
st.set_page_config(
    page_title="Bike Sharing Performance Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Memuat Data dengan Caching
@st.cache_data
def load_data():
    day_df = pd.read_csv("day_clean.csv")
    hour_df = pd.read_csv("hour_clean.csv")
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    return day_df, hour_df

day_df, hour_df = load_data()

# Filter Rentang Tanggal di Sidebar
st.sidebar.header("Filter Data")
min_date = day_df['dteday'].min()
max_date = day_df['dteday'].max()

try:
    date_range = st.sidebar.date_input(
        label="Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date
except Exception:
    start_date, end_date = min_date, max_date

filtered_day = day_df[(day_df['dteday'] >= pd.to_datetime(start_date)) & (day_df['dteday'] <= pd.to_datetime(end_date))]
filtered_hour = hour_df[(hour_df['dteday'] >= pd.to_datetime(start_date)) & (hour_df['dteday'] <= pd.to_datetime(end_date))]

# Header & Ringkasan Metrik
st.title("🚲 Bike Sharing Performance Dashboard")
st.markdown("Dasbor Interaktif Analisis Penyewaan Sepeda (2011-2012)")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Penyewaan", value=f"{filtered_day['cnt'].sum():,} Unit")
with col2:
    st.metric("Rata-Rata Harian", value=f"{filtered_day['cnt'].mean():,.0f} Unit")
with col3:
    st.metric("Total Pengguna Terdaftar", value=f"{filtered_day['registered'].sum():,} User")

st.markdown("---")

# Visualisasi Pertanyaan Bisnis 1
st.subheader("1. Pengaruh Musim Terhadap Penyewaan Sepeda")
season_eda = filtered_day.groupby('season').agg(avg_cnt=('cnt', 'mean')).reset_index()

fig1, ax1 = plt.subplots(figsize=(10, 4))
sns.set_theme(style="whitegrid")
max_val = season_eda['avg_cnt'].max() if not season_eda.empty else 0
colors = ["#1f77b4" if val == max_val else "#d3d3d3" for val in season_eda['avg_cnt']]

sns.barplot(x='season', y='avg_cnt', data=season_eda, palette=colors, ax=ax1)
ax1.set_title("Rata-Rata Penyewaan Harian Berdasarkan Musim", fontweight='bold')
ax1.set_xlabel("Musim")
ax1.set_ylabel("Rata-Rata Unit")

for p in ax1.patches:
    if p.get_height() > 0:
        ax1.annotate(f"{p.get_height():,.0f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', xytext=(0, 3), textcoords='offset points', fontweight='bold')

st.pyplot(fig1)

with st.expander("Lihat Kesimpulan & Rekomendasi Musim"):
    st.write(
        "**Kesimpulan:** Musim Gugur (Fall) dan Musim Panas (Summer) menjadi puncak penyewaan sepeda harian tertinggi, sedangkan Musim Semi (Spring) mencatat angka terendah.\n\n"
        "**Rekomendasi:** Mobilisasi 90%-100% kapasitas armada selama Musim Panas dan Gugur. Manfaatkan Musim Semi untuk penarikan unit secara bertahap guna pemeliharaan besar-besaran."
    )

st.markdown("---")

# Visualisasi Pertanyaan Bisnis 2
st.subheader("2. Pola Jam Sibuk & Prioritas Jadwal Pemeliharaan (Maintenance)")
hourly_analysis = filtered_hour.groupby(['workingday', 'hr']).agg(avg_cnt=('cnt', 'mean')).reset_index()

fig2, ax2 = plt.subplots(figsize=(12, 4))
sns.lineplot(x='hr', y='avg_cnt', hue='workingday', data=hourly_analysis, marker='o', linewidth=2, palette=['#ff7f0e', '#1f77b4'], ax=ax2)
ax2.set_title("Pola Penyewaan Per Jam: Hari Kerja vs Akhir Pekan", fontweight='bold')
ax2.set_xlabel("Jam (00:00 - 23:00)")
ax2.set_ylabel("Rata-Rata Unit")
ax2.set_xticks(range(0, 24))
ax2.axvspan(0, 5, color='green', alpha=0.15, label='Window Maintenance')
ax2.legend(title="Jenis Hari", loc="upper left")

st.pyplot(fig2)

with st.expander("Lihat Kesimpulan & Rekomendasi Pemeliharaan"):
    st.write(
        "**Kesimpulan:** Hari kerja memiliki dua puncak komuter (07:00–09:00 dan 17:00–19:00). Volume penyewaan terendah terjadi pada pukul 00:00–05:00 dini hari.\n\n"
        "**Rekomendasi:** Jadwalkan seluruh perawatan teknis berat dan redistribusi unit antar-stasiun pada pukul 01:00–05:00 dini hari agar armada siap 100% sebelum jam sibuk pagi."
    )