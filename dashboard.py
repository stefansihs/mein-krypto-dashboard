import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Krypto Kapitalfluss Dashboard", layout="wide")
st.title("📊 Ultimatives Krypto Kapitalfluss Dashboard")
st.caption("Alle Daten live und ohne Anmeldung – dein persönliches Frühwarnsystem für Bewegungen im Finanz- & Kryptomarkt")

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

cg_url = "https://api.coingecko.com/api/v3/simple/price"
params = {
    'ids': ','.join(portfolio_coins),
    'vs_currencies': 'usd',
    'include_market_cap': 'true',
    'include_24hr_vol': 'true',
    'include_24hr_change': 'true'
}
response = requests.get(cg_url, params=params)
data = response.json()

st.subheader("📈 Live-Daten deiner beobachteten Coins")
coin_table = []
for coin, info in data.items():
    coin_table.append({
        "Coin": coin.replace('-', ' ').title(),
        "Preis (USD)": info.get("usd", 0),
        "24h Veränderung (%)": info.get("usd_24hr_change", 0),
        "Marktkapitalisierung": info.get("usd_market_cap", 0),
        "Volumen (24h)": info.get("usd_24hr_vol", 0)
    })
df = pd.DataFrame(coin_table)
df_sorted = df.sort_values(by="Marktkapitalisierung", ascending=False)
st.dataframe(df_sorted, use_container_width=True, hide_index=True)

# SECTION 2 – Makro-Indikatoren (FRED via Beispiel-CSV)
st.header("📉 Makro-Indikatoren")
data_macro = pd.DataFrame({
    'Datum': pd.date_range(end=datetime.today(), periods=12, freq='M'),
    'FED Rate (%)': [0.25, 0.25, 0.5, 1.0, 1.75, 2.5, 3.25, 4.0, 4.5, 5.0, 5.25, 5.5],
    'CPI Inflation (%)': [1.6, 2.0, 2.5, 3.0, 4.5, 6.0, 8.0, 7.0, 6.5, 5.0, 3.5, 3.1],
    'DXY Index': [89, 90, 91, 93, 95, 97, 100, 102, 104, 106, 105, 103]
})
fig = go.Figure()
fig.add_trace(go.Scatter(x=data_macro['Datum'], y=data_macro['FED Rate (%)'], name='FED Rate'))
fig.add_trace(go.Scatter(x=data_macro['Datum'], y=data_macro['CPI Inflation (%)'], name='CPI Inflation'))
fig.add_trace(go.Scatter(x=data_macro['Datum'], y=data_macro['DXY Index'], name='DXY'))
fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=350)
st.plotly_chart(fig, use_container_width=True)

# SECTION 3 – Sentiment-Modul
st.header("📊 Sentiment: Fear & Greed + Google Trends")
fng_data = requests.get("https://api.alternative.me/fng/").json()
fng_value = fng_data['data'][0]['value']
fng_text = fng_data['data'][0]['value_classification']
fng_date = datetime.fromtimestamp(int(fng_data['data'][0]['timestamp']))

st.metric(label=f"Fear & Greed Index ({fng_text})", value=fng_value, delta=f"Stand: {fng_date.strftime('%d.%m.%Y')}")

# SECTION 4 – Whale-Bewegungen (ClankApp Beispiel)
st.header("🐋 Whale-Bewegungen (ClankApp API Beispiel)")
st.info("Live-Daten via ClankApp: Transfers von >$500k auf Ethereum – nur demonstrativ")
url_clank = "https://api.clankapp.com/v2/transactions?symbol=eth&limit=5"
resp = requests.get(url_clank).json()
for tx in resp.get("data", []):
    st.write(f"{tx['amount']} {tx['coin_symbol'].upper()} von {tx['from_label']} ➡️ {tx['to_label']} (${tx['amount_usd']:,} USD)")

# SECTION 5 – Ereignis-Zeitleiste (manuell)
st.header("🗓️ Ereignisse")
events = pd.DataFrame({
    'Datum': ['2024-04-15', '2024-05-01', '2024-07-01'],
    'Ereignis': ['FED Meeting', 'BTC Halving', 'Ethereum Dencun Upgrade']
})
st.table(events)

st.markdown("---")
st.caption("Erstellt für persönliche Marktanalyse – alle Module erweiterbar ✨")
