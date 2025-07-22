import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
from db import get_engine
from zscore_utils import calculate_zscore

engine = get_engine()

st.title("Prediksi Stunting via ZScore TB/U (cgmzscore)")

with st.form("form_input"):
    umur = st.number_input("Umur anak (bulan)", max_value=60)
    jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    tinggi = st.number_input("Tinggi badan anak (cm)", min_value=30.0, max_value=130.0)
    submit = st.form_submit_button("Prediksi dan Simpan")

if submit:
    try:
        zscore = calculate_zscore(umur, jenis_kelamin, tinggi)
        if zscore < -3:
            status = "Stunting Berat"
        elif zscore < -2:
            status = "Stunting"
        else:
            status = "Tidak Stunting"

        st.write(f"Z-Score TB/U: **{zscore:.2f}**")

        if status in ["Stunting Berat", "Stunting"]:
            st.error(f"Status: {status}")
        else:
            st.success(f"Status: {status}")

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