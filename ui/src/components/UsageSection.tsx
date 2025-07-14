import React from 'react';
import styled from 'styled-components';
import Section from './Section';

const UsageGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
  margin-top: 20px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const UsageBox = styled.div`
  padding: 24px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background-color: var(--background);
`;

const UsageTitle = styled.h3`
  color: var(--title);
  font-weight: 700;
  font-size: 18px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const UsageIcon = styled.span`
  font-size: 20px;
`;

const UsageDescription = styled.p`
  color: var(--text-primary);
  font-size: 14px;
  margin-bottom: 16px;
  line-height: 1.6;
`;

const ExamplePrompts = styled.div`
  margin-top: 16px;
`;

const PromptsLabel = styled.div`
  color: var(--accent);
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
`;

const PromptsList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const PromptItem = styled.li`
  color: var(--text-secondary);
  font-size: 13px;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
  background-color: rgba(29, 78, 94, 0.1);
  padding: 6px 8px;
  margin-bottom: 4px;
  border-radius: 3px;
  border-left: 2px solid var(--accent);

  &:before {
    content: '"';
    color: var(--accent);
  }

  &:after {
    content: '"';
    color: var(--accent);
  }
`;

interface UsageType {
  icon: string;
  title: string;
  description: string;
  prompts: string[];
}

const UsageSection: React.FC = () => {
  const usageTypes: UsageType[] = [
    {
      icon: '🔍',
      title: 'Feedback Queries',
      description: 'Get quality assessments and insights about your code. Use these prompts to understand if your code shows signs of being AI-generated or follows best practices.',
      prompts: [
        'chat is this slop?',
        'did an LLM write this?',
        'what do you think of this code?'
      ]
    },
    {
      icon: '✨',
      title: 'Cleanup Queries',
      description: 'Automatically optimize and refactor your code in place. These prompts will transform sloppy patterns into production-ready Python following modern best practices.',
      prompts: [
        'sloptimize this',
        'improve this slop',
        'clean this up',
      ]
    }
  ];

  return (
    <Section title="Usage">
      <UsageGrid>
        {usageTypes.map((usage, index) => (
          <UsageBox key={index}>
            <UsageTitle>
              <UsageIcon>{usage.icon}</UsageIcon>
              {usage.title}
            </UsageTitle>
            <UsageDescription>
              {usage.description}
            </UsageDescription>
            <ExamplePrompts>
              <PromptsLabel>Example Prompts</PromptsLabel>
              <PromptsList>
                {usage.prompts.map((prompt, promptIndex) => (
                  <PromptItem key={promptIndex}>
                    {prompt}
                  </PromptItem>
                ))}
              </PromptsList>
            </ExamplePrompts>
          </UsageBox>
        ))}
      </UsageGrid>
    </Section>
  );
};

export default UsageSection;