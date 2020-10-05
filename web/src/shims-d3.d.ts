interface ScaleContinuousNumeric<Range, Output> {
  range(range: ReadonlyArray<Range>, step: number): this;
  foo: () => this;
}
