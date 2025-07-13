import React, { useState } from 'react';
import styled from 'styled-components';

const CommandBoxContainer = styled.div`
  margin-bottom: 20px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background-color: var(--background);
  overflow: hidden;
`;

const CommandHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background-color: var(--modal-background);
  border-bottom: 1px solid var(--border);
`;

const CommandTitle = styled.span`
  color: var(--title);
  font-weight: 700;
  font-size: 14px;
`;

const CopyBtn = styled.button<{ $copied: boolean }>`
  background-color: ${props => props.$copied ? 'var(--highlight)' : 'var(--border)'};
  color: var(--text-primary);
  border: none;
  padding: 5px 10px;
  border-radius: 3px;
  font-family: inherit;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: var(--accent);
  }
`;

const Command = styled.pre`
  padding: 15px;
  margin: 0;
  color: var(--text-primary);
  background-color: transparent;
  font-family: inherit;
  font-size: 14px;
  white-space: pre-wrap;
  overflow-x: auto;
`;

interface CommandBoxProps {
  title: string;
  command: string;
}

const CommandBox: React.FC<CommandBoxProps> = ({ title, command }) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(command);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
      
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = command;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      try {
        document.execCommand('copy');
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (fallbackErr) {
        console.error('Fallback copy failed: ', fallbackErr);
      }
      
      document.body.removeChild(textArea);
    }
  };

  return (
    <CommandBoxContainer>
      <CommandHeader>
        <CommandTitle>{title}</CommandTitle>
        <CopyBtn $copied={copied} onClick={copyToClipboard}>
          {copied ? 'Copied!' : 'Copy'}
        </CopyBtn>
      </CommandHeader>
      <Command>{command}</Command>
    </CommandBoxContainer>
  );
};

export default CommandBox;