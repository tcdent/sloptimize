import React from 'react';
import styled from 'styled-components';

const BannerContainer = styled.div`
  text-align: center;
  margin-bottom: 40px;
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background-color: var(--modal-background);
`;

const AsciiArt = styled.pre`
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
  text-shadow: 0 0 10px rgba(93, 211, 158, 0.5);
  margin-bottom: 10px;
  
  @media (max-width: 768px) {
    font-size: 8px;
  }
`;

const Subtitle = styled.div`
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 400;
  margin-top: 10px;
  
  @media (max-width: 768px) {
    font-size: 14px;
  }
`;

const Banner: React.FC = () => {

  const asciiArt = `███████╗██╗      ██████╗ ██████╗ ████████╗██╗███╗   ███╗██╗███████╗███████╗
██╔════╝██║     ██╔═══██╗██╔══██╗╚══██╔══╝██║████╗ ████║██║╚══███╔╝██╔════╝
███████╗██║     ██║   ██║██████╔╝   ██║   ██║██╔████╔██║██║  ███╔╝ █████╗  
╚════██║██║     ██║   ██║██╔═══╝    ██║   ██║██║╚██╔╝██║██║ ███╔╝  ██╔══╝  
███████║███████╗╚██████╔╝██║        ██║   ██║██║ ╚═╝ ██║██║███████╗███████╗
╚══════╝╚══════╝ ╚═════╝ ╚═╝        ╚═╝   ╚═╝╚═╝     ╚═╝╚═╝╚══════╝╚══════╝`;

  return (
    <BannerContainer>
      <AsciiArt>{asciiArt}</AsciiArt>
      <Subtitle>
        Transform AI-Generated Code into Production-Ready Python
      </Subtitle>
    </BannerContainer>
  );
};

export default Banner;