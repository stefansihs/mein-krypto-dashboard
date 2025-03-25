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
    return "🟢 steigend" if values[-1] > values[-2] else "🔴 fallend"

trend_fed = trend(data_macro['FED Rate (%)'])
trend_cpi = trend(data_macro['CPI Inflation (%)'])
trend_dxy = trend(data_macro['DXY Index'])

st.markdown(f"**Makro-Trends:** FED: {trend_fed} | Inflation: {trend_cpi} | DXY: {trend_dxy}")

# Makro-Risiko-Skala (vereinfacht)
risk_score = 0
risk_score += 2 if data_macro['FED Rate (%)'].iloc[-1] > 4 else 0
risk_score += 2 if data_macro['DXY Index'].iloc[-1] > 102 else 0
risk_score += 1 if data_macro['CPI Inflation (%)'].iloc[-1] > 3 else 0

st.metric(label="🧠 Makro-Risiko-Score (1–10)", value=risk_score + 5)

fig = go.Figure()
fig.add_trace(go.Scatter(x=data_macro['Datum'], y=data_macro['FED Rate (%)'], name='FED Rate'))
fig.add_trace(go.Scatter(x=data_macro['Datum'], y=data_macro['CPI Inflation (%)'], name='CPI Inflation'))
fig.add_trace(go.Scatter(x=data_macro['Datum'], y=data_macro['DXY Index'], name='DXY'))
fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=350)
st.plotly_chart(fig, use_container_width=True)

# SECTION 4 – Sentiment-Modul
st.header("📊 Sentiment: Fear & Greed + Google Trends")
fng_data = requests.get("https://api.alternative.me/fng/").json()
fng_value = fng_data['data'][0]['value']
fng_text = fng_data['data'][0]['value_classification']
fng_date = datetime.fromtimestamp(int(fng_data['data'][0]['timestamp']))

st.metric(label=f"Fear & Greed Index ({fng_text})", value=fng_value, delta=f"Stand: {fng_date.strftime('%d.%m.%Y')}")

# SECTION 5 – Whale-Bewegungen (ClankApp Beispiel)
st.header("🐋 Whale-Bewegungen (ClankApp API Beispiel)")
st.info("Live-Daten via ClankApp: Transfers von >$500k auf Ethereum – nur demonstrativ")
url_clank = "https://api.clankapp.com/v2/transactions?symbol=eth&limit=5"

try:
    resp = requests.get(url_clank, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("data"):
            for tx in data["data"]:
                st.write(f"{tx['amount']} {tx['coin_symbol'].upper()} von {tx['from_label']} ➡️ {tx['to_label']} (${tx['amount_usd']:,} USD)")
        else:
            st.warning("Keine Whale-Daten verfügbar.")
    else:
        st.warning("ClankApp API ist aktuell nicht erreichbar.")
except Exception:
    st.error("Whale-Daten konnten nicht geladen werden.")

# SECTION 6 – Ereignis-Zeitleiste (manuell)
st.header("🗓️ Ereignisse")
events = pd.DataFrame({
    'Datum': ['2024-04-15', '2024-05-01', '2024-07-01'],
    'Ereignis': ['FED Meeting', 'BTC Halving', 'Ethereum Dencun Upgrade']
})
st.table(events)

# SECTION 7 – Einzel-Chart pro Coin
st.header("📈 Preisverlauf einzelner Coins (7 Tage)")

coin_names = [coin['name'] for coin in data]
selected_coin = st.selectbox("Wähle einen Coin für den Chart", coin_names)

if selected_coin:
    selected_id = next((coin['id'] for coin in data if coin['name'] == selected_coin), None)
    if selected_id:
        chart_url = f"https://api.coingecko.com/api/v3/coins/{selected_id}/market_chart"
        chart_params = {
            'vs_currency': 'usd',
            'days': '7',
            'interval': 'daily'
        }
        chart_data = requests.get(chart_url, params=chart_params).json()
        prices = chart_data.get('prices', [])
        if prices:
            dates = [datetime.fromtimestamp(p[0] / 1000).date() for p in prices]
            values = [p[1] for p in prices]
            fig_chart = go.Figure()
            fig_chart.add_trace(go.Scatter(x=dates, y=values, mode='lines', name=selected_coin))
            fig_chart.update_layout(title=f"{selected_coin} – Preisentwicklung (7 Tage)", xaxis_title='Datum', yaxis_title='USD', height=350)
            st.plotly_chart(fig_chart, use_container_width=True)
        else:
            st.warning("Keine Preisdaten gefunden.")

st.markdown("---")
st.caption("Erstellt für persönliche Marktanalyse – alle Module erweiterbar ✨")
