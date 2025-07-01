import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
from dotenv import load_dotenv
import os
from cgmzscore.src.main import z_score_lhfa  # TB/U sesuai kewajiban

# Load konfigurasi
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

# Koneksi ke PostgreSQL
@st.cache_resource
def get_engine():
    return create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

engine = get_engine()

st.title("Prediksi Stunting via ZScore TB/U (cgmzscore)")

with st.form("form_input"):
    umur = st.number_input("Umur anak (bulan)", max_value=60)
    jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    tinggi = st.number_input("Tinggi badan anak (cm)", min_value=30.0, max_value=130.0)
    submit = st.form_submit_button("Prediksi dan Simpan")

if submit:
    try:
        sex = 'M' if jenis_kelamin == "Laki-laki" else 'F'
#INI RUMUS NYA GES 
        zscore = z_score_lhfa(age_in_days=umur*30, sex=sex, height=str(tinggi))
        status = "Stunting" if zscore < -2 else "Tidak Stunting"

        st.write(f"Zscore tinggi per umur: **{zscore:.2f}**")
        if status == "stunting":
            st.error("stunting")
        else:
            st.success("Tidak stunting")
#DISIMPAN DULU GES DI DB
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO prediksi_stunting
                (umur_bulan, jenis_kelamin, tinggi_badan, zscore, status_prediksi)
                VALUES (:umur, :jk, :tb, :zs, :st)
            """), {
                "umur": umur, "jk": jenis_kelamin,
                "tb": tinggi, "zs": round(zscore, 2), "st": status
            })
            conn.commit()
        st.success("Data berhasil disimpan.")
    except Exception as e:
        st.error("Terjadi kesalahan:")
        st.error(e)

# # Tampilkan riwayat
# st.subheader("Riwayat Prediksi Terakhir")
# try:
#     df = pd.read_sql("SELECT * FROM prediksi_stunting ORDER BY id DESC LIMIT 100", engine)
#     st.dataframe(df)
# except Exception as e:
#     st.error("Gagal memuat riwayat.")
#     st.error(e)
