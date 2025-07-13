import React from 'react';
import styled from 'styled-components';

const FooterContainer = styled.div`
  text-align: center;
  padding: 30px 20px;
  border-top: 1px solid var(--border);
  margin-top: 40px;
`;

const FooterContent = styled.div`
  color: var(--text-secondary);
  font-size: 18px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
`;

const Link = styled.a`
  color: var(--accent);
  text-decoration: none;
  font-weight: 700;
  padding: 8px 16px;
  border: 1px solid var(--accent);
  border-radius: 4px;
  transition: all 0.2s;
  
  &:hover {
    background-color: var(--accent);
    color: var(--background);
  }
`;

const Prompt = styled.span`
  color: var(--accent);
  margin-right: 10px;
  font-weight: 700;
`;

const Footer: React.FC = () => {
  return (
    <FooterContainer>
      <FooterContent>
        <Link href="https://github.com/tcdent/sloptimize" target="_blank" rel="noopener noreferrer">
          sloptimize on GitHub
        </Link>
        <Link href="https://x.com/ssslomp" target="_blank" rel="noopener noreferrer">
          ssslomp on X
        </Link>
      </FooterContent>
    </FooterContainer>
  );
};

export default Footer;