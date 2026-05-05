"""Dashboard-specific CSS styles for ChitraAI"""

DASHBOARD_CSS = """
<style>
    .dashboard-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem 1rem;
    }
    
    .dashboard-header {
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .dashboard-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF6B35 0%, #FF0080 50%, #8B00FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 40px rgba(255, 107, 53, 0.6);
        margin-bottom: 1rem;
        letter-spacing: 2px;
    }
    
    .dashboard-subtitle {
        color: rgba(255, 255, 255, 0.6);
        font-size: 1.1rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    
    .pipeline-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
        margin-top: 3rem;
    }
    
    .pipeline-card {
        background: rgba(255, 107, 53, 0.03);
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px 12px 0 0;
        padding: 1.75rem;
        position: relative;
        cursor: pointer;
        transition: all 0.3s ease;
        overflow: hidden;
        min-height: 240px;
        display: flex;
        flex-direction: column;
    }
    
    /* Button below card */
    .pipeline-card + div {
        margin-top: -2px;
        margin-bottom: 1.5rem;
    }
    
    .pipeline-card + div button[kind="primary"] {
        border-radius: 0 0 12px 12px !important;
        border-top: none !important;
        margin-top: 0 !important;
    }
    
    .coming-soon-text {
        background: rgba(255, 107, 53, 0.03);
        border: 2px solid rgba(255, 255, 255, 0.05);
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 0.75rem;
        text-align: center;
        color: rgba(255, 107, 53, 0.5);
        font-size: 0.7rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-top: -2px;
    }
    
    .pipeline-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.1) 0%, rgba(255, 0, 128, 0.1) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: 0;
    }
    
    .pipeline-card:hover::before {
        opacity: 1;
    }
    
    .pipeline-card.active {
        border-color: rgba(255, 107, 53, 0.6);
        box-shadow: 0 0 30px rgba(255, 107, 53, 0.3), inset 0 0 20px rgba(255, 107, 53, 0.05);
    }
    
    .pipeline-card.active:hover {
        border-color: rgba(255, 107, 53, 0.9);
        box-shadow: 0 0 50px rgba(255, 107, 53, 0.5), inset 0 0 30px rgba(255, 107, 53, 0.1);
    }
    
    .pipeline-card.active:hover + div button {
        box-shadow: 0 0 50px rgba(255, 107, 53, 0.5) !important;
    }
    
    .pipeline-card.locked {
        opacity: 0.5;
        cursor: not-allowed;
        border-color: rgba(255, 255, 255, 0.05);
    }
    
    .pipeline-card.locked:hover {
        transform: none;
        box-shadow: none;
    }
    
    .card-content {
        position: relative;
        z-index: 1;
        display: flex;
        flex-direction: column;
        flex: 1;
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    
    .card-title {
        color: #FFF;
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: 1px;
        line-height: 1.3;
    }
    
    .card-status {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        white-space: nowrap;
    }
    
    .card-status.active {
        background: rgba(0, 255, 100, 0.15);
        color: #00FF64;
        border: 1px solid rgba(0, 255, 100, 0.4);
        text-shadow: 0 0 10px rgba(0, 255, 100, 0.5);
    }
    
    .card-status.locked {
        background: rgba(255, 255, 255, 0.05);
        color: rgba(255, 255, 255, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .card-description {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.85rem;
        line-height: 1.6;
        margin-bottom: 1.25rem;
        flex: 1;
    }
    
    .card-metrics {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: auto;
    }
    
    .lazy-meter {
        flex: 1;
    }
    
    .lazy-label {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .lazy-bar {
        width: 100%;
        height: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        overflow: hidden;
        position: relative;
    }
    
    .lazy-fill {
        height: 100%;
        background: linear-gradient(90deg, #FF6B35 0%, #FF0080 100%);
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(255, 107, 53, 0.6);
        transition: width 0.5s ease;
    }
    
    .lazy-value {
        color: #FF6B35;
        font-size: 1.2rem;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.5);
        margin-left: 1rem;
        min-width: 50px;
        text-align: right;
    }
    

    
    .back-button {
        position: fixed;
        top: 1rem;
        left: 1rem;
        background: rgba(255, 107, 53, 0.1);
        border: 1px solid rgba(255, 107, 53, 0.3);
        color: #FF6B35;
        padding: 0.7rem 1.5rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        cursor: pointer;
        transition: all 0.3s ease;
        z-index: 1000;
    }
    
    .back-button:hover {
        background: rgba(255, 107, 53, 0.2);
        border-color: rgba(255, 107, 53, 0.6);
        box-shadow: 0 0 20px rgba(255, 107, 53, 0.3);
    }
    #card_3 {
        margin-top: 1rem;
    }
    
    @media (max-width: 768px) {
        .pipeline-grid {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
        
        .dashboard-title {
            font-size: 2.5rem;
        }
        
        .back-button {
            top: 1rem;
            left: 1rem;
            padding: 0.5rem 1rem;
            font-size: 0.75rem;
        }
    }
</style>
"""
