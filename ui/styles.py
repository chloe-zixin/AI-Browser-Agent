from __future__ import annotations


def inject_global_styles() -> None:
    import streamlit as st

    st.markdown(
        """
        <style>
        :root {
            --bg: #070b14;
            --panel: linear-gradient(180deg, rgba(11,16,30,0.96) 0%, rgba(8,12,24,0.98) 100%);
            --panel-2: linear-gradient(180deg, rgba(18,24,42,0.92) 0%, rgba(10,14,26,0.95) 100%);
            --line: rgba(127, 90, 240, 0.20);
            --line-strong: rgba(166, 114, 255, 0.42);
            --text: #f4f7ff;
            --muted: #9da7c2;
            --muted-2: #6f7a98;
            --purple: #8b5cf6;
            --purple-2: #a855f7;
            --purple-3: #c084fc;
            --blue: #38bdf8;
            --cyan: #22d3ee;
            --green: #22c55e;
            --danger: #fb7185;
            --warning: #f59e0b;
            --shadow: 0 0 0 1px rgba(139,92,246,0.14), 0 10px 30px rgba(0,0,0,0.35), 0 0 40px rgba(139,92,246,0.12);
            --radius-xl: 22px;
            --radius-lg: 18px;
            --radius-md: 14px;
        }

        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background:
                radial-gradient(circle at 15% 20%, rgba(56,189,248,0.10), transparent 20%),
                radial-gradient(circle at 85% 15%, rgba(168,85,247,0.16), transparent 22%),
                radial-gradient(circle at 80% 80%, rgba(34,211,238,0.10), transparent 18%),
                linear-gradient(135deg, #03060d 0%, #070b14 45%, #050814 100%);
            color: var(--text);
        }

        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"] { display: none; }

        .block-container {
            padding-top: 1.1rem;
            padding-bottom: 1.25rem;
            max-width: 1500px;
        }

        .app-shell {
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 28px;
            background: rgba(5, 9, 18, 0.78);
            box-shadow: 0 20px 60px rgba(0,0,0,0.38), 0 0 0 1px rgba(168,85,247,0.10);
            padding: 14px;
            backdrop-filter: blur(10px);
        }

        .top-browser {
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 20px;
            background: linear-gradient(180deg, rgba(18,22,32,0.96), rgba(9,12,21,0.96));
            padding: 10px 14px;
            margin-bottom: 14px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
        }

        .browser-row {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .traffic {
            display: flex;
            gap: 7px;
            min-width: 60px;
        }

        .dot {
            width: 11px;
            height: 11px;
            border-radius: 50%;
            opacity: 0.95;
        }

        .dot.red { background: #ff5f57; }
        .dot.yellow { background: #febc2e; }
        .dot.green { background: #28c840; }

        .browser-bar {
            flex: 1;
            height: 36px;
            border-radius: 999px;
            background: linear-gradient(180deg, rgba(16,20,30,0.98), rgba(9,12,20,0.98));
            border: 1px solid rgba(255,255,255,0.05);
            display: flex;
            align-items: center;
            padding: 0 16px;
            color: var(--muted);
            font-size: 13px;
        }

        .browser-actions {
            display: flex;
            gap: 8px;
        }

        .mini-btn {
            width: 28px;
            height: 28px;
            border-radius: 10px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
        }

        .side-nav {
            min-height: 840px;
            border-radius: 24px;
            background: var(--panel);
            border: 1px solid rgba(255,255,255,0.05);
            box-shadow: var(--shadow);
            padding: 12px 10px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .brand {
            width: 52px;
            height: 52px;
            margin: 0 auto 10px auto;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 23px;
            font-weight: 800;
            color: white;
            background: linear-gradient(135deg, rgba(29,36,62,1) 0%, rgba(76,29,149,1) 50%, rgba(139,92,246,1) 100%);
            box-shadow: 0 0 24px rgba(139,92,246,0.32);
        }

        .nav-stack {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-top: 10px;
        }

        .nav-item {
            width: 48px;
            height: 48px;
            margin: 0 auto;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #d7def3;
            background: rgba(255,255,255,0.025);
            border: 1px solid rgba(255,255,255,0.045);
            font-size: 20px;
        }

        .nav-item.active {
            background: linear-gradient(135deg, rgba(85,44,202,0.92), rgba(180,83,255,0.94));
            border: 1px solid rgba(210,170,255,0.26);
            box-shadow: 0 0 28px rgba(168,85,247,0.30);
        }

        .panel-title {
            font-size: 18px;
            font-weight: 700;
            color: var(--text);
        }

        .panel-subtitle {
            color: var(--muted);
            font-size: 12px;
        }

        .badge-glow {
            display: inline-flex;
            align-items: center;
            padding: 6px 10px;
            border-radius: 999px;
            border: 1px solid rgba(168,85,247,0.22);
            background: rgba(168,85,247,0.10);
            color: #efe7ff;
            font-size: 12px;
        }

        .metric-card {
            background: linear-gradient(180deg, rgba(12,17,31,0.98), rgba(9,12,23,0.98));
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 22px;
            padding: 16px;
            min-height: 130px;
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
        }

        .metric-card.featured {
            background:
                radial-gradient(circle at 85% 20%, rgba(192,132,252,0.26), transparent 18%),
                linear-gradient(135deg, rgba(76,29,149,0.92), rgba(23,37,84,0.92));
        }

        .metric-label {
            color: #cdd6ee;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 12px;
        }

        .metric-value {
            font-size: 40px;
            font-weight: 800;
            color: white;
            margin-bottom: 8px;
        }

        .metric-foot {
            display: flex;
            justify-content: space-between;
            color: var(--muted);
            font-size: 12px;
        }

        .status-dots {
            display: flex;
            gap: 6px;
        }

        .status-dots span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--green);
            display: inline-block;
            box-shadow: 0 0 12px rgba(34,197,94,0.5);
        }

        /* ⭐ 真按钮炫酷化 */
        div.stButton > button {
            width: 100%;
            height: 56px;
            border-radius: 999px;
            border: 1px solid rgba(168, 85, 247, 0.28);
            background: linear-gradient(90deg, #6d28d9 0%, #a855f7 100%);
            color: #ffffff;
            font-size: 16px;
            font-weight: 700;
            box-shadow:
                0 10px 30px rgba(109,40,217,0.28),
                inset 0 1px 0 rgba(255,255,255,0.08);
            transition: all 0.18s ease;
            margin-top: 16px;
        }

        div.stButton > button:hover {
            background: linear-gradient(90deg, #7c3aed 0%, #c084fc 100%);
            border: 1px solid rgba(216,180,254,0.35);
            color: #ffffff;
            box-shadow:
                0 14px 36px rgba(168,85,247,0.34),
                inset 0 1px 0 rgba(255,255,255,0.12);
        }

        div.stButton > button:focus,
        div.stButton > button:focus-visible {
            outline: none;
            box-shadow:
                0 0 0 1px rgba(216,180,254,0.45),
                0 14px 36px rgba(168,85,247,0.34);
            color: #ffffff;
        }

        div.stButton > button:active {
            transform: translateY(1px);
        }

        /* success 提示框美化 */
        div[data-testid="stAlert"] {
            border-radius: 18px !important;
            border: 1px solid rgba(34,197,94,0.20) !important;
            background: linear-gradient(90deg, rgba(10,50,35,0.75), rgba(8,30,24,0.75)) !important;
            color: #dcfce7 !important;
        }

        /* JSON 区域美化 */
        div[data-testid="stJson"] {
            border-radius: 18px;
            border: 1px solid rgba(168,85,247,0.12);
            background: rgba(8,12,22,0.78);
            padding: 8px;
        }

        .footer-note {
            color: var(--muted-2);
            font-size: 11px;
            margin-top: 10px;
        }

        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background: #f3f6f7;
            color: #17313a;
        }

        [data-testid="stHeader"] { background: rgba(243,246,247,0.92); }
        .block-container {
            max-width: 1380px;
            padding: 2rem 2rem 3rem;
        }

        .app-shell {
            border: 0;
            border-radius: 0;
            background: transparent;
            box-shadow: none;
            padding: 0;
            backdrop-filter: none;
        }

        h1, h2, h3, label, p, [data-testid="stMetricLabel"] {
            color: #17313a !important;
        }

        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #dce5e7;
            border-radius: 8px;
            padding: 14px 16px;
        }

        [data-testid="stMetricValue"] { color: #145e56 !important; }

        [data-testid="stDataFrame"] {
            border: 1px solid #dce5e7;
            border-radius: 8px;
            overflow: hidden;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stSelectbox"] [data-baseweb="select"] > div {
            border-color: #cbd9dc;
            border-radius: 6px;
            background: #ffffff;
        }

        [data-testid="stForm"] {
            border: 1px solid #dce5e7;
            border-radius: 8px;
            background: #ffffff;
            padding: 18px 20px 8px;
            margin: 16px 0 24px;
        }

        [data-testid="stFormSubmitButton"] button,
        div.stButton > button {
            min-height: 42px;
            border-radius: 6px;
            border: 1px solid #145e56;
            background: #145e56;
            color: #ffffff;
            font-weight: 650;
            box-shadow: none;
            margin-top: 0;
        }

        [data-testid="stFormSubmitButton"] button:hover,
        div.stButton > button:hover {
            border-color: #0d4b45;
            background: #0d4b45;
            color: #ffffff;
        }

        [data-testid="stAlert"] { border-radius: 6px !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )