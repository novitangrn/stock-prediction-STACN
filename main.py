import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from pathlib import Path
from scraper import scrape_news

# Page configuration
st.set_page_config(
    page_title='Sectoral Stock Prediction Dashboard',
    page_icon='📈',
    layout='wide'
)

# Custom CSS for styling
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

# Title with styling
st.markdown("""
    <h1 style='text-align: center; color: #0066cc; margin-bottom: 2rem;'>
        📈 Prediksi Saham Sektoral dengan Model STACN
    </h1>
    """, unsafe_allow_html=True)

# Sector definitions with consistent mapping
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

# Create a single mapping for sector codes to file prefixes
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

# Historical data loading with cache
@st.cache_data
def load_historical_data(sector_prefix):
    try:
        # Construct file path based on sector prefix
        file_path = Path(f"data/{sector_prefix}_data.csv")
        
        # Read the CSV file
        df = pd.read_csv(file_path, parse_dates=['date'])
        
        # Ensure all numeric columns are float
        numeric_cols = ['open', 'high', 'low', 'close', 'stock_num', 'vol']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Sort by date to ensure correct order
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    except Exception as e:
        st.error(f"Error loading data for sector {sector_prefix}: {str(e)}")
        return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'stock_num', 'vol'])

# Generate predictions function (moved outside of submit button logic)
def generate_predictions(start_price, volatility=0.015):
    # Only generate one day prediction
    change = np.random.normal(0.002, volatility)
    new_price = start_price * (1 + change)
    return [new_price]

# Function to create prediction chart
def create_prediction_chart(future_date, prediction, sector_name):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[future_date],
        y=[prediction],
        mode='markers',
        name='Prediksi',
        marker=dict(size=12, color='#FF9900')
    ))
    
    fig.update_layout(
        title=f'Prediksi Harga - {sector_name}',
        yaxis_title='Harga',
        xaxis_title='Tanggal',
        template='plotly_white',
        height=400
    )
    
    return fig

# Function to create historical price chart
def create_historical_chart(filtered_df, sector_name):
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
            x=0.0,
            font=dict(size=18)
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
    
    return fig

# Create tabs
tabs = st.tabs(list(sectors.keys()))

# Process each sector tab
for tab, (sector_name, sector_code) in zip(tabs, sectors.items()):
    with tab:
        # Get the corresponding file prefix
        file_prefix = sector_file_mapping[sector_code]
        df = load_historical_data(file_prefix)
        
        # Create two columns for layout
        col1, col2 = st.columns([2, 1])

        # Left panel - News and Prediction
        with col1:
            st.markdown(f"### 📰 Input Berita & Prediksi - {sector_name}")
            
            with st.form(f"prediction_form_{sector_code}"):
                news_date = st.date_input("Tanggal Berita", value=date.today(), key=f"date_{sector_code}")
                
                st.markdown("##### Judul Berita Hari Ini")
                
                # Initialize session state for scraped news if not exists
                if f"scraped_news_{sector_code}" not in st.session_state:
                    st.session_state[f"scraped_news_{sector_code}"] = ""
                
                # Display text area with current value from session state
                news_titles = st.text_area(
                    "Masukkan 5 Judul Berita", 
                    height=150, 
                    placeholder="Masukkan 5 Judul Berita atau klik 'Scrape Berita'",
                    key=f"news_{sector_code}",
                    value=st.session_state[f"scraped_news_{sector_code}"]
                )
                
                # Scraper button
                scrape_button = st.form_submit_button("Scrape Berita")
                if scrape_button:
                    with st.spinner('Mengambil berita terbaru...'):
                        try:
                            scraped_titles = scrape_news(news_date)
                            if scraped_titles:
                                # Store scraped titles in a different session state key
                                st.session_state[f"scraped_news_{sector_code}"] = "\n".join(scraped_titles)
                                st.rerun()
                            else:
                                st.warning("Tidak ada berita yang ditemukan untuk tanggal ini")
                        except Exception as e:
                            st.error(f"Error saat scraping berita: {str(e)}")
                
                # Prediction button - No slider, just button for one day prediction
                submit_button = st.form_submit_button("Prediksi Harga Saham (1 Hari)")
                if submit_button:
                    with st.spinner('Melakukan prediksi...'):
                        # Get the last closing price from data or use placeholder
                        last_price = df['close'].iloc[-1] if not df.empty else 100
                        
                        # Generate prediction for a single day
                        prediction = generate_predictions(last_price)[0]
                        future_date = (date.today() + timedelta(days=1)).strftime('%d %b')
                        
                        st.success(f"Prediksi untuk besok ({future_date}) berhasil!")
                        
                        # Create and display prediction chart
                        fig2 = create_prediction_chart(future_date, prediction, sector_name)
                        st.plotly_chart(fig2, use_container_width=True)
                        
                        # Display detailed prediction result
                        st.markdown("##### Hasil Prediksi Detail:")
                        
                        # Calculate change percentage
                        change = ((prediction - last_price) / last_price) * 100
                        
                        # Display prediction card
                        st.markdown(f"""
                        <div class="prediction-card">
                            <h6>{future_date}</h6>
                            <p style="font-size: 1.2rem; font-weight: bold">Rp {prediction:.2f} 
                            <span style="color: {'green' if change >= 0 else 'red'};">
                                {'↑' if change >= 0 else '↓'} {abs(change):.2f}%
                            </span></p>
                        </div>
                        """, unsafe_allow_html=True)

        # Right panel - Historical Analysis
        with col2:
            st.markdown(f"### 📊 Analisis Data Historis - {sector_name}")

            # Metric cards
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
                        st.metric("Performa YTD", f"{ytd_change:.2f}%", delta=f"{ytd_change:.2f}%")
                    else:
                        st.metric("Performa YTD", "N/A", "0%")
                else:
                    st.metric("Performa YTD", "N/A", "0%")
            
            # Historical chart section
            if not df.empty:
                # Time range selection
                time_range = st.selectbox(
                    "Rentang Waktu",
                    options=["1 Minggu", "1 Bulan", "3 Bulan", "All Time"],
                    index=1,
                    key=f"timerange_{sector_code}"
                )
            
                # Define time ranges
                ranges = {
                    "1 Minggu": 7,
                    "1 Bulan": 30,
                    "3 Bulan": 90,
                    "All Time": len(df)
                }
            
                # Ensure date is datetime and sorted
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date').reset_index(drop=True)
            
                # Filter data based on selected time range
                filtered_df = df.tail(ranges[time_range])
            
                # Create and display historical chart
                fig = create_historical_chart(filtered_df, sector_name)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Tidak ada data untuk ditampilkan dalam grafik")
            
            # Historical data table section
            st.markdown("##### Data Historis Detail")
            if not df.empty:
                try:
                    # Prepare display dataframe
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
            
                    # Date range filter
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
            
                    # Display formatted dataframe
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
                except ValueError as ve:
                    st.error(f"Terjadi kesalahan saat memproses data: {ve}")
                except Exception as e:
                    st.error(f"Kesalahan tak terduga: {e}")
            else:
                st.warning(f"Tidak ada data historis untuk {sector_name}")
