import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  scale: number;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  description: JSX.Element;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Automate Mailing',
    scale: 1.0,
    Svg: require('@site/static/img/outlook.svg').default,
    description: (
      <>
        Creator Administator automatically sends customizable emails when
        an maker request is received, finished or unclear.
      </>
    ),
  },
  {
    title: 'Focus on What Matters',
    scale: 1.0,
    Svg: require('@site/static/img/logo.svg').default,
    description: (
      <>
      Creator Administrator does the administation for you. By doing so you can focus on making stuff. 
      </>
    ),
  },
  {
    title: 'For 3D Printers and Laser Cutters',
    scale: 1.0,
    Svg: require('@site/static/img/hammer_wrench.svg').default,
    description: (
      <>
        Intended for handling 3D printing requests, or/and to handle requests for a laser cutting machine. 
      </>
    ),
  },
];

function Feature({title, scale, Svg, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg transform={"scale(" + scale + ")"} className={styles.featureSvg} role="img" />
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
