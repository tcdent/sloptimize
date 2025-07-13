import { createGlobalStyle } from 'styled-components';

const GlobalStyles = createGlobalStyle`
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  :root {
    /* Color Palette */
    --mindaro: #bce784;
    --emerald: #5dd39e;
    --midnight-green: #1d4e5e;
    --raisin-black: #212130;
    --licorice: #171118;
    
    /* Semantic Color Variables */
    --background: var(--licorice);
    --modal-background: var(--raisin-black);
    --border: var(--midnight-green);
    --text-primary: var(--mindaro);
    --text-secondary: var(--mindaro);
    --accent: var(--emerald);
    --highlight: var(--midnight-green);
    --title: var(--emerald);
  }

  body {
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    background-color: var(--background);
    color: var(--text-primary);
    line-height: 1.6;
    overflow-x: hidden;
  }

  /* Scrollbar Styling */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  ::-webkit-scrollbar-track {
    background: var(--modal-background);
  }

  ::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: var(--accent);
  }

  /* Selection Styling */
  ::selection {
    background: var(--modal-background);
    color: var(--text-primary);
  }

  /* Copy Success Animation */
  @keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
  }

  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0.3; }
  }

  /* Override Prism.js default styles */
  pre[class*="language-"] {
    box-shadow: none !important;
    border: none !important;
    background: transparent !important;
  }

  code[class*="language-"] {
    box-shadow: none !important;
    background: transparent !important;
  }
`;

export default GlobalStyles;