from cgmzscore.src.main import z_score_lhfa

def calculate_zscore (umur_bulan, jenis_kelamin, tinggi):

    sex = 'M' if jenis_kelamin == "Laki - laki" else 'F'
    age_in_days = round(umur_bulan * 30.4375)

    if age_in_days < 0 or age_in_days > 1825:
        raise ValueError("Umur diluar rentang WHO (0-60 bulan).")

    z_score = z_score_lhfa(age_in_days=age_in_days, sex=sex, height=(tinggi))

    return z_score