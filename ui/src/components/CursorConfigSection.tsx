import React from 'react';
import styled from 'styled-components';
import CommandBox from './CommandBox';
import Section from './Section';

const CursorConfigSection: React.FC = () => {
  const cursorConfig = `{
  "claude-code.enabled": true,
  "claude-code.features": {
    "sloptimize": true,
    "codeAnalysis": true,
    "optimization": true
  },
  "claude-code.sloptimize": {
    "provider": "openai",
    "model": "o1-3-code",
    "autoOptimize": false,
    "showDiff": true
  }
}`;

  return (
    <Section title="Cursor Configuration">
      <CommandBox
        title="settings.json"
        command={cursorConfig}
      />
    </Section>
  );
};

export default CursorConfigSection;