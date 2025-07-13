import React from 'react';
import styled from 'styled-components';
import CommandBox from './CommandBox';
import Section from './Section';

const InstallationGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const InstallationColumn = styled.div`
  border: 1px solid var(--border);
  border-radius: 4px;
  background-color: var(--background);
  padding: 20px;
`;

const ColumnTitle = styled.h3`
  color: var(--title);
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 16px;
  text-align: center;
`;

const InstallationSection: React.FC = () => {
  const claudeCodeCommand = 'claude mcp add --transport http sloptimize https://mcp.sloptimize.ai';
  const cursorInstructions = `1. Cursor menu > Settings > Cursor Settings
2. Navigate to "Tools & Integrations"
3. Click "New MCP Server"
4. Add the configuration below`;

  const cursorConfig = `{
  "mcpServers": {
    "sloptimize": {
      "type": "http",
      "url": "https://mcp.sloptimize.ai"
    }
  }
}`;

  return (
    <Section title="Get Started">
      <InstallationGrid>
        <InstallationColumn>
          <ColumnTitle>Claude Code</ColumnTitle>
          <div style={{ marginBottom: '20px', color: 'var(--text-primary)', fontSize: '14px', lineHeight: '1.6' }}>
            Make sure Claude Code is installed, then run:
          </div>
          <CommandBox
            title="Command Line"
            command={claudeCodeCommand}
          />
        </InstallationColumn>
        
        <InstallationColumn>
          <ColumnTitle>Cursor</ColumnTitle>
          <div style={{ marginBottom: '20px', color: 'var(--text-primary)', fontSize: '14px', lineHeight: '1.6' }}>
            {cursorInstructions.split('\n').map((line, index) => (
              <div key={index}>{line}</div>
            ))}
          </div>
          <CommandBox
            title="Configuration JSON"
            command={cursorConfig}
          />
        </InstallationColumn>
      </InstallationGrid>
    </Section>
  );
};

export default InstallationSection;