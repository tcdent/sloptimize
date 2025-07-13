import React from 'react';
import styled from 'styled-components';
import GlobalStyles from './styles/GlobalStyles';
import Banner from './components/Banner';
import ProblemSection from './components/ProblemSection';
import InstallationSection from './components/InstallationSection';
import CodeExampleSection from './components/CodeExampleSection';
import FeaturesSection from './components/FeaturesSection';
import Footer from './components/Footer';

const TerminalContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: var(--background);
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(29, 78, 94, 0.3);
  min-height: 100vh;
`;

function App() {
  return (
    <>
      <GlobalStyles />
      <TerminalContainer>
        <Banner />
        <InstallationSection />
        <ProblemSection />
        <CodeExampleSection />
        <FeaturesSection />
        <Footer />
      </TerminalContainer>
    </>
  );
}

export default App;
