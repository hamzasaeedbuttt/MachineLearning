import streamlit as st
import requests
import pandas as pd
import os
import time

# Page configuration
st.set_page_config(
    page_title="Quant Vista",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .positive-change {
        color: #2ecc71;
        font-weight: bold;
    }
    .negative-change {
        color: #e74c3c;
        font-weight: bold;
    }
    .stDataFrame {
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">📈 Quant Vista</div>', unsafe_allow_html=True)
st.write("**Get AI-powered stock recommendations ranked by predicted price increase**")

# API endpoint configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://192.168.0.202:8000")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    num_recommendations = st.slider(
        "Number of Stocks to Analyze",
        min_value=5,
        max_value=30,
        value=10,
        help="Number of stocks to analyze and get recommendations from"
    )
    
    # Show time estimate
    if num_recommendations > 0:
        est_time = num_recommendations * 12
        if est_time >= 60:
            st.info(f"⏱️ Estimated time: ~{est_time/60:.1f} minutes for {num_recommendations} stocks (API rate limit)")
        else:
            st.info(f"⏱️ Estimated time: ~{est_time} seconds for {num_recommendations} stocks")
    
    custom_symbols = st.text_input(
        "Custom Stock Symbols (Optional)",
        help="Enter comma-separated stock symbols (e.g., AAPL,MSFT,GOOGL). Leave empty for popular stocks.",
        placeholder="AAPL, MSFT, GOOGL"
    )
    
    st.markdown("---")
    st.info("💡 **How it works:**\n\n1. The system automatically fetches live data for multiple stocks\n2. Calculates technical indicators (moving averages, volatility, returns)\n3. Uses ML models to predict tomorrow's price\n4. Ranks stocks by predicted price increase\n5. Shows you the best investment opportunities")
    
    st.markdown("---")
    st.markdown("**API Status**")
    try:
        status_response = requests.get(f"{API_BASE_URL}/", timeout=2)
        if status_response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Not Available")

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("🚀 Top Stock Recommendations")

with col2:
    if st.button("🔄 Get Recommendations", type="primary", use_container_width=True):
        st.session_state.fetch_recommendations = True

# Fetch and display recommendations
if st.session_state.get('fetch_recommendations', False) or st.button("🔄 Refresh", key="refresh_btn"):
    # Calculate estimated time (12 seconds per stock for free tier API)
    estimated_seconds = num_recommendations * 12
    estimated_minutes = estimated_seconds / 60
    time_msg = f"This will take approximately {estimated_minutes:.1f} minutes ({estimated_seconds} seconds)" if estimated_seconds > 60 else f"This will take approximately {estimated_seconds} seconds"
    
    # Calculate timeout (estimated time + 60 seconds buffer, minimum 120 seconds)
    timeout_seconds = max(estimated_seconds + 60, 120)
    
    with st.spinner(f"🔄 Fetching live stock data for {num_recommendations} stocks... {time_msg}. Please wait..."):
        try:
            # Build API URL
            params = {"limit": num_recommendations}
            if custom_symbols and custom_symbols.strip():
                params["symbols"] = custom_symbols.strip()
            
            # Make API request
            response = requests.get(
                f"{API_BASE_URL}/recommendations",
                params=params,
                timeout=timeout_seconds
            )
            
            if response.status_code == 200:
                data = response.json()
                recommendations = data.get("recommendations", [])
                total_analyzed = data.get("total_analyzed", 0)
                
                if recommendations:
                    # Create DataFrame for better display
                    df_data = []
                    for i, rec in enumerate(recommendations, 1):
                        df_data.append({
                            "Rank": i,
                            "Symbol": rec["symbol"],
                            "Current Price": f"${rec['current_price']:.2f}",
                            "Predicted Price": f"${rec['predicted_price']:.2f}",
                            "Predicted Change": f"${rec['predicted_change']:.2f}",
                            "Predicted Change %": f"{rec['predicted_change_percent']:.2f}%",
                            "Direction": "📈 Up" if rec["predicted_change_percent"] > 0 else "📉 Down"
                        })
                    
                    df = pd.DataFrame(df_data)
                    
                    # Display results
                    st.success(f"✅ Analyzed {total_analyzed} stocks and found {len(recommendations)} recommendations!")
                    
                    # Display as table with styling
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Show top 3 prominently
                    if len(recommendations) >= 3:
                        st.markdown("---")
                        st.subheader("🏆 Top 3 Investment Opportunities")
                        
                        cols = st.columns(3)
                        for idx, col in enumerate(cols):
                            if idx < len(recommendations):
                                rec = recommendations[idx]
                                with col:
                                    st.metric(
                                        label=f"{rec['symbol']}",
                                        value=f"${rec['predicted_price']:.2f}",
                                        delta=f"+{rec['predicted_change_percent']:.2f}%"
                                    )
                                    st.caption(f"Current: ${rec['current_price']:.2f}")
                                    st.caption(f"Expected Gain: ${rec['predicted_change']:.2f}")
                    
                    # Store in session state
                    st.session_state.recommendations = recommendations
                    st.session_state.fetch_recommendations = False
                    
                else:
                    st.warning("⚠️ No positive predictions found. Try different stocks or check back later.")
                    
            else:
                st.error(f"❌ API Error: {response.status_code}")
                try:
                    error_detail = response.json()
                    st.error(f"Details: {error_detail.get('detail', 'Unknown error')}")
                except:
                    st.error(f"Response: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            st.error("❌ Connection Error: Could not connect to API. Make sure the API server is running at " + API_BASE_URL)
        except requests.exceptions.Timeout:
            st.error("❌ Request Timeout: The API took too long to respond. Please try again.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display cached recommendations if available
elif st.session_state.get('recommendations'):
    recommendations = st.session_state.recommendations
    
    df_data = []
    for i, rec in enumerate(recommendations[:num_recommendations], 1):
        df_data.append({
            "Rank": i,
            "Symbol": rec["symbol"],
            "Current Price": f"${rec['current_price']:.2f}",
            "Predicted Price": f"${rec['predicted_price']:.2f}",
            "Predicted Change": f"${rec['predicted_change']:.2f}",
            "Predicted Change %": f"{rec['predicted_change_percent']:.2f}%",
            "Direction": "📈 Up" if rec["predicted_change_percent"] > 0 else "📉 Down"
        })
    
    df = pd.DataFrame(df_data)
    st.info("💡 Click 'Get Recommendations' to fetch fresh data")
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.info("👆 Click the 'Get Recommendations' button above to see AI-powered stock investment recommendations!")
    
    # Show example of what to expect
    with st.expander("📋 What you'll see"):
        st.markdown("""
        The system will analyze multiple stocks and show you:
        - **Rank**: Stock ranking by predicted increase
        - **Symbol**: Stock ticker symbol
        - **Current Price**: Today's closing price
        - **Predicted Price**: Tomorrow's predicted price
        - **Predicted Change**: Expected dollar increase
        - **Predicted Change %**: Expected percentage increase
        - **Direction**: Whether price is predicted to go up or down
        
        Stocks are automatically ranked from highest to lowest predicted gain!
        """)

# Footer
st.markdown("---")
st.markdown("**Disclaimer:** This tool is for educational purposes only. Stock predictions are not guaranteed and past performance does not indicate future results. Always do your own research before investing.")
