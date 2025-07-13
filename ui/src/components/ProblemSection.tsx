import React from 'react';
import styled from 'styled-components';
import Section from './Section';

const ProblemContent = styled.div`
  color: var(--text-primary);
  font-size: 16px;
  line-height: 1.8;
  margin-bottom: 20px;
`;

const ProblemStatement = styled.p`
  margin-bottom: 16px;

  &:last-child {
    margin-bottom: 0;
  }
`;

const HighlightText = styled.span`
  color: var(--accent);
  font-weight: 700;
`;

const ProblemSection: React.FC = () => {
  return (
    <Section title="Vibe Code like a Senior Engineer">
      <ProblemContent>
        <ProblemStatement>
          Your agentic coder is pretty good at zero-shotting solutions to your problems,
          but all current generative models produce code that's riddled with slop.
        </ProblemStatement>
        <ProblemStatement>
          <HighlightText>sloptimize</HighlightText> automatically identifies and transforms sloppy patterns into modern, idiomatic Python that follows best practices for production codebases.
          If you care about writing correct, maintainable, and stylistically modern Python code, <HighlightText>sloptimize</HighlightText> can help you achieve that.
        </ProblemStatement>
        <ProblemStatement>
          Configure the <HighlightText>MCP</HighlightText> tool with <HighlightText>Claude Code</HighlightText> or <HighlightText>Cursor</HighlightText> and Start to start
          building projects that look like a senior engineer wrote them by hand.
        </ProblemStatement>
      </ProblemContent>
    </Section>
  );
};

export default ProblemSection;