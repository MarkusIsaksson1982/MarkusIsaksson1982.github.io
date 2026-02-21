import styles from './Footer.module.css';

export default function Footer() {
  return (
    <footer className={styles.footer} role="contentinfo">
      <div className={styles.inner}>
        <p>
          Built by{' '}
          <a href="https://github.com/MarkusIsaksson1982" rel="noopener">Markus Isaksson</a>
          {' · '}
          <a href="https://www.linkedin.com/in/markus-isaksson-08273a127/" rel="noopener">LinkedIn</a>
          {' · '}
          <a href="../mp1-fcc-explorer/">MP1 Vanilla</a>
          {' · '}
          <a href="../mp2-survey-builder/">MP2 Survey Builder</a>
          {' · '}
          React 18 + Vite
        </p>
        <p className={styles.aiNote}>
          <small>Architected with Claude Sonnet 4.6 · Full AI orchestration log in README</small>
        </p>
      </div>
    </footer>
  );
}
