import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Krypto Kapitalfluss Dashboard", layout="wide")
st.title("📊 Ultimatives Krypto Kapitalfluss Dashboard")
st.caption("Alle Daten live und ohne Anmeldung – dein persönliches Frühwarnsystem für Bewegungen im Finanz- & Kryptomarkt")

# SECTION 0 – Sofort-Handlungsindikator
st.header("🚦 Marktampel – Handlungsempfehlung in Echtzeit")

# Anteil Coins mit negativem Trend
try:
    neg_count = df_sorted["24h Veränderung (%)"].lt(0).sum()
    total_count = len(df_sorted)
    neg_ratio = round((neg_count / total_count) * 100, 1)

    if 'risk_score' in locals():
        score = risk_score + 5
        if score >= 8 and neg_ratio > 60:
            st.error(f"📍 Marktlage: 🔴 Hohe Vorsicht
Grund: {neg_ratio}% der Coins im Minus, Makro-Risiko sehr hoch ({score}/10).")
        elif score >= 6 or neg_ratio > 40:
            st.warning(f"📍 Marktlage: 🟠 Beobachten
Grund: {neg_ratio}% der Coins im Minus, moderates Makro-Risiko ({score}/10).")
        else:
            st.success(f"📍 Marktlage: 🟢 Positiv
Grund: Nur {neg_ratio}% der Coins im Minus, Makro-Umfeld günstig ({score}/10).")
except:
    st.info("Marktampel konnte nicht berechnet werden. Prüfe Datenverfügbarkeit.")

# SECTION 1 – Portfolio Coins Marktübersicht (CoinGecko)
st.header("🪙 Dein Portfolio: Marktüberblick")
portfolio_coins = [
    "sei-network", "sui", "filecoin", "fetch-ai", "graphlinq-protocol", "the-graph",
    "ethereum", "xai", "starknet", "immutable-x", "polygon", "hedera",
    "astar", "api3", "flux", "portal", "skey-network", "near", "neurai",
    "singularitynet", "gala", "chirpley", "vulcan-forged", "kaspa", "storj",
    "yourai", "audius", "zetachain", "smooth-love-potion", "fantom", "duel-network",
    "gamerx", "red-pulse-phoenix", "neat-protocol", "supra", "slp", "phala",
    "chrap", "phb", "duel", "gmrx"
]

cg_url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    'vs_currency': 'usd',
    'ids': ','.join(portfolio_coins),
    'order': 'market_cap_desc',
    'per_page': 250,
    'page': 1,
    'sparkline': False
}
response = requests.get(cg_url, params=params)
data = response.json()

# Übersichtstabelle
st.subheader("📈 Live-Daten deiner beobachteten Coins")
coin_table = []
for coin in data:
    coin_table.append({
        "Coin": coin['name'],
        "Preis (USD)": coin['current_price'],
        "24h Veränderung (%)": coin['price_change_percentage_24h'],
        "Market Cap": coin['market_cap'],
        "Volumen (24h)": coin['total_volume']
    })
df = pd.DataFrame(coin_table)
df_sorted = df.sort_values(by="Market Cap", ascending=False)

# Farben für 24h Bewegung
st.markdown("**🟢 Grün = Kursanstieg | 🔴 Rot = Kursverlust**")
def highlight_change(val):
    if val is None:
        return ''
    color = 'green' if val > 0 else 'red'
    return f'background-color: {color}; color: white'

styled_df = df_sorted.style.applymap(highlight_change, subset=["24h Veränderung (%)"])
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# Heatmap-ähnlicher Hinweis basierend auf Makro-Risiko
if 'risk_score' in locals():
    st.markdown("### 📊 🧭 Makro-basierte Marktinterpretation")
    if risk_score + 5 >= 8:
        st.error("⚠️ Aktuell hohe makroökonomische Risiken! Defensive Coins bevorzugen (z. B. BTC, ETH, Stablecoins).")
    elif risk_score + 5 >= 6:
        st.warning("🔶 Moderate Risiken im Markt. Wachsam bleiben und bei Altcoins selektiv sein.")
    else:
        st.success("✅ Niedriges Makro-Risiko: Marktumfeld eher günstig für Risikoanlagen (z. B. Altcoins).")

# SECTION 2 – Bewertungs-Radar
st.header("📊 Fundamentale Bewertung (Radar-Modul)")
radar_table = []
for coin in data:
    try:
        volume_ratio = coin['total_volume'] / coin['market_cap'] if coin['market_cap'] else 0
        supply_ratio = coin['circulating_supply'] / coin['total_supply'] if coin['total_supply'] else 0
        radar_table.append({
            "Coin": coin['symbol'].upper(),
            "Volume/MarketCap": round(volume_ratio, 3),
            "Supply genutzt (%)": round(supply_ratio * 100, 2),
            "Preis (USD)": coin['current_price']
        })
    except:
        continue

radar_df = pd.DataFrame(radar_table)
st.dataframe(radar_df, use_container_width=True, hide_index=True)

# SECTION 3 – Makro-Indikatoren
st.header("📉 Makro-Indikatoren")
data_macro = pd.DataFrame({
    'Datum': pd.date_range(end=datetime.today(), periods=12, freq='M'),
    'FED Rate (%)': [0.25, 0.25, 0.5, 1.0, 1.75, 2.5, 3.25, 4.0, 4.5, 5.0, 5.25, 5.5],
    'CPI Inflation (%)': [1.6, 2.0, 2.5, 3.0, 4.5, 6.0, 8.0, 7.0, 6.5, 5.0, 3.5, 3.1],
    'DXY Index': [89, 90, 91, 93, 95, 97, 100, 102, 104, 106, 105, 103]
})

# Trendanalyse
def trend(values):
    if len(values) >= 2:
        return "🟢 steigend" if values.iloc[-1] > values.iloc[-2] else "🔴 fallend"
    else:
        return "⚪️ nicht genug Daten"
