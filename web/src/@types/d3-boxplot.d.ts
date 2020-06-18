declare module 'd3-boxplot' {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function boxplot(): any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function boxplotStats(arg: number[]): any;

  export {
    boxplot,
    boxplotStats,
  };
}
