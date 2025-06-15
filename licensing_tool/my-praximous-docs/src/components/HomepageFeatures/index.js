import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Secure On-Premise Gateway',
    Svg: require('@site/static/img/shield.svg').default, // Updated path
    description: 'Keep your data in your environment. Praximous acts as a central, secure orchestration layer, preventing sensitive information from being exposed to third-party services.',
  },
  {
    title: 'Resilient & Agnostic',
    Svg: require('@site/static/img/network.svg').default, // Updated path
    description: 'Never depend on a single AI provider. With dynamic failover and a pluggable architecture, Praximous ensures your applications remain operational and flexible.',
  },
  {
    title: 'Extensible Smart Skills',
    Svg: require('@site/static/img/puzzle_gears.svg').default, // Updated path
    description: 'Go beyond simple LLM calls. Build modular, reusable logic units—Smart Skills—to automate complex business processes and create powerful, context-aware workflows.',
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      {/*
        Consider adding a minHeight here if your descriptions vary a lot in length,
        to keep the feature boxes visually aligned.
        Example: style={{minHeight: '120px'}}
      */}
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
