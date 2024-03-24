import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  description: JSX.Element;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Automate Mailing',
    Svg: require('@site/static/img/outlook.svg').default,
    description: (
      <>
        Creator Administator automatically sends customizable emails when
        an maker request is created, a request is finished or when a request 
        is unclear.
      </>
    ),
  },
  {
    title: 'Focus on What Matters',
    Svg: require('@site/static/img/logo.svg').default,
    description: (
      <>
      Creator Administrator keeps track of all makers request. Keeping track of 
      a requests status and progress. By doing so you can focus on making stuff. 
      </>
    ),
  },
  {
    title: 'For 3D Printers and Laser Cutters',
    Svg: require('@site/static/img/hammer_wrench.svg').default,
    description: (
      <>
        Intended for handling many 3D printing requests to then print with your 3D printers. Or to handle many requests for a laser cutting machine. 
      </>
    ),
  },
];

function Feature({title, Svg, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): JSX.Element {
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
