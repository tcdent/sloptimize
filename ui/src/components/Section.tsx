import React from 'react';
import styled from 'styled-components';

const SectionContainer = styled.div`
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background-color: var(--modal-background);
`;

const SectionHeader = styled.div`
  color: var(--title);
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
`;

const Prompt = styled.span`
  color: var(--accent);
  margin-right: 10px;
  font-weight: 700;
`;

interface SectionProps {
  title: string;
  children: React.ReactNode;
}

const Section: React.FC<SectionProps> = ({ title, children }) => {
  return (
    <SectionContainer>
      <SectionHeader>
        <Prompt>$</Prompt>
        {title}
      </SectionHeader>
      {children}
    </SectionContainer>
  );
};

export default Section;