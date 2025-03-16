import styles from "./styles/MorphingGradient.module.css";

// ----------------------------------------------------------------------------

export function MorphingGradient() {
  return (
    <div>
      <div className={styles["container"]}>
        <div className={styles["gradients-container"]}>
          <div className={styles["g1"]}></div>
          <div className={styles["g2"]}></div>
          <div className={styles["g3"]}></div>
          <div className={styles["g4"]}></div>
          <div className={styles["g5"]}></div>
        </div>
      </div>
      <div className={styles["morph-background"]}></div>
    </div>
  );
}
