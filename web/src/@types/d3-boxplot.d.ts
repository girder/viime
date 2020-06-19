declare module 'd3-boxplot' {
  interface BoxplotStats {
    boxes: {start: number; end: number }[];
    fences: {start: number; end: number }[];
    fiveNumbs: [number, number, number, number, number];
    iqr: number;
    points: { value: number; datum: number; outlier: boolean; farout: boolean }[];
    whiskers: { start: number; end: number }[];
  }

  function boxplotStats(arg: number[]): BoxplotStats;

  export {
    BoxplotStats,
    boxplotStats,
  };
}
