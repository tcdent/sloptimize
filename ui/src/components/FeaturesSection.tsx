import React from 'react';
import styled from 'styled-components';
import Section from './Section';

const FeaturesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 20px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const FeatureBox = styled.div`
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background-color: var(--background);
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(29, 78, 94, 0.3);
  }
`;

const FeatureIcon = styled.div`
  font-size: 32px;
  margin-bottom: 10px;
`;

const FeatureTitle = styled.div`
  color: var(--title);
  font-weight: 700;
  font-size: 16px;
  margin-bottom: 8px;
`;

const FeatureDesc = styled.div`
  color: var(--text-primary);
  font-size: 14px;
`;

interface Feature {
  icon: string;
  title: string;
  description: string;
}

const FeaturesSection: React.FC = () => {
  const features: Feature[] = [
    {
      icon: '🎯',
      title: 'Cognitive Load Reduction',
      description: 'Simplify complex constructs and eliminate redundant patterns that burden code comprehension'
    },
    {
      icon: '🧠',
      title: 'Semantic Clarity',
      description: 'Transform ambiguous naming and structure into self-documenting, intention-revealing code'
    },
    {
      icon: '⚡',
      title: 'Modern Language Idioms',
      description: 'Embrace contemporary Python patterns while discarding outdated approaches'
    },
    {
      icon: '🔄',
      title: 'Defensive Programming',
      description: 'Replace excessive guards with purposeful error handling and robust design principles'
    },
    {
      icon: '📐',
      title: 'Structural Consistency',
      description: 'Establish coherent organization patterns that scale across codebases'
    },
    {
      icon: '🎨',
      title: 'Expressive Minimalism',
      description: 'Achieve maximum clarity with minimal syntax through thoughtful code design'
    }
  ];

  return (
    <Section title="Features">
      <FeaturesGrid>
        {features.map((feature, index) => (
          <FeatureBox key={index}>
            <FeatureIcon>{feature.icon}</FeatureIcon>
            <FeatureTitle>{feature.title}</FeatureTitle>
            <FeatureDesc>{feature.description}</FeatureDesc>
          </FeatureBox>
        ))}
      </FeaturesGrid>
    </Section>
  );
};

export default FeaturesSection;