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
        # Construct file path based on sector code
        file_path = Path(f"data/{sector_code}_data.csv")
        
        # Read the CSV file with exact column names
        df = pd.read_csv(file_path, parse_dates=['date'])
        
        # Ensure all numeric columns are float
        numeric_cols = ['open', 'high', 'low', 'close', 'stock_num', 'vol']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Sort by date to ensure correct order
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    except Exception as e:
        st.error(f"Error loading data for sector {sector_code}: {str(e)}")
        return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'stock_num', 'vol'])

   
tabs = st.tabs(list(sectors.keys()))

sector_file_mapping = {
    "ENRG": "A",    # Energy
    "BASIC": "B",   # Basic Materials
    "INDS": "C",    # Industrials
    "NONCYC": "D",  # Consumer Noncyclicals
    "CYC": "E",     # Consumer Cyclicals
    "HEALTH": "F",  # Healthcare
    "FIN": "G",     # Financials
    "PROP": "H",    # Properties & Real Estate
    "TECH": "I",    # Technology
    "INFRA": "J",   # Infrastructures
    "TRANS": "K"    # Transportation & Logistic
}

# In the tab loop, update how you load the data:
for tab, (sector_name, sector_code) in zip(tabs, sectors.items()):
    with tab:
        # Get the corresponding file prefix
        file_prefix = sector_file_mapping[sector_code]
        df = load_historical_data(file_prefix)


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

            # Metrics with error handling
            m1, m2 = st.columns(2)
            with m1:
                if not df.empty and len(df) > 1:
                    last_close = df['close'].iloc[-1]
                    prev_close = df['close'].iloc[-2]
                    close_change = ((last_close - prev_close) / prev_close * 100)
                    st.metric("Harga Close", f"Rp {last_close:,.0f}", f"{close_change:.2f}%")
                else:
                    st.metric("Harga Close", "N/A", "0%")

            with m2:
                if not df.empty and len(df) > 1:
                    # Calculate YTD performance
                    current_year = pd.Timestamp.now().year
                    start_of_year = pd.Timestamp(f"{current_year}-01-01")
                    df_ytd = df[df['date'] >= start_of_year]
            
                    if not df_ytd.empty:
                        start_price = df_ytd['close'].iloc[0]
                        last_close = df['close'].iloc[-1]
                        ytd_change = ((last_close - start_price) / start_price) * 100
                        st.metric("Performa YTD", f"{ytd_change:.2f}%", delta=f"{(ytd_change):.2f}%")
                    else:
                        st.metric("Performa YTD", "N/A", "0%")
                else:
                    st.metric("Performa YTD", "N/A", "0%")
            
            # Chart section
            if not df.empty:
                time_range = st.selectbox(
                    "Rentang Waktu",
                    options=["1 Minggu", "1 Bulan", "3 Bulan", "All Time"],
                    index=1,
                    key=f"timerange_{sector_code}"
                )
            
                ranges = {
                    "1 Minggu": 7,
                    "1 Bulan": 30,
                    "3 Bulan": 90,
                    "All Time": len(df)
                }
            
                # Ensure date is datetime and sorted
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date').reset_index(drop=True)
            
                # Get the filtered data
                filtered_df = df.tail(ranges[time_range])
            
                # Create figure
                fig = go.Figure()
            
                # Add Close price line
                fig.add_trace(go.Scatter(
                    x=filtered_df['date'],
                    y=filtered_df['close'],
                    mode='lines',
                    name='Close',
                    line=dict(color='#0066cc', width=2)
                ))
            
                # Add Open price line
                fig.add_trace(go.Scatter(
                    x=filtered_df['date'],
                    y=filtered_df['open'],
                    mode='lines',
                    name='Open',
                    line=dict(color='#00cc66', width=2)
                ))
            
                # Update layout
                fig.update_layout(
                    title=dict(
                        text=f'Pergerakan Harga Saham - {sector_name}',
                        x=0.5,
                        font=dict(size=20)
                    ),
                    yaxis_title='Harga (IDR)',
                    xaxis_title='Tanggal',
                    template='plotly_white',
                    height=400,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    hovermode='x unified'
                )
            
                # Format y-axis
                fig.update_yaxes(tickformat=",")
            
                # Show plot
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Tidak ada data untuk ditampilkan dalam grafik")
            
            # Historical data section
            st.markdown("##### Data Historis Detail")
            if not df.empty:
                display_df = df.rename(columns={
                    'date': 'Tanggal',
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'stock_num': 'Stock Num',
                    'vol': 'Volume'
                })
            
                # Format date to dd/mm/yyyy
                display_df['Tanggal'] = pd.to_datetime(display_df['Tanggal']).dt.strftime('%d/%m/%Y')
            
                # Date filter
                min_date = pd.to_datetime(display_df['Tanggal'], format='%d/%m/%Y').min()
                max_date = pd.to_datetime(display_df['Tanggal'], format='%d/%m/%Y').max()
                start_date, end_date = st.date_input(
                    "Filter Tanggal:",
                    [min_date.date(), max_date.date()],
                    format="DD/MM/YYYY",
                    key=f"date_filter_{sector_code}"
                )
            
                # Convert to datetime for comparison
                start_date = pd.to_datetime(start_date)
                end_date = pd.to_datetime(end_date)
            
                # Apply date filter
                mask = (pd.to_datetime(display_df['Tanggal'], format='%d/%m/%Y') >= start_date) & \
                       (pd.to_datetime(display_df['Tanggal'], format='%d/%m/%Y') <= end_date)
                filtered_display_df = display_df[mask]
            
                st.dataframe(
                    filtered_display_df.style.format({
                        'Open': 'Rp {:,.2f}',
                        'High': 'Rp {:,.2f}',
                        'Low': 'Rp {:,.2f}',
                        'Close': 'Rp {:,.2f}',
                        'Volume': '{:,.0f}',
                        'Stock Num': '{:,.0f}'
                    }),
                    height=200
                )
            else:
                st.warning(f"No historical data available for {sector_name}")
