import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from pathlib import Path

# Konfigurasi halaman
st.set_page_config(
    page_title='Sectoral Stock Prediction Dashboard',
    page_icon='📈',
    layout='wide'
)

# Custom CSS untuk styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #0066cc;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #0052a3;
    }
    .main > div {
        padding: 2rem;
        border-radius: 10px;
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    .prediction-card {
        background-color: #f7f7f7;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #0066cc;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        background-color: #f1f3f4;
        border-radius: 4px;
    }
    .stTabs [data-baseweb="tab-list"] button:hover {
        background-color: #e8eaed;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0066cc !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Judul dengan styling
st.markdown("""
    <h1 style='text-align: center; color: #0066cc; margin-bottom: 2rem;'>
        📈 Prediksi Saham Sektoral dengan Model STACN
    </h1>
    """, unsafe_allow_html=True)

# Definisi sektor
sectors = {
    "A - Energy": "ENRG",
    "B - Basic Materials": "BASIC",
    "C - Industrials": "INDS",
    "D - Noncyclicals": "NONCYC",
    "E - Cyclicals": "CYC",
    "F - Healthcare": "HEALTH",
    "G - Financials": "FIN",
    "H - Properties": "PROP",
    "I - Technology": "TECH",
    "J - Infrastructures": "INFRA",
    "K - Transportation": "TRANS"
}

# Data historis dengan cache
@st.cache_data
def load_historical_data(sector_code):
    try:
        file_path = Path(f"data/{sector_code}_data.csv")
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        return df
    except Exception as e:
        st.error(f"Error loading data for sector {sector_code}: {str(e)}")
        return pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Stock Num'])
   

tabs = st.tabs(list(sectors.keys()))

# Mapping for file names
sector_file_mapping = {
    "ENRG": "A",
    "BASIC": "B",
    "INDS": "C",
    "NONCYC": "D",
    "CYC": "E",
    "HEALTH": "F",
    "FIN": "G",
    "PROP": "H",
    "TECH": "I",
    "INFRA": "J",
    "TRANS": "K"
}


for tab, (sector_name, sector_code) in zip(tabs, sectors.items()):
    with tab:
        file_prefix = sector_file_mapping[sector_code]
        df = load_historical_data(file_prefix)
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"### 📰 Input Berita & Prediksi - {sector_name}")
            
            with st.form(f"prediction_form_{sector_code}"):
                news_date = st.date_input(f"Tanggal Berita", value=date.today(), key=f"date_{sector_code}")
                
                st.markdown("##### Judul Berita Hari Ini")
                news_titles = st.text_area(
                    "Masukkan 5 Judul Berita (Pisahkan dengan Enter)",
                    height=150,
                    placeholder="Contoh:\nBerita 1\nBerita 2\nBerita 3...",
                    key=f"news_{sector_code}"
                )
                
                prediction_range = st.select_slider(
                    "Rentang Prediksi",
                    options=["1 Hari", "2 Hari", "3 Hari", "5 Hari", "10 Hari"],
                    value="5 Hari",
                    key=f"range_{sector_code}"
                )
                
                submit_button = st.form_submit_button("Prediksi Harga Saham")
                
                if submit_button:
                    # ... (kode prediksi yang sama seperti sebelumnya, dengan penambahan key unik) ...
                    with st.spinner('Melakukan prediksi...'):
                        days = int(prediction_range.split()[0])
                        last_price = df['Close'].iloc[-1]
                        
                        def generate_predictions(start_price, days, volatility=0.015):
                            prices = [start_price]
                            for i in range(days):
                                change = np.random.normal(0.002, volatility) 
                                new_price = prices[-1] * (1 + change)
                                prices.append(new_price)
                            return prices[1:]
                        
                        predictions = generate_predictions(last_price, days)
                        future_dates = [(date.today() + timedelta(days=i+1)).strftime('%d %b') for i in range(days)]
                        
                        st.success(f"Prediksi untuk {days} hari ke depan berhasil!")
                        
                        # Grafik prediksi
                        hist_dates = df['Date'].iloc[-5:].tolist()
                        hist_prices = df['Close'].iloc[-5:].tolist()
                        
                        fig2 = go.Figure()
                        fig2.add_trace(go.Scatter(
                            x=hist_dates, 
                            y=hist_prices,
                            mode='lines',
                            name='Historis',
                            line=dict(color='#0066cc', width=2)
                        ))
                        
                        fig2.add_trace(go.Scatter(
                            x=[hist_dates[-1]] + [datetime.strptime(f"{date.today().year} {d}", "%Y %d %b") for d in future_dates],
                            y=[hist_prices[-1]] + predictions,
                            mode='lines+markers',
                            name='Prediksi',
                            line=dict(color='#FF9900', width=2, dash='dot'),
                            marker=dict(size=8)
                        ))
                        
                        fig2.update_layout(
                            title=f'Prediksi Harga - {sector_name}',
                            yaxis_title='Harga',
                            xaxis_title='Tanggal',
                            template='plotly_white',
                            height=400
                        )
                        
                        st.plotly_chart(fig2, use_container_width=True)
                        
                        # Hasil prediksi detail
                        st.markdown("##### Hasil Prediksi Detail:")
                        pred_cols = st.columns(min(3, days))
                        
                        for i, (date_str, pred_price) in enumerate(zip(future_dates, predictions)):
                            with pred_cols[i % len(pred_cols)]:
                                change = ((pred_price - last_price if i == 0 else 
                                         pred_price - predictions[i-1]) / 
                                        (last_price if i == 0 else predictions[i-1])) * 100
                                
                                st.markdown(f"""
                                <div class="prediction-card">
                                    <h6>{date_str}</h6>
                                    <p style="font-size: 1.2rem; font-weight: bold">${pred_price:.2f} 
                                    <span style="color: {'green' if change >= 0 else 'red'};">
                                        {'↑' if change >= 0 else '↓'} {abs(change):.2f}%
                                    </span></p>
                                </div>
                                """, unsafe_allow_html=True)

        # PANEL ANALISIS HISTORIS DI KANAN
        with col2:
            st.markdown(f"### 📊 Analisis Data Historis - {sector_name}")
            
            # Metrics
            m1, m2 = st.columns(2)
            with m1:
                st.metric("Harga Terakhir", f"${df['Close'].iloc[-1]:.2f}", 
                         f"{((df['Close'].iloc[-1] - df['Close'].iloc[-2])/df['Close'].iloc[-2]*100):.2f}%")
            with m2:
                st.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}", 
                         f"{((df['Volume'].iloc[-1] - df['Volume'].iloc[-2])/df['Volume'].iloc[-2]*100):.2f}%")
            
            # Chart
            time_range = st.select_slider(
                "Rentang Waktu",
                options=["5 Hari", "10 Hari", "1 Bulan", "3 Bulan"],
                value="10 Hari",
                key=f"timerange_{sector_code}"
            )

            ranges = {
                "5 Hari": 5,
                "10 Hari": 10,
                "1 Bulan": 30,
                "3 Bulan": 90
            }

            filtered_df = df.tail(ranges[time_range])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=filtered_df['Date'],
                y=filtered_df['Close'],
                mode='lines',
                name='Close',
                line=dict(color='#0066cc', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=filtered_df['Date'],
                y=filtered_df['Open'],
                mode='lines',
                name='Open',
                line=dict(color='#00cc66', width=2)
            ))
            
            fig.update_layout(
                title=f'Pergerakan Harga Saham - {sector_name}',
                yaxis_title='Harga',
                xaxis_title='Tanggal',
                template='plotly_white',
                height=400,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)

            # Update the historical data detail section
            st.markdown("##### Data Historis Detail")
            if not df.empty:
                display_df = df.copy()
                numeric_cols = display_df.select_dtypes(include=[np.number]).columns
                format_dict = {}
                for col in numeric_cols:
                    if 'price' in col.lower() or col in ['Open', 'High', 'Low', 'Close']:
                        format_dict[col] = '${:.2f}'
                    elif 'volume' in col.lower() or col == 'Volume':
                        format_dict[col] = '{:,.0f}'
                    else:
                        format_dict[col] = '{:.2f}'
                
                st.dataframe(
                    display_df.style.format(format_dict),
                    height=200
                )
            else:
                st.warning(f"No historical data available for {sector_name}")
