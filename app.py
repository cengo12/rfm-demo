import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

try:
    st.set_page_config(page_title="RFM Müşteri Segmentasyonu",
                       page_icon=":chart_with_upwards_trend:",
                       layout="wide",
                       initial_sidebar_state="collapsed")

    # Renders sidebar file upload menu and returns uploaded file
    with st.sidebar:
        excel_file = st.file_uploader(
            label="Excel Dosyasını Yükle",
            type=['xlsx', 'xlsm'],
            accept_multiple_files=False
        )

        with st.form(key="settingsForm"):
            c1, c2 = st.columns(2)
            with c1:
                company_name = st.text_input(
                    label="Firma Adı Sütun Başlığı",
                    value="FİRMA",
                    placeholder="Gerekli Alan"
                )

                order_no = st.text_input(
                    label="Sipariş No Sütun Başlığı",
                    value="NO ",
                    placeholder="Gerekli Alan"
                )

                order_check = st.text_input(
                    label="Son Durum Sütun Başlığı",
                    value="SON DURUM",
                    placeholder="Gerekli Alan"
                )

            with c2:
                order_date = st.text_input(
                    label="Tarih Seçimi Sütun Başlığı",
                    value="TARİH",
                    placeholder="Gerekli Alan"
                )

                order_amount = st.text_input(
                    label="Toplam Tutar Sütun Başlığı",
                    value="TL TUTAR",
                    placeholder="Gerekli Alan"
                )

                check_value = st.text_input(
                    label="Dosyadaki Sipariş Onay Metni",
                    value="TEKLİF GÖNDERİLDİ",
                    placeholder="Gerekli Alan"
                )

            st.form_submit_button(
                label="Onayla"
            )

    # Read excel file and create a pandas dataframe
    df = pd.read_excel(excel_file)

    # Drop columns except specified in settings
    df = df[[company_name, order_no, order_date, order_amount, order_check]]

    # Drop all rows containing null values
    df.dropna()

    # Clear non numeric values
    df = df[pd.to_numeric(df[order_amount], errors='coerce').notnull()]

    # Drop all rows with no purchase
    df = df[df[order_check] == check_value]

    # Convert date column to datetime
    df[order_date] = pd.to_datetime(df[order_date])

    # Get most recent date for recency score calculation
    most_recent_date = df[order_date].max()

    # Create rfm table
    rfm_table = df.groupby(company_name).agg({order_date: lambda x: (most_recent_date - x.max()).days,  # Recency
                                              order_no: lambda x: len(x.unique()),  # Frequency
                                              order_amount: lambda x: x.sum()})  # Monetary

    rfm_table[order_date] = rfm_table[order_date].astype(int)

    rfm_table.rename(columns={order_date: 'recency',
                              order_no: 'frequency',
                              order_amount: 'monetary_value'}, inplace=True)

    # Calculate rfm score and add to dataframe

    # Calculate quantiles for use in scoring
    quantiles = rfm_table.quantile(q=[0.2, 0.4, 0.6, 0.8])
    quantiles = quantiles.to_dict()


    # Arguments (x = value, p = recency, monetary_value, frequency, d = quartiles dict)
    def r_score(x, p, d):
        if x <= d[p][0.20]:
            return 5
        elif x <= d[p][0.40]:
            return 4
        elif x <= d[p][0.60]:
            return 3
        elif x <= d[p][0.80]:
            return 2
        else:
            return 1


    # Arguments (x = value, p = recency, monetary_value, frequency, d = quartiles dict)
    def fm_score(x, p, d):
        if x <= d[p][0.20]:
            return 1
        elif x <= d[p][0.40]:
            return 2
        elif x <= d[p][0.60]:
            return 3
        elif x <= d[p][0.80]:
            return 4
        else:
            return 5


    rfm_table['R_Quartile'] = rfm_table['recency'].apply(r_score, args=('recency', quantiles,))
    rfm_table['F_Quartile'] = rfm_table['frequency'].apply(fm_score, args=('frequency', quantiles,))
    rfm_table['M_Quartile'] = rfm_table['monetary_value'].apply(fm_score, args=('monetary_value', quantiles,))
    rfm_table['RFMClass'] = rfm_table.R_Quartile.map(str) \
                            + rfm_table.F_Quartile.map(str) \
                            + rfm_table.M_Quartile.map(str)

    rfm_table['RFMClass'] = rfm_table['RFMClass'].astype('int')

    # ----RFM Score Based Segmentation----
    r = rfm_table['R_Quartile']
    f = rfm_table['F_Quartile']
    m = rfm_table['M_Quartile']

    conditions = [
        # Champions
        (r >= 4) & (r <= 5) &
        (f >= 4) & (f <= 5) &
        (m >= 4) & (m <= 5),

        # Loyal Customers
        (r >= 3) & (r <= 5) &
        (f >= 3) & (f <= 5) &
        (m >= 3) & (m <= 5),

        # Potential Loyalist
        (r >= 3) & (r <= 5) &
        (f >= 2) & (f <= 5) &
        (m >= 1) & (m <= 3),

        # Recent Customers
        (r >= 3) & (r <= 5) &
        (f >= 1) & (f <= 2) &
        (m >= 1) & (m <= 2),

        # Promising
        (r >= 3) & (r <= 5) &
        (f >= 1) & (f <= 2) &
        (m >= 3) & (m <= 5),

        # Customers Needing Attention
        (r >= 3) & (r <= 5) &
        (f >= 2) & (f <= 4) &
        (m >= 3) & (m <= 5),

        # About To Sleep
        (r >= 2) & (r <= 3) &
        (f >= 1) & (f <= 3) &
        (m >= 1) & (m <= 3),

        # At Risk
        (r >= 1) & (r <= 2) &
        (f >= 2) & (f <= 5) &
        (m >= 2) & (m <= 5),

        # Can't Lose Them
        (r >= 1) & (r <= 2) &
        (f >= 1) & (f <= 5) &
        (m >= 3) & (m <= 5),

        # Hibernating
        (r >= 1) & (r <= 3) &
        (f >= 1) & (f <= 4) &
        (m >= 1) & (m <= 3),

        # Lost
        (r >= 1) & (r <= 1) &
        (f >= 1) & (f <= 5) &
        (m >= 1) & (m <= 2)
    ]

    values = ['Şampiyonlar',
              'Sadık Müşteriler',
              'Potansiyel Sadık Müşteriler',
              'Son Müşteriler',
              'Umut Verici Müşteriler',
              'Dikkat İsteyen Müşteriler',
              'Uyumak Üzere Olan Müşteriler',
              'Riskteki Müşteriler',
              'Kaybedilmemesi Gereken Müşteriler',
              'Uyuyan Müşteriler',
              'Kayıp Müşteriler']

    # Add segmentation column
    rfm_table['RFM Segmentasyonu'] = np.select(conditions, values)

    segments_df = rfm_table['RFM Segmentasyonu'].value_counts().rename_axis('unique_values').reset_index(name='counts')

    fig = px.histogram(rfm_table, x='RFM Segmentasyonu', text_auto=True).update_xaxes(categoryorder="max descending")

    pie = px.pie(rfm_table,
                 values=rfm_table['RFM Segmentasyonu'].value_counts().values,
                 names=rfm_table['RFM Segmentasyonu'].value_counts().index,
                 )

    tree = px.treemap(segments_df,
                      path=["unique_values"],
                      values='counts')

    colors = ['#fae588', '#f79d65', '#f9dc5c', '#e8ac65', '#e76f51', '#ef233c', '#b7094c', '#f9dc5c',
              '#e76f51']  # color palette

    tree.update_layout(
        treemapcolorway=colors,  # defines the colors in the treemap
        margin=dict(t=50, l=25, r=25, b=25))

    st.title("RFM Skoru ile Müşteri Segmentasyonu")

    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            st.dataframe(rfm_table, width=1400)
        with c2:
            st.write(pie)

    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            st.write(fig, width=1500)
        with c2:
            st.write(tree)

except Exception:
    st.error("Yan Menüden Excel Dosyasını Yükleyiniz")

