"""Cyberpunk theme CSS styles for ChitraAI"""

CYBERPUNK_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    * {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .stApp {
        background: #0A0A0A;
    }
    
    /* Remove top padding from main container */
    .main .block-container {
        padding-top: 2rem !important;
    }
    
    .neon-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF6B35 0%, #FF0080 50%, #8B00FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(255, 107, 53, 0.5);
        margin-bottom: 0;
        line-height: 1.2;
    }
    
    .status-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .status-bar .neon-title { margin: 0; line-height: 1.1; }
    
    .system-status {
        color: #FF6B35;
        font-size: 0.9rem;
        text-align: right;
        line-height: 1.2;
    }
    
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #FF6B35;
        box-shadow: 0 0 10px #FF6B35;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .status-cards {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    .status-card {
        background: rgba(255, 107, 53, 0.05);
        border: 1px solid;
        padding: 1rem;
        border-radius: 4px;
    }
    
    .status-card.connected {
        border-image: linear-gradient(135deg, #FF6B35, #FF0080) 1;
    }
    
    .status-card.disconnected {
        border: 1px solid #333;
        opacity: 0.5;
    }
    
    .card-title {
        color: #888;
        font-size: 0.75rem;
        margin-bottom: 0.5rem;
    }
    
    .card-status {
        color: #FF6B35;
        font-size: 1rem;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.5);
    }
    
    .card-status.disconnected {
        color: #555;
        text-shadow: none;
    }
    
    div[data-testid="column"]:first-child > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 107, 53, 0.03);
        border: 1px solid #333;
        border-right: 1px solid rgba(255, 107, 53, 0.35);
        box-shadow: 1px 0 0 rgba(255, 107, 53, 0.06), 10px 0 28px rgba(255, 107, 53, 0.06);
        padding: 1.05rem 1rem 1.05rem;
    }
    div[data-testid="column"]:last-child > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 107, 53, 0.03);
        border: 1px solid #333;
        border-left: 1px solid rgba(255, 107, 53, 0.35);
        box-shadow: -1px 0 0 rgba(255, 107, 53, 0.06), -10px 0 28px rgba(255, 107, 53, 0.06);
        padding: 1.05rem 1rem 1.05rem;
    }
    
    .panel-title {
        color: #FF6B35;
        font-size: 0.85rem;
        margin-bottom: 1.25rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
    }
    
    .upload-label {
        color: #FF6B35;
        font-size: 0.7rem;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 700;
    }
    
    div[data-testid="column"]:first-child [data-testid="stFileUploader"] {
        margin-bottom: 0;
    }
    div[data-testid="column"]:first-child [data-testid="stFileUploaderDropzone"] {
        border: 2px dashed rgba(255, 255, 255, 0.16) !important;
        background: rgba(0, 0, 0, 0.35) !important;
        border-radius: 6px !important;
        padding: 0 !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
        box-shadow: none;
    }
    div[data-testid="column"]:first-child [data-testid="stFileUploaderDropzone"]:hover {
        border-color: rgba(255, 107, 53, 0.65) !important;
        background: rgba(255, 107, 53, 0.05) !important;
        box-shadow: 0 0 18px rgba(255, 107, 53, 0.09);
    }
    div[data-testid="column"]:first-child [data-testid="stFileUploaderDropzone"] > div {
        display: grid !important;
        place-items: center !important;
        min-height: 120px;
        padding: 18px 15px !important;
    }
    div[data-testid="column"]:first-child [data-testid="stFileUploaderDropzone"] small,
    div[data-testid="column"]:first-child [data-testid="stFileUploaderDropzone"] span,
    div[data-testid="column"]:first-child [data-testid="stFileUploaderDropzone"] p,
    div[data-testid="column"]:first-child [data-testid="stFileUploaderDropzone"] button {
        display: none !important;
    }
    div[data-testid="column"]:first-child [data-testid="stFileUploader"]:nth-of-type(1) [data-testid="stFileUploaderDropzone"]::before {
        content: "↑\A\AMP3 • WAV • M4A";
        white-space: pre;
        text-align: center;
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.75rem;
        letter-spacing: 1px;
        line-height: 1.5;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.15);
        display: block;
    }
    div[data-testid="column"]:first-child [data-testid="stFileUploader"]:nth-of-type(1) [data-testid="stFileUploaderDropzone"] > div {
        min-height: 120px;
    }
    div[data-testid="column"]:first-child [data-testid="stFileUploader"]:nth-of-type(2) [data-testid="stFileUploaderDropzone"]::before {
        content: "◇\A\APNG • JPG";
        white-space: pre;
        text-align: center;
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.75rem;
        letter-spacing: 1px;
        line-height: 1.5;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.12);
    }
    
    .toggle-container {
        padding: 1.05rem 1.1rem;
        background: rgba(255, 107, 53, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.14);
        margin: 1.1rem 0 1.25rem;
        text-align: left;
        border-radius: 6px;
        box-shadow: none;
        cursor: pointer;
    }
    .toggle-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.6rem;
    }
    .toggle-title .label {
        color: rgba(255, 255, 255, 0.86);
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 1.5px;
    }
    .toggle-container:hover {
        border-color: rgba(255, 107, 53, 0.55);
        box-shadow: 0 0 0 1px rgba(255, 107, 53, 0.2), 0 0 22px rgba(255, 107, 53, 0.09);
    }
    .toggle-container [data-testid="stCheckbox"] {
        margin-top: -0.05rem;
        display: flex;
        justify-content: flex-start;
    }
    .toggle-container [data-testid="stCheckbox"] label {
        width: auto;
        padding: 0;
        display: flex !important;
        align-items: center !important;
        gap: 0.45rem;
        line-height: 1;
        color: rgba(255, 255, 255, 0.88) !important;
        font-size: 0.84rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .toggle-container [data-testid="stCheckbox"] input {
        margin-top: 0 !important;
    }
    
    .agent-list {
        position: relative;
        padding-left: 0.25rem;
        margin-top: 0.25rem;
    }
    .agent-list::before {
        content: '';
        position: absolute;
        left: 1.05rem;
        top: 0.55rem;
        bottom: 0.55rem;
        width: 2px;
        background: linear-gradient(180deg, rgba(255, 107, 53, 0.55) 0%, rgba(255, 0, 128, 0.55) 100%);
        opacity: 0.28;
        filter: drop-shadow(0 0 6px rgba(255, 107, 53, 0.25));
        border-radius: 2px;
    }

    .agent-item {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 1.15rem;
        position: relative;
        align-items: center;
    }
    
    .agent-number {
        color: #FF6B35;
        font-size: 1.25rem;
        font-weight: 700;
        min-width: 2rem;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.5);
        line-height: 1.0;
        padding-top: 0.1rem;
    }
    
    .agent-content {
        flex: 1;
    }
    
    .agent-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.35rem;
    }
    
    .agent-name {
        color: #FFF;
        font-size: 0.98rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    .agent-desc {
        color: #666;
        font-size: 0.74rem;
        line-height: 1.55;
    }
    
    .agent-status {
        color: #FF6B35;
        font-size: 0.7rem;
        padding: 0.25rem 0.75rem;
        border: 1px solid #FF6B35;
        text-shadow: 0 0 5px rgba(255, 107, 53, 0.5);
        white-space: nowrap;
        border-radius: 999px;
        letter-spacing: 1px;
    }
    
    .agent-item.final-output {
        border-top: 1px solid rgba(255, 255, 255, 0.12);
        padding-top: 1.1rem;
        margin-top: 0.9rem;
    }
    
    .final-output-body {
        margin-top: 0.85rem;
        padding: 1rem;
        border: 1px solid rgba(255, 107, 53, 0.35);
        background: rgba(255, 107, 53, 0.06);
        border-radius: 6px;
        box-shadow: inset 0 0 0 1px rgba(255, 107, 53, 0.08);
    }
    
    .agent-status.running {
        animation: glow 1.5s infinite;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 5px rgba(255, 107, 53, 0.5); }
        50% { box-shadow: 0 0 15px rgba(255, 107, 53, 0.8); }
    }
    
    .system-log {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #333;
        padding: 1.05rem 1.15rem;
        border-radius: 6px;
        box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.5);
    }
    
    .log-title {
        color: #FF6B35;
        font-size: 0.75rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
    }
    .log-title.terminal {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 0.75rem;
    }
    .term-dots {
        display: inline-flex;
        gap: 6px;
        transform: translateY(-1px);
    }
    .term-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.18);
        box-shadow: 0 0 10px rgba(255, 107, 53, 0.12);
    }
    
    .log-content {
        color: rgba(255, 107, 53, 0.6);
        font-size: 0.8rem;
        line-height: 1.8;
        font-family: 'JetBrains Mono', monospace;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.08);
    }
    
    button[kind="primary"] {
        background: linear-gradient(135deg, #FF6B35 0%, #FF0080 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        box-shadow: 0 0 20px rgba(255, 107, 53, 0.3) !important;
    }
    
    button[kind="primary"]:hover {
        box-shadow: 0 0 30px rgba(255, 107, 53, 0.6) !important;
    }
    
    .stCheckbox label {
        color: #888 !important;
    }
</style>
"""
