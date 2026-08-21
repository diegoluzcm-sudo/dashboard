from __future__ import annotations

import io
import re
from datetime import date, datetime, timedelta
from urllib.parse import parse_qs, urlparse

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Performance Comercial", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# Reexecuta o app automaticamente para buscar alterações das planilhas sem interação manual.
AUTO_REFRESH_MS = 5 * 60 * 1000
refresh_tick = st_autorefresh(interval=AUTO_REFRESH_MS, limit=None, key="planilhas_auto_refresh")

# -----------------------------
# Configuração das fontes
# -----------------------------
SALES_URL = "https://docs.google.com/spreadsheets/d/1xW1VZ1Mew3h35rSRmwum0E85zu4ylVcglO4eKrbrAJA/edit?usp=sharing"
CYCLE_URL = "https://docs.google.com/spreadsheets/d/1U4RW4Ooi6ko-Db7dOgpdWJXFo_XnNp8CKVONA0lUwjU/edit?usp=sharing"
PRE_URL = "https://docs.google.com/spreadsheets/d/1FnoxE7PC1TVNcnI_Vju97yhFB2uj1qnxgmVwAbRGcAk/edit?usp=sharing"
SALES_GIDS = {"Agosto/26": "401481319", "Julho/26": "0", "Junho/26": "0"}
CYCLE_GID = "1402401272"
CYCLE_DASHBOARD_GID = "377925676"
PRE_GID = "0"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{--bg:#080b12;--panel:#111722;--line:#263244;--text:#f5f7fb;--muted:#8793a8;--green:#2ed47a;--yellow:#f5bd3d;--red:#ff5a67;--blue:#5b8cff}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}.stApp{background:radial-gradient(circle at 90% -10%,rgba(91,140,255,.13),transparent 32%),var(--bg);color:var(--text)}[data-testid="stHeader"]{background:transparent}.block-container{max-width:1500px;padding:1.5rem 2rem 1rem}h1,h2,h3{font-family:'Space Grotesk',sans-serif!important;color:var(--text)!important}.section-kicker{color:var(--blue);font-size:.7rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;margin-top:1.25rem}.hero-subtitle,p,label{color:var(--muted)!important}.metric-card,.panel{background:linear-gradient(145deg,rgba(24,33,48,.98),rgba(14,20,31,.98));border:1px solid rgba(122,144,180,.18);border-radius:15px;box-shadow:0 14px 38px rgba(0,0,0,.18)}.metric-card{padding:1rem;min-height:120px}.metric-label{color:var(--muted);font-size:.75rem;font-weight:600}.metric-value{font-family:'Space Grotesk';font-size:1.45rem;font-weight:700;color:var(--text);margin-top:.5rem}.metric-note{font-size:.73rem;margin-top:.35rem}.positive{color:var(--green)}.warning{color:var(--yellow)}.critical{color:var(--red)}.panel{padding:1rem}.panel-title{font-family:'Space Grotesk';font-weight:600;color:var(--text);font-size:1.05rem}.panel-caption{font-size:.76rem;color:var(--muted)}.progress-shell{background:#293447;border-radius:99px;height:9px;overflow:hidden;margin-top:.6rem}.progress-bar{height:100%;background:linear-gradient(90deg,var(--blue),#70a1ff);border-radius:99px;animation:grow 1.2s ease-out}@keyframes grow{from{width:0}}.footer{text-align:center;color:#657188;font-size:.72rem;border-top:1px solid rgba(122,144,180,.12);padding-top:1rem;margin-top:1.8rem}.tv-shell{height:calc(100vh - 2.2rem);display:flex;flex-direction:column;justify-content:space-between;overflow:hidden}.tv-shell .section-kicker{margin-top:.35rem}.tv-shell .panel{padding:.65rem}.tv-shell .panel-title{font-size:.92rem}.tv-shell .panel-caption{font-size:.68rem}.tv-shell .stPlotlyChart{margin:0}.tv-shell [data-testid='stDataFrame']{max-height:250px}.tv-shell [data-testid='stButton']{margin-top:.25rem}.tv-topbar{display:flex;align-items:center;justify-content:space-between;margin-bottom:.6rem}.tv-title{font-family:'Space Grotesk';font-size:1.8rem;font-weight:700;color:var(--text)}.tv-subtitle{color:var(--muted);font-size:.85rem}.tv-badge{border:1px solid rgba(91,140,255,.45);color:#9bb7ff;border-radius:99px;padding:.35rem .7rem;font-size:.75rem;font-weight:700}.tv-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.55rem}.tv-grid.two{grid-template-columns:repeat(2,1fr)}.tv-card{background:linear-gradient(145deg,rgba(24,33,48,.98),rgba(14,20,31,.98));border:1px solid rgba(122,144,180,.18);border-radius:15px;padding:.75rem;min-height:92px}.tv-card .metric-value{font-size:1.55rem;margin-top:.25rem}.tv-card .metric-note{font-size:.65rem}.tv-card .metric-label{font-size:.68rem}.tv-footer{display:flex;justify-content:space-between;align-items:center;color:#657188;font-size:.75rem;margin-top:.45rem;padding-top:.45rem;border-top:1px solid rgba(122,144,180,.12)}.tv-exit{position:fixed;right:1.2rem;top:.8rem;z-index:99999;background:#ff5a67;color:#fff!important;text-decoration:none!important;border-radius:999px;padding:.55rem 1rem;font-weight:700;font-size:.8rem;box-shadow:0 5px 18px rgba(0,0,0,.35)}.tv-exit:hover{background:#ff7882}body:has(.tv-mode-marker) [data-testid='stSidebar'],body:has(.tv-mode-marker) [data-testid='stHeader']{display:none}body:has(.tv-mode-marker),body:has(.tv-mode-marker) .stApp{overflow:hidden;height:100vh}body:has(.tv-mode-marker) .block-container{max-width:1800px;height:100vh;overflow:hidden;padding:.65rem 1rem}body:has(.tv-mode-marker) [data-testid='stPlotlyChart']{margin:0}body:has(.tv-mode-marker) [data-testid='stDataFrame']{max-height:250px}.tv-table{font-size:1rem}@media(max-width:1000px){.tv-grid{grid-template-columns:repeat(2,1fr)}.tv-title{font-size:1.35rem}}
</style>
""", unsafe_allow_html=True)


def sheet_csv_url(sheet_url: str, gid: str) -> str:
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", sheet_url)
    if not match:
        raise ValueError("Link do Google Sheets inválido")
    return f"https://docs.google.com/spreadsheets/d/{match.group(1)}/export?format=csv&gid={gid}"


@st.cache_data(ttl=300, show_spinner=False)
def read_raw_sheet(sheet_url: str, gid: str, refresh_key: int = 0) -> pd.DataFrame:
    return pd.read_csv(sheet_csv_url(sheet_url, gid), header=None, dtype=str, keep_default_na=False)


def read_uploaded(upload):
    if upload is None:
        return None
    content = upload.getvalue()
    if upload.name.lower().endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(content), header=None, dtype=str).fillna("")
    return pd.read_csv(io.BytesIO(content), header=None, dtype=str, keep_default_na=False)


def money(value) -> float:
    if value is None:
        return 0.0
    text = str(value).strip().replace("R$", "").replace(" ", "")
    if not text or text in {"-", "nan", "NaN"}:
        return 0.0
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        return float(re.sub(r"[^0-9.-]", "", text) or 0)
    except ValueError:
        return 0.0


def normalize_name(value: str) -> str:
    text = re.sub(r"[^a-z0-9]", "", str(value).lower().replace("á", "a").replace("ã", "a").replace("â", "a").replace("é", "e").replace("ê", "e").replace("í", "i").replace("ó", "o").replace("ô", "o").replace("ú", "u"))
    if text in {"santana", "santanna", "santanna"}:
        return "Sant'Anna"
    return str(value).strip()


def find_col(columns, terms):
    for col in columns:
        norm = re.sub(r"[^a-z0-9]", "", str(col).lower().replace("á", "a").replace("ã", "a").replace("â", "a").replace("é", "e").replace("ê", "e").replace("í", "i").replace("ó", "o").replace("ô", "o").replace("ú", "u"))
        if all(str(term).lower() in norm for term in terms):
            return col
    return None


def parse_date_series(series):
    return pd.to_datetime(series, dayfirst=True, errors="coerce")


def parse_sales(raw: pd.DataFrame):
    # A planilha de vendas possui blocos de indicadores no topo e a tabela abaixo.
    header_idx = None
    for i in range(min(80, len(raw))):
        values = " ".join(str(x).lower() for x in raw.iloc[i].tolist())
        if "nome" in values and "closer" in values and ("hunter" in values or "sdr" in values):
            header_idx = i
            break
    result = pd.DataFrame()
    meta = {"recebido": 0.0, "contrato_total": 0.0, "falta_meta": 0.0, "falta_super": 0.0, "ating_meta": 0.0, "ating_super": 0.0}
    for i in range(min(35, len(raw))):
        row = " | ".join(str(x) for x in raw.iloc[i].tolist())
        low = row.lower()
        nums = [money(x) for x in raw.iloc[i].tolist() if money(x)]
        if "valor recebido" in low and nums:
            meta["recebido"] = nums[0]
        if "valor de contrato (meta)" in low and nums:
            meta["contrato_total"] = nums[0]
        if "quanto falta pra super meta" in low and nums:
            meta["falta_super"] = nums[0]
        elif "quanto falta pra meta" in low and nums:
            meta["falta_meta"] = nums[0]
        if "quanto atingimos da super meta" in low and nums:
            meta["ating_super"] = nums[0]
        elif "quanto atingimos da meta" in low and nums:
            meta["ating_meta"] = nums[0]
    if header_idx is None:
        return result, meta
    headers = [str(x).strip() or f"col_{j}" for j, x in enumerate(raw.iloc[header_idx].tolist())]
    data = raw.iloc[header_idx + 1:].copy()
    data.columns = headers
    data = data.loc[data[headers[0]].astype(str).str.strip().ne("")].copy()
    nome = find_col(data.columns, ["nome"])
    closer = find_col(data.columns, ["closer"])
    hunter = find_col(data.columns, ["hunter"]) or find_col(data.columns, ["sdr"])
    valor = find_col(data.columns, ["valor", "meta"]) or find_col(data.columns, ["contrato"])
    liquido = find_col(data.columns, ["valor", "liquido"])
    data_col = find_col(data.columns, ["data"]) or find_col(data.columns, ["inicio"])
    venda_col = find_col(data.columns, ["venda", "feita"]) or find_col(data.columns, ["status"])
    if nome:
        result["Lead"] = data[nome].astype(str).str.strip()
    else:
        result["Lead"] = data.iloc[:, 0].astype(str).str.strip()
    result["Closer"] = data[closer].map(normalize_name) if closer else ""
    result["SDR"] = data[hunter].map(normalize_name) if hunter else ""
    result["Valor Contrato"] = data[valor].map(money) if valor else 0.0
    result["Valor Líquido"] = data[liquido].map(money) if liquido else 0.0
    result["Data"] = parse_date_series(data[data_col]) if data_col else pd.NaT
    if venda_col:
        flag = data[venda_col].astype(str).str.strip().str.lower().isin(["true", "verdadeiro", "sim", "1", "x", "yes"])
        result = result[flag.to_numpy()]
    result = result[(result["Lead"] != "") & ((result["Valor Contrato"] > 0) | (result["Valor Líquido"] > 0))].copy()
    # A mesma venda pode ocupar várias linhas (por exemplo, MRR e One Time).
    # Conta-se um único Lead, somando-se os valores das linhas do mesmo contrato.
    if not result.empty:
        result = result.groupby(["Lead", "Closer", "SDR"], dropna=False, as_index=False).agg({"Valor Contrato": "sum", "Valor Líquido": "sum", "Data": "min"})
    if meta["recebido"] == 0 and not result.empty:
        meta["recebido"] = result["Valor Líquido"].sum()
    if meta["contrato_total"] == 0 and not result.empty:
        meta["contrato_total"] = result["Valor Contrato"].sum()
    return result.reset_index(drop=True), meta


def parse_cycle(raw: pd.DataFrame):
    header = None
    for i in range(min(20, len(raw))):
        if "Lead" in raw.iloc[i].tolist() and "SDR" in raw.iloc[i].tolist():
            header = i
            break
    if header is None:
        return pd.DataFrame()
    df = raw.iloc[header + 1:].copy()
    df.columns = [str(x).strip() or f"col_{j}" for j, x in enumerate(raw.iloc[header].tolist())]
    df = df.rename(columns={next((c for c in df.columns if normalize_name(c) == "lead"), df.columns[0]): "Lead"})
    rename = {}
    for col in df.columns:
        low = str(col).strip().lower()
        n = normalize_name(col)
        if n == "sdr": rename[col] = "SDR"
        elif n == "closer": rename[col] = "Closer"
        elif "data" in low and "entrada" in low: rename[col] = "Data Entrada"
        elif "data" in low and ("primeiro contato" in low or "contato" in low): rename[col] = "Data Contato"
        elif "data" in low and "reuni" in low: rename[col] = "Data Reunião"
        elif "data" in low and "fech" in low: rename[col] = "Data Fechamento"
    df = df.rename(columns=rename)
    for col in ["Data Entrada", "Data Contato", "Data Reunião", "Data Fechamento"]:
        if col not in df: df[col] = pd.NaT
        else: df[col] = parse_date_series(df[col])
    for col in ["SDR", "Closer"]:
        if col in df: df[col] = df[col].map(normalize_name)
    return df[df["Lead"].astype(str).str.strip().ne("")].copy()


def parse_cycle_dashboard(raw: pd.DataFrame):
    """Lê a aba Dashboard do ciclo como fonte oficial de contrato e líquido por venda."""
    if raw.empty:
        return pd.DataFrame(columns=["Lead", "Closer", "SDR", "Valor Contrato", "Valor Líquido", "Data"])
    header = None
    for i in range(min(20, len(raw))):
        values = [str(v).strip().lower() for v in raw.iloc[i].tolist()]
        if any("lead" in normalize_name(v) for v in values) and any("closer" in normalize_name(v) for v in values):
            header = i
            break
    if header is None:
        return pd.DataFrame(columns=["Lead", "Closer", "SDR", "Valor Contrato", "Valor Líquido", "Data"])
    df = raw.iloc[header + 1:].copy()
    df.columns = [str(x).strip() or f"col_{j}" for j, x in enumerate(raw.iloc[header].tolist())]
    lead_col = next((c for c in df.columns if str(normalize_name(c)).strip().lower() == "lead"), df.columns[0])
    closer_col = next((c for c in df.columns if str(normalize_name(c)).strip().lower() == "closer"), None)
    sdr_col = next((c for c in df.columns if str(normalize_name(c)).strip().lower() == "sdr"), None)
    contrato_col = next((c for c in df.columns if ("valor" in str(c).lower() and ("contrato" in str(c).lower() or "meta" in str(c).lower()))), None)
    liquido_col = next((c for c in df.columns if "valor" in str(c).lower() and "liquido" in str(c).lower()), None)
    data_col = next((c for c in df.columns if "data" in str(c).lower() and ("fechamento" in str(c).lower() or "fech" in str(c).lower())), None)
    result = pd.DataFrame({
        "Lead": df[lead_col].astype(str).str.strip(),
        "Closer": df[closer_col].map(normalize_name) if closer_col else "",
        "SDR": df[sdr_col].map(normalize_name) if sdr_col else "",
        "Valor Contrato": df[contrato_col].map(money) if contrato_col else 0.0,
        "Valor Líquido": df[liquido_col].map(money) if liquido_col else 0.0,
        "Data": parse_date_series(df[data_col]) if data_col else pd.NaT,
    })
    result = result[(result["Lead"] != "") & ((result["Valor Contrato"] > 0) | (result["Valor Líquido"] > 0))].copy()
    if result.empty:
        return result
    # Cada Lead representa uma venda única; múltiplas linhas de contrato são consolidadas.
    return result.groupby("Lead", as_index=False).agg({"Closer": "first", "SDR": "first", "Valor Contrato": "sum", "Valor Líquido": "sum", "Data": "min"})


def parse_pre_vendas(raw: pd.DataFrame):
    # Bloco geral: a primeira coluna contém a data e B:I os totais do time.
    rows = []
    for i in range(len(raw)):
        dt = pd.to_datetime(raw.iloc[i, 0], dayfirst=True, errors="coerce")
        if pd.notna(dt):
            vals = [money(raw.iloc[i, j]) for j in range(1, min(9, raw.shape[1]))]
            while len(vals) < 8: vals.append(0.0)
            rows.append([dt] + vals[:8])
    daily = pd.DataFrame(rows, columns=["Data", "Discadas", "Contatadas", "Agendadas", "Leads Reciclados", "Remarcadas", "Realizadas", "No-show", "Vendas"])
    # Blocos de SDRs: detecta os nomes no primeiro cabeçalho e soma as colunas de Realizadas/No-show/Venda.
    sdr_names = ["William", "Barbara", "Vitória"]
    sdr_rows = []
    for name in sdr_names:
        positions = [j for j, v in enumerate(raw.iloc[0].tolist()) if normalize_name(v) == name]
        if not positions: continue
        start = positions[0]
        end = positions[1] if len(positions) > 1 else raw.shape[1]
        header_values = [re.sub(r"[^a-z0-9]", "", str(v).lower().replace("á", "a").replace("ã", "a").replace("í", "i").replace("ó", "o")) for v in raw.iloc[1, start:end].tolist()]
        def pos(term):
            return next((start + k for k, v in enumerate(header_values) if term in v), None)
        rcol, ncol, vcol = pos("realizadas"), pos("noshow"), pos("venda")
        if rcol is None: continue
        for i in range(2, len(raw)):
            dt = pd.to_datetime(raw.iloc[i, 0], dayfirst=True, errors="coerce")
            if pd.notna(dt):
                sdr_rows.append({"Data": dt, "Nome": name, "Realizadas": money(raw.iloc[i, rcol]), "No-show": money(raw.iloc[i, ncol]) if ncol else 0, "Vendas": money(raw.iloc[i, vcol]) if vcol else 0})
    return daily, pd.DataFrame(sdr_rows)


def brl(v):
    return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def card(label, value, note, tone=""):
    st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-note {tone}'>{note}</div></div>", unsafe_allow_html=True)


def fig_theme(fig, height=330):
    fig.update_layout(template="plotly_dark", height=height, margin=dict(l=10,r=10,t=35,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="DM Sans", color="#dbe4f3", size=11), xaxis=dict(gridcolor="#263244"), yaxis=dict(gridcolor="#263244"))
    return fig


def tv_card(label, value, note="", tone=""):
    return f"<div class='tv-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-note {tone}'>{note}</div></div>"


def tv_rotation(seconds, screen, total_screens):
    components.html(f"""
    <script>
    const delay = {int(seconds)} * 1000;
    setTimeout(() => {{
      const parentWindow = window.parent;
      const url = new URL(parentWindow.location.href);
      const current = Number(url.searchParams.get('tv_screen') || '{screen}');
      url.searchParams.set('tv', '1');
      url.searchParams.set('tv_screen', String((current + 1) % {total_screens}));
      parentWindow.location.href = url.toString();
    }}, delay);
    </script>
    """, height=0)


def render_tv_mode(screen, seconds, inicio, fim, contrato, meta_valor, percentual_meta, recebido, falta_meta, falta_super, funil, sdr_rank, closer_rank, daily_filtered):
    total_screens = 6
    rotation_tick = st_autorefresh(interval=max(1, int(seconds)) * 1000, limit=None, key="tv_rotation_refresh")
    screen = (screen + int(rotation_tick or 0)) % total_screens
    periodo_label = f"{inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}"
    st.markdown("<div class='tv-mode-marker'></div>", unsafe_allow_html=True)
    st.markdown("<a class='tv-exit' href='?tv=0' target='_self'>Sair do Modo TV</a>", unsafe_allow_html=True)
    with st.container():
        st.markdown(f"<div class='tv-topbar'><div><div class='tv-title'>Performance Comercial</div><div class='tv-subtitle'>Modo TV · {periodo_label}</div></div><div class='tv-badge'>TELA {screen + 1}/{total_screens} · PRÓXIMA EM {seconds}s</div></div>", unsafe_allow_html=True)
        if screen == 0:
            st.markdown("<div class='section-kicker'>01 · Resultado financeiro</div>", unsafe_allow_html=True)
            st.markdown("<div class='tv-grid'>" + tv_card("Valor de Contrato", brl(contrato), "Fonte: aba Dashboard", "positive") + tv_card("Meta", brl(meta_valor), "Objetivo do período", "warning") + tv_card("% da Meta Atingida", f"{percentual_meta:.2f}%", f"{brl(contrato)} de {brl(meta_valor)}", "warning") + tv_card("Valor Recebido", brl(recebido), "Valor líquido", "positive") + "</div>", unsafe_allow_html=True)
        elif screen == 1:
            st.markdown("<div class='section-kicker'>02 · Saldos e progresso</div>", unsafe_allow_html=True)
            st.markdown("<div class='tv-grid two'>" + tv_card("Falta pra Meta", brl(falta_meta), "Saldo restante", "warning") + tv_card("Falta pra Super Meta", brl(falta_super), "Cenário stretch", "critical") + "</div>", unsafe_allow_html=True)
            progress = min(max(percentual_meta, 0), 100)
            st.markdown(f"<div class='panel' style='margin-top:.8rem'><div class='panel-title'>Progresso da meta</div><div class='progress-shell'><div class='progress-bar' style='width:{progress:.2f}%'></div></div><div class='panel-caption' style='margin-top:.5rem'>{percentual_meta:.2f}% atingido no período selecionado.</div></div>", unsafe_allow_html=True)
        elif screen == 2:
            st.markdown("<div class='section-kicker'>03 · Funil comercial</div>", unsafe_allow_html=True)
            ff = go.Figure(go.Funnel(y=funil["Etapa"], x=funil["Quantidade"], textinfo="value+percent initial", marker=dict(color=["#5b8cff","#7da4ff","#f5bd3d","#70a1ff","#ff5a67","#2ed47a"])))
            fig_theme(ff, 285)
            st.plotly_chart(ff, use_container_width=True, config={"displayModeBar": False})
        elif screen == 3:
            st.markdown("<div class='section-kicker'>04 · Pré-vendas</div>", unsafe_allow_html=True)
            st.markdown("<div class='panel'><div class='panel-title'>Vendas e reuniões realizadas por SDR</div><div class='panel-caption'>Fonte oficial: planilha de Pré Vendas · William, Barbara e Vitoria.</div>", unsafe_allow_html=True)
            st.dataframe(sdr_rank[["Nome", "Vendas", "Realizadas", "No-show", "Taxa Conversão"]].sort_values("Vendas", ascending=False), hide_index=True, use_container_width=True, height=250)
            st.markdown("</div>", unsafe_allow_html=True)
        elif screen == 4:
            st.markdown("<div class='section-kicker'>05 · Closers</div>", unsafe_allow_html=True)
            st.markdown("<div class='panel'><div class='panel-title'>Ranking financeiro por Closer</div><div class='panel-caption'>Vendas únicas por Lead · fonte oficial: aba Dashboard.</div>", unsafe_allow_html=True)
            closer_display = closer_rank[["Nome", "Vendas", "Valor", "Líquido"]].sort_values("Valor", ascending=False).copy()
            if not closer_display.empty:
                closer_display["Valor"] = closer_display["Valor"].map(brl)
                closer_display["Líquido"] = closer_display["Líquido"].map(brl)
            st.dataframe(closer_display, hide_index=True, use_container_width=True, height=250)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='section-kicker'>06 · Acompanhamento operacional</div>", unsafe_allow_html=True)
            st.markdown("<div class='tv-grid'>" + tv_card("Discadas", int(funil.loc[funil["Etapa"] == "Discadas", "Quantidade"].sum()), "Atividades do período", "positive") + tv_card("Contatadas", int(funil.loc[funil["Etapa"] == "Contatadas", "Quantidade"].sum()), "Leads contatados", "positive") + tv_card("Agendadas", int(funil.loc[funil["Etapa"] == "Agendadas", "Quantidade"].sum()), "Reuniões marcadas", "warning") + tv_card("Realizadas", int(funil.loc[funil["Etapa"] == "Realizadas", "Quantidade"].sum()), "Reuniões concluídas", "positive") + tv_card("No-show", int(funil.loc[funil["Etapa"] == "No-show", "Quantidade"].sum()), "Reuniões não realizadas", "critical") + tv_card("Vendas", int(funil.loc[funil["Etapa"] == "Vendas", "Quantidade"].sum()), "Fechamentos no período", "positive") + "</div>", unsafe_allow_html=True)
            st.markdown("<div class='panel' style='margin-top:.8rem'><div class='panel-title'>Ofertas pendentes / Risco Zero</div><div class='panel-caption'>Valores pendentes permanecem separados da meta até confirmação do pagamento.</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='tv-footer'><span>Atualização automática a cada {seconds} segundos</span><span>Sem rolagem · tela {screen + 1} de {total_screens}</span></div>", unsafe_allow_html=True)


# -----------------------------
# Sidebar: fontes, metas e período
# -----------------------------
st.sidebar.title("Controle do dashboard")
st.sidebar.caption("Os dados são verificados automaticamente a cada 5 minutos, sem depender de novas solicitações.")
periodo = st.sidebar.selectbox("Período", ["Hoje", "Últimos 7 dias", "Mês atual", "Últimos 3 meses", "Últimos 6 meses", "Personalizado"], index=2)
hoje = pd.Timestamp.today().normalize()
if periodo == "Hoje": inicio, fim = hoje, hoje
elif periodo == "Últimos 7 dias": inicio, fim = hoje - pd.Timedelta(days=6), hoje
elif periodo == "Mês atual": inicio, fim = hoje.replace(day=1), hoje
elif periodo == "Últimos 3 meses": inicio, fim = hoje - pd.DateOffset(months=3), hoje
elif periodo == "Últimos 6 meses": inicio, fim = hoje - pd.DateOffset(months=6), hoje
else:
    inicio = pd.Timestamp(st.sidebar.date_input("Data inicial", (hoje - pd.Timedelta(days=30)).date()))
    fim = pd.Timestamp(st.sidebar.date_input("Data final", hoje.date()))
st.sidebar.divider()
st.sidebar.subheader("Metas do período")
meta_valor_manual = st.sidebar.number_input("Meta de valor de contrato", min_value=0.0, value=425000.0, step=1000.0)
meta_super_manual = st.sidebar.number_input("Super meta de valor", min_value=0.0, value=500000.0, step=1000.0)
meta_vendas = st.sidebar.number_input("Meta de vendas", min_value=0, value=10, step=1)
meta_realizadas = st.sidebar.number_input("Meta de reuniões realizadas", min_value=0, value=54, step=1)
st.sidebar.divider()
st.sidebar.subheader("Fontes conectadas")
sales_url = st.sidebar.text_input("Planilha permanente de vendas", SALES_URL)
sales_month = st.sidebar.selectbox("Aba de vendas", list(SALES_GIDS.keys()), index=0)
sales_upload = st.sidebar.file_uploader("Substituir vendas por CSV/Excel", type=["csv", "xlsx"], key="sales_upload")
cycle_url = st.sidebar.text_input("Planilha do ciclo de vendas", CYCLE_URL)
cycle_upload = st.sidebar.file_uploader("Substituir ciclo por CSV/Excel", type=["csv", "xlsx"], key="cycle_upload")
pre_url = st.sidebar.text_input("Planilha de realizadas dos SDRs", PRE_URL)
pre_upload = st.sidebar.file_uploader("Substituir realizadas por CSV/Excel", type=["csv", "xlsx"], key="pre_upload")
st.sidebar.divider()
st.sidebar.subheader("Apresentação")
tv_seconds = st.sidebar.number_input("Trocar tela a cada (segundos)", min_value=5, max_value=300, value=20, step=5)
if st.sidebar.button("Abrir Modo TV", type="primary", use_container_width=True):
    st.session_state["tv_active"] = True
    st.query_params["tv"] = "1"
    st.query_params["tv_screen"] = "0"
    st.rerun()

# -----------------------------
# Ingestão
# -----------------------------
errors = []
try:
    raw_sales = read_uploaded(sales_upload) if sales_upload else read_raw_sheet(sales_url, SALES_GIDS[sales_month], refresh_tick)
    sales, sheet_meta = parse_sales(raw_sales)
except Exception as exc:
    sales, sheet_meta = pd.DataFrame(), {"recebido": 0, "contrato_total": 0, "falta_meta": 0, "falta_super": 0, "ating_meta": 0, "ating_super": 0}
    errors.append(f"Vendas: {exc}")
try:
    raw_cycle = read_uploaded(cycle_upload) if cycle_upload else read_raw_sheet(cycle_url, CYCLE_GID, refresh_tick)
    cycle = parse_cycle(raw_cycle)
    raw_cycle_dashboard = read_raw_sheet(cycle_url, CYCLE_DASHBOARD_GID, refresh_tick)
    cycle_dashboard = parse_cycle_dashboard(raw_cycle_dashboard)
    for required_col in ["SDR", "Closer", "Data Entrada", "Data Contato", "Data Reunião", "Data Fechamento"]:
        if required_col not in cycle:
            cycle[required_col] = pd.NaT if required_col.startswith("Data") else ""
except Exception as exc:
    cycle = pd.DataFrame(); cycle_dashboard = pd.DataFrame(); errors.append(f"Ciclo: {exc}")
try:
    raw_pre = read_uploaded(pre_upload) if pre_upload else read_raw_sheet(pre_url, PRE_GID, refresh_tick)
    daily, sdr_source = parse_pre_vendas(raw_pre)
    if not sdr_source.empty and "Data" in sdr_source:
        sdr_source = sdr_source[(sdr_source["Data"] >= inicio) & (sdr_source["Data"] <= fim)].groupby("Nome", as_index=False)[["Realizadas", "No-show", "Vendas"]].sum()
except Exception as exc:
    daily, sdr_source = pd.DataFrame(), pd.DataFrame(); errors.append(f"Pré-vendas: {exc}")

# Filtragem temporal: atividades usam Data; vendas usam Data ou Data Fechamento.
sales_filtered = sales.copy()
if not sales_filtered.empty and "Data" in sales_filtered:
    # Datas ausentes são preenchidas pelo fechamento do Ciclo de Vendas quando houver Lead correspondente.
    if not cycle.empty and "Data Fechamento" in cycle:
        fechamento_por_lead = cycle[["Lead", "Data Fechamento"]].dropna(subset=["Data Fechamento"]).drop_duplicates("Lead")
        sales_filtered = sales_filtered.merge(fechamento_por_lead, on="Lead", how="left")
        sales_filtered["Data"] = sales_filtered["Data"].fillna(sales_filtered["Data Fechamento"])
        sales_filtered = sales_filtered.drop(columns=["Data Fechamento"])
    # Em filtros temporais, vendas sem data conhecida não entram silenciosamente no período.
    sales_filtered = sales_filtered[sales_filtered["Data"].notna() & (sales_filtered["Data"] >= inicio) & (sales_filtered["Data"] <= fim + pd.Timedelta(days=1))]

def filter_date(df, column):
    if df.empty or column not in df:
        return df.iloc[0:0].copy()
    return df[df[column].notna() & (df[column] >= inicio) & (df[column] <= fim + pd.Timedelta(days=1))].copy()

# A aba Dashboard é a fonte oficial do mês. Se ela não tiver datas preenchidas, usa todas as linhas válidas da aba, evitando zerar o ranking.
if not cycle_dashboard.empty and "Data" in cycle_dashboard and cycle_dashboard["Data"].notna().any():
    cycle_dashboard_filtered = filter_date(cycle_dashboard, "Data")
    # Se o recorte selecionado não encontrar linhas, mantém a aba Dashboard visível
    # para que o ranking oficial não desapareça por causa de datas incompletas ou formato misto.
    if cycle_dashboard_filtered.empty:
        cycle_dashboard_filtered = cycle_dashboard.copy()
else:
    cycle_dashboard_filtered = cycle_dashboard.copy()
cycle_entry_filtered = filter_date(cycle, "Data Entrada")
cycle_contact_filtered = filter_date(cycle, "Data Contato")
cycle_meeting_filtered = filter_date(cycle, "Data Reunião")
cycle_close_filtered = filter_date(cycle, "Data Fechamento")
# A tabela operacional mostra qualquer Lead que teve uma etapa no período.
cycle_filtered = pd.concat([cycle_entry_filtered, cycle_contact_filtered, cycle_meeting_filtered, cycle_close_filtered], ignore_index=True).drop_duplicates(subset=["Lead"]) if not cycle.empty else cycle.copy()
daily_filtered = daily[(daily["Data"] >= inicio) & (daily["Data"] <= fim)] if not daily.empty else daily

dashboard_contrato = float(cycle_dashboard_filtered["Valor Contrato"].sum()) if not cycle_dashboard_filtered.empty else 0.0
dashboard_liquido = float(cycle_dashboard_filtered["Valor Líquido"].sum()) if not cycle_dashboard_filtered.empty else 0.0
liquido_calculado = dashboard_liquido if dashboard_liquido > 0 else (float(sales_filtered["Valor Líquido"].sum()) if not sales_filtered.empty and "Valor Líquido" in sales_filtered else 0.0)
# Para o mês completo, preserva o Valor Recebido oficial informado no topo da aba mensal.
# Para recortes diários ou personalizados, calcula somente as vendas dentro do recorte.
resumo_mensal = periodo == "Mês atual"
recebido = liquido_calculado if dashboard_liquido > 0 else (float(sheet_meta.get("recebido", 0)) if resumo_mensal and sheet_meta.get("recebido", 0) else liquido_calculado)
contrato_calculado = dashboard_contrato if dashboard_contrato > 0 else (float(sales_filtered["Valor Contrato"].sum()) if not sales_filtered.empty and "Valor Contrato" in sales_filtered else 0.0)
contrato = contrato_calculado if dashboard_contrato > 0 else (float(sheet_meta.get("contrato_total", 0)) if resumo_mensal and sheet_meta.get("contrato_total", 0) else contrato_calculado)
vendas = int(len(sales_filtered))
realizadas = int(daily_filtered["Realizadas"].sum()) if not daily_filtered.empty else 0
noshow = int(daily_filtered["No-show"].sum()) if not daily_filtered.empty else 0
contatadas = int(daily_filtered["Contatadas"].sum()) if not daily_filtered.empty else 0
agendadas = int(daily_filtered["Agendadas"].sum()) if not daily_filtered.empty else 0
falta_meta = float(sheet_meta.get("falta_meta", 0)) if resumo_mensal and sheet_meta.get("falta_meta", 0) else max(float(meta_valor_manual) - contrato, 0)
falta_super = float(sheet_meta.get("falta_super", 0)) if resumo_mensal and sheet_meta.get("falta_super", 0) else max(float(meta_super_manual) - contrato, 0)
# No resumo mensal, a planilha informa o saldo que falta para cada meta.
# Assim, a meta oficial é contrato realizado + saldo restante, e não um valor padrão.
meta_valor = contrato + falta_meta if resumo_mensal and falta_meta else float(meta_valor_manual)
meta_super = contrato + falta_super if resumo_mensal and falta_super else float(meta_super_manual)
percentual_meta = (contrato / meta_valor * 100) if meta_valor else 0

# -----------------------------
# Modo TV prioritário: interrompe a renderização normal antes do cabeçalho
# -----------------------------
tv_query = str(st.query_params.get("tv", "0")).strip().lower()
tv_enabled = st.session_state.get("tv_active", False) or tv_query in {"1", "true", "on"}
if tv_enabled:
    # A apresentação não deve renderizar o cabeçalho, cards e tabelas do dashboard normal.
    # Monta apenas os rankings mínimos necessários para as telas TV.
    if not cycle_dashboard_filtered.empty:
        closer_rank_tv = cycle_dashboard_filtered.groupby("Closer", dropna=False).agg(Vendas=("Lead", "nunique"), Valor=("Valor Contrato", "sum"), Líquido=("Valor Líquido", "sum")).reset_index().rename(columns={"Closer": "Nome"})
        closer_rank_tv = closer_rank_tv[closer_rank_tv["Nome"].astype(str).str.strip().ne("")].copy()
    else:
        closer_rank_tv = pd.DataFrame(columns=["Nome", "Vendas", "Valor", "Líquido"])
    if not sdr_source.empty:
        sdr_rank_tv = sdr_source.copy().rename(columns={"Nome": "Nome"})
    else:
        sdr_rank_tv = pd.DataFrame(columns=["Nome", "Vendas", "Realizadas", "No-show"])
    for col in ["Vendas", "Realizadas", "No-show"]:
        if col not in sdr_rank_tv.columns: sdr_rank_tv[col] = 0
    if "Taxa Conversão" not in sdr_rank_tv.columns:
        sdr_rank_tv["Taxa Conversão"] = (sdr_rank_tv["Vendas"] / sdr_rank_tv["Realizadas"].replace(0, 1) * 100).round(2)
    try:
        tv_screen = int(st.query_params.get("tv_screen", "0"))
    except (TypeError, ValueError):
        tv_screen = 0
    funil_tv = pd.DataFrame({"Etapa": ["Discadas", "Contatadas", "Agendadas", "Realizadas", "No-show", "Vendas"], "Quantidade": [int(daily_filtered["Discadas"].sum()) if not daily_filtered.empty and "Discadas" in daily_filtered else 0, contatadas, agendadas, realizadas, noshow, vendas]})
    render_tv_mode(tv_screen, tv_seconds, inicio, fim, contrato, meta_valor, percentual_meta, recebido, falta_meta, falta_super, funil_tv, sdr_rank_tv, closer_rank_tv, daily_filtered)
    st.stop()

# -----------------------------
# Cabeçalho e status da conexão
# -----------------------------
st.markdown("<div class='section-kicker'>Sales performance cockpit · dados integrados</div>", unsafe_allow_html=True)
st.title("Performance Comercial")
st.markdown(f"<div class='hero-subtitle'>Período: <strong>{inicio.strftime('%d/%m/%Y')}</strong> a <strong>{fim.strftime('%d/%m/%Y')}</strong> · fontes conectadas por Google Sheets e upload.</div>", unsafe_allow_html=True)
if errors:
    st.warning("Alguma fonte não pôde ser carregada: " + " | ".join(errors))
with st.expander("Status das fontes conectadas", expanded=False):
    st.write({"Planilha de vendas": f"{len(sales)} linhas válidas", "Ciclo de vendas": f"{len(cycle)} leads", "Dashboard financeiro": f"{len(cycle_dashboard)} vendas com valores", "Closers no Dashboard": ", ".join(cycle_dashboard["Closer"].dropna().astype(str).unique().tolist()) if not cycle_dashboard.empty and "Closer" in cycle_dashboard else "nenhum", "Pré-vendas": f"{len(daily)} dias", "SDRs detectados": ", ".join(sdr_source["Nome"].tolist()) if not sdr_source.empty else "nenhum"})

# -----------------------------
# Financeiro
# -----------------------------
st.markdown("<div class='section-kicker'>01 · Visão geral financeira</div>", unsafe_allow_html=True)
c1,c2,c3,c4,c5,c6=st.columns(6)
with c1: card("Valor de Contrato", brl(contrato), "Total oficial da aba mensal", "positive")
with c2: card("Meta", brl(meta_valor), "Objetivo oficial do período", "warning")
with c3:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>% da Meta Atingida</div><div class='metric-value'>{percentual_meta:.2f}%</div><div class='progress-shell'><div class='progress-bar' style='width:{min(percentual_meta,100):.2f}%'></div></div><div class='metric-note'>Contrato: {brl(contrato)} de {brl(meta_valor)}</div></div>", unsafe_allow_html=True)
with c4: card("Valor Recebido", brl(recebido), "Valor líquido oficial", "positive")
with c5: card("Falta pra Meta", brl(falta_meta), "Saldo oficial para atingir", "warning")
with c6: card("Falta pra Super Meta", brl(falta_super), "Saldo oficial do cenário stretch", "critical")

# -----------------------------
# Ranking financeiro dos Closers e funil do período
# -----------------------------
if not cycle_dashboard_filtered.empty:
    closer_rank = cycle_dashboard_filtered.groupby("Closer", dropna=False).agg(
        Vendas=("Lead", "nunique"),
        Valor=("Valor Contrato", "sum"),
        Líquido=("Valor Líquido", "sum"),
    ).reset_index().rename(columns={"Closer": "Nome"})
else:
    closer_rank = pd.DataFrame(columns=["Nome", "Vendas", "Valor", "Líquido"])
closer_rank = closer_rank[closer_rank["Nome"].astype(str).str.strip().ne("")].copy()

st.markdown("<div class='section-kicker'>02 · Ranking financeiro e funil do período</div>", unsafe_allow_html=True)
funil=pd.DataFrame({"Etapa":["Discadas","Contatadas","Agendadas","Realizadas","No-show","Vendas"],"Quantidade":[int(daily_filtered["Discadas"].sum()) if not daily_filtered.empty and "Discadas" in daily_filtered else 0,contatadas,agendadas,realizadas,noshow,vendas]})
left,right=st.columns([1.15,1])
with left:
    st.markdown("<div class='panel'><div class='panel-title'>Ranking de vendas por valor · Closers</div><div class='panel-caption'>Vendas únicas por Lead, contrato e líquido oficiais da aba Dashboard do ciclo.</div>", unsafe_allow_html=True)
    closer_chart = closer_rank.sort_values("Valor").copy()
    if not closer_chart.empty:
        closer_chart["Nome"] = closer_chart["Nome"].astype(str)
        winner = closer_chart.loc[closer_chart["Valor"].idxmax(), "Nome"]
        closer_chart["Nome"] = closer_chart["Nome"].map(lambda x: "🏆 " + x if x == winner else x)
        cf=px.bar(closer_chart,x="Valor",y="Nome",orientation="h",text="Valor",color="Valor",color_continuous_scale=[[0,"#284a91"],[1,"#2ed47a"]])
        cf.update_traces(texttemplate="R$ %{x:,.0f}",textposition="outside"); cf.update_layout(coloraxis_showscale=False,xaxis_title="Valor de contrato",yaxis_title="")
        fig_theme(cf,300); st.plotly_chart(cf,use_container_width=True,config={"displayModeBar":False})
        display=closer_rank[["Nome","Vendas","Valor","Líquido"]].sort_values("Valor",ascending=False).copy()
        display["Valor"]=display["Valor"].map(brl); display["Líquido"]=display["Líquido"].map(brl)
        st.dataframe(display,hide_index=True,use_container_width=True,height=145)
    else: st.info("Nenhuma venda por Closer no período.")
    st.markdown("</div>",unsafe_allow_html=True)
with right:
    st.markdown("<div class='panel'><div class='panel-title'>Funil do período</div><div class='panel-caption'>Atividades contabilizadas pela aba Pré Vendas.</div>", unsafe_allow_html=True)
    ff=go.Figure(go.Funnel(y=funil["Etapa"],x=funil["Quantidade"],textinfo="value+percent initial",marker=dict(color=["#5b8cff","#7da4ff","#f5bd3d","#70a1ff","#ff5a67","#2ed47a"])))
    fig_theme(ff,350); st.plotly_chart(ff,use_container_width=True,config={"displayModeBar":False}); st.markdown("</div>",unsafe_allow_html=True)

st.markdown("<div class='panel' style='margin-top:.8rem'><div class='panel-title'>Atividades por dia</div><div class='panel-caption'>Leitura diária para acompanhamento operacional.</div>", unsafe_allow_html=True)
if not daily_filtered.empty:
    serie=daily_filtered.groupby("Data",as_index=False)[["Contatadas","Agendadas","Realizadas","No-show","Vendas"]].sum().melt("Data",var_name="Indicador",value_name="Quantidade")
    fs=px.line(serie,x="Data",y="Quantidade",color="Indicador",markers=True,color_discrete_map={"Contatadas":"#5b8cff","Agendadas":"#f5bd3d","Realizadas":"#2ed47a","No-show":"#ff5a67","Vendas":"#a879ff"})
    fig_theme(fs,250); st.plotly_chart(fs,use_container_width=True,config={"displayModeBar":False})
else: st.info("Nenhuma atividade no período selecionado.")
st.markdown("</div>",unsafe_allow_html=True)

# -----------------------------
# Rankings separados
# -----------------------------
st.markdown("<div class='section-kicker'>03 · Rankings de vendas e realizadas</div>", unsafe_allow_html=True)

# Base de SDRs: ciclo para vendas/agendamentos e Pré Vendas para realizadas/no-show.
# Realizadas são estritamente exibidas para William, Barbara e Vitoria.
SDR_OFICIAIS = {"william", "barbara", "vitoria", "vitoria"}
# Cada indicador usa a data da própria etapa, e não a data de entrada do Lead.
rank_frames = []
for frame, metric in [(cycle_contact_filtered, "Contatadas"), (cycle_meeting_filtered, "Agendadas"), (cycle_close_filtered, "Vendas")]:
    if not frame.empty:
        counts = frame.groupby("SDR", dropna=False).size().reset_index(name=metric).rename(columns={"SDR": "Nome"})
        rank_frames.append(counts)
if rank_frames:
    sdr_rank = rank_frames[0]
    for counts in rank_frames[1:]:
        sdr_rank = sdr_rank.merge(counts, on="Nome", how="outer")
else:
    sdr_rank = pd.DataFrame(columns=["Nome", "Contatadas", "Agendadas", "Vendas"])
sdr_rank["Realizadas_Ciclo"] = 0
if not sdr_source.empty:
    fonte_sdr = sdr_source.rename(columns={"Realizadas": "Realizadas_Fonte", "No-show": "No-show_Fonte", "Vendas": "Vendas_Fonte"})
    sdr_rank = sdr_rank.merge(fonte_sdr, on="Nome", how="outer")
for col in ["Contatadas", "Agendadas", "Vendas", "Vendas_Fonte", "Realizadas_Ciclo", "Realizadas_Fonte", "No-show_Fonte"]:
    if col not in sdr_rank:
        sdr_rank[col] = 0
sdr_rank = sdr_rank.fillna(0)
sdr_rank["Vendas"] = sdr_rank["Vendas_Fonte"].astype(int)
sdr_rank["Realizadas"] = sdr_rank["Realizadas_Fonte"].astype(int)
sdr_rank["No-show"] = sdr_rank["No-show_Fonte"].astype(int)
sdr_rank = sdr_rank[sdr_rank["Nome"].map(lambda x: re.sub(r"[^a-z]", "", str(x).lower().replace("á", "a").replace("í", "i")) in SDR_OFICIAIS)].copy()
sdr_rank["Taxa Conversão"] = (sdr_rank["Vendas"] / sdr_rank["Realizadas"].replace(0, 1) * 100).round(2)

# -----------------------------
# Modo TV: telas financeiras, funil e rankings com rotação automática
# -----------------------------
if False:
    try:
        tv_screen = int(st.query_params.get("tv_screen", "0"))
    except (TypeError, ValueError):
        tv_screen = 0
    funil_tv = pd.DataFrame({"Etapa": ["Discadas", "Contatadas", "Agendadas", "Realizadas", "No-show", "Vendas"], "Quantidade": [int(daily_filtered["Discadas"].sum()) if not daily_filtered.empty and "Discadas" in daily_filtered else 0, contatadas, agendadas, realizadas, noshow, vendas]})
    render_tv_mode(tv_screen, tv_seconds, inicio, fim, contrato, meta_valor, percentual_meta, recebido, falta_meta, falta_super, funil_tv, sdr_rank, closer_rank, daily_filtered)
    st.stop()

r1, r2 = st.columns(2)
with r1:
    st.markdown("<div class='panel'><div class='panel-title'>Ranking de vendas por SDR</div><div class='panel-caption'>Vendas contabilizadas pela coluna Venda da planilha de Pré Vendas.</div>", unsafe_allow_html=True)
    chart = sdr_rank.sort_values("Vendas").copy()
    if not chart.empty:
        winner = chart.loc[chart["Vendas"].idxmax(), "Nome"]
        chart["Nome"] = chart["Nome"].map(lambda x: "🏆 " + str(x) if x == winner else str(x))
        fig = px.bar(chart, x="Vendas", y="Nome", orientation="h", text="Vendas", color="Vendas", color_continuous_scale=[[0, "#284a91"], [1, "#5b8cff"]])
        fig.update_traces(textposition="outside"); fig.update_layout(coloraxis_showscale=False, xaxis_title="Vendas", yaxis_title=""); fig_theme(fig, 245); st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else: st.info("Nenhuma venda por SDR no período.")
    st.dataframe(sdr_rank[["Nome", "Vendas", "Realizadas", "Taxa Conversão"]].sort_values("Vendas", ascending=False), hide_index=True, use_container_width=True, height=180)
    st.markdown("</div>", unsafe_allow_html=True)
with r2:
    st.markdown("<div class='panel'><div class='panel-title'>Ranking de realizadas por SDR</div><div class='panel-caption'>Somente William, Barbara e Vitoria; leitura da fonte de Pré Vendas.</div>", unsafe_allow_html=True)
    chart = sdr_rank.sort_values("Realizadas").copy()
    if not chart.empty:
        winner = chart.loc[chart["Realizadas"].idxmax(), "Nome"]
        chart["Nome"] = chart["Nome"].map(lambda x: "🏆 " + str(x) if x == winner else str(x))
        fig = px.bar(chart, x="Realizadas", y="Nome", orientation="h", text="Realizadas", color="Realizadas", color_continuous_scale=[[0, "#236746"], [1, "#2ed47a"]])
        fig.update_traces(textposition="outside"); fig.update_layout(coloraxis_showscale=False, xaxis_title="Realizadas", yaxis_title=""); fig_theme(fig, 245); st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else: st.info("Nenhuma realizada por SDR no período.")
    st.dataframe(sdr_rank[["Nome", "Realizadas", "No-show", "Vendas", "Taxa Conversão"]].sort_values("Realizadas", ascending=False), hide_index=True, use_container_width=True, height=180)
    st.markdown("</div>", unsafe_allow_html=True)

r3, r4 = st.columns(2)
with r3:
    st.markdown("<div class='panel'><div class='panel-title'>Ranking de vendas por Closer</div><div class='panel-caption'>Vendas, contrato e líquido oficiais da aba Dashboard do ciclo.</div>", unsafe_allow_html=True)
    chart = closer_rank.sort_values("Vendas").copy()
    if not chart.empty:
        winner = chart.loc[chart["Vendas"].idxmax(), "Nome"]
        chart["Nome"] = chart["Nome"].map(lambda x: "🏆 " + str(x) if x == winner else str(x))
        fig = px.bar(chart, x="Vendas", y="Nome", orientation="h", text="Vendas", color="Vendas", color_continuous_scale=[[0, "#236746"], [1, "#2ed47a"]])
        fig.update_traces(textposition="outside"); fig.update_layout(coloraxis_showscale=False, xaxis_title="Vendas", yaxis_title=""); fig_theme(fig, 245); st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else: st.info("Nenhuma venda por Closer no período.")
    st.dataframe(closer_rank[["Nome", "Vendas", "Valor", "Líquido"]].sort_values("Valor", ascending=False).assign(Valor=lambda d: d["Valor"].map(brl), Líquido=lambda d: d["Líquido"].map(brl)), hide_index=True, use_container_width=True, height=180)
    st.markdown("</div>", unsafe_allow_html=True)
with r4:
    st.markdown("<div class='panel'><div class='panel-title'>Ofertas pendentes e Riscos Zero</div><div class='panel-caption'>Cadastro manual separado das vendas realizadas; não entra na meta até a confirmação do pagamento.</div>", unsafe_allow_html=True)
    st.metric("Valor pendente cadastrado", "R$ 0,00", "Preencha na aba Ofertas Pendentes abaixo")
    st.markdown("Use a aba manual para informar loja, Closer, SDR, valor e condição.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Tabela operacional e rodapé
# -----------------------------
st.markdown("<div class='section-kicker'>04 · Detalhamento operacional</div>",unsafe_allow_html=True)
if "ofertas_pendentes" not in st.session_state:
    st.session_state["ofertas_pendentes"] = pd.DataFrame(columns=["Data", "Loja", "Closer", "SDR", "Valor de Contrato", "Condição", "Status", "Observação"])

tab1,tab2,tab3=st.tabs(["Ciclo de Vendas","Vendas Fechadas","Ofertas Pendentes / Riscos Zero"])
with tab1:
    st.dataframe(cycle_filtered,use_container_width=True,hide_index=True,height=300)
with tab2:
    st.dataframe(sales_filtered,use_container_width=True,hide_index=True,height=300)
with tab3:
    st.info("Cadastre aqui as ofertas que ainda não devem entrar na meta. O valor só será considerado em vendas quando o status for confirmado como pago na planilha oficial.")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        upload_pendentes = st.file_uploader("Importar ofertas pendentes (CSV ou Excel)", type=["csv", "xlsx"], key="upload_pendentes")
    with col_b:
        st.download_button("Baixar cadastro atual", st.session_state["ofertas_pendentes"].to_csv(index=False).encode("utf-8-sig"), "ofertas_pendentes.csv", "text/csv", key="download_pendentes")
    if upload_pendentes is not None:
        imported = read_uploaded(upload_pendentes)
        if imported is not None and not imported.empty:
            header_idx = 0
            for i in range(min(12, len(imported))):
                row_text = " ".join(imported.iloc[i].astype(str).tolist()).lower()
                if "loja" in row_text or "valor" in row_text:
                    header_idx = i
                    break
            imported.columns = imported.iloc[header_idx].astype(str).str.strip()
            imported = imported.iloc[header_idx + 1:].reset_index(drop=True)
            rename_map = {}
            for col in imported.columns:
                norm = re.sub(r"[^a-z0-9]", "", str(col).lower())
                if "loja" in norm or "lead" in norm or "nome" in norm: rename_map[col] = "Loja"
                elif "closer" in norm: rename_map[col] = "Closer"
                elif "sdr" in norm or "hunter" in norm: rename_map[col] = "SDR"
                elif "valor" in norm or "contrato" in norm: rename_map[col] = "Valor de Contrato"
                elif "condicao" in norm or "modalidade" in norm: rename_map[col] = "Condição"
                elif "status" in norm or "situacao" in norm: rename_map[col] = "Status"
            imported = imported.rename(columns=rename_map)
            for col in ["Data", "Loja", "Closer", "SDR", "Valor de Contrato", "Condição", "Status", "Observação"]:
                if col not in imported.columns: imported[col] = ""
            st.session_state["ofertas_pendentes"] = imported[["Data", "Loja", "Closer", "SDR", "Valor de Contrato", "Condição", "Status", "Observação"]].copy()
    edited_pending = st.data_editor(st.session_state["ofertas_pendentes"], num_rows="dynamic", use_container_width=True, hide_index=True, key="editor_pendentes", column_config={"Valor de Contrato": st.column_config.NumberColumn("Valor de Contrato", format="R$ %.2f"), "Status": st.column_config.SelectboxColumn("Status", options=["Risco Zero - para cair", "Risco Zero - efetivado", "Garantia Incondicional", "Pendente"] )})
    st.session_state["ofertas_pendentes"] = edited_pending
    pending_total = sum(money(v) for v in edited_pending["Valor de Contrato"]) if not edited_pending.empty else 0
    st.caption(f"Total cadastrado nesta sessão: {brl(pending_total)} · Estes valores ficam separados da meta até confirmação na planilha oficial.")
st.markdown(f"<div class='footer'>Última atualização: {datetime.now().strftime('%d/%m/%Y às %H:%M')} · Fonte fixa: Google Sheets · Santana/Sant'Anna padronizado como Sant'Anna</div>",unsafe_allow_html=True)
