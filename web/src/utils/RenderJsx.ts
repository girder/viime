export default {
  functional: true,
  props: {
    f: {
      required: true,
    },
    args: {
      type: Array,
      required: false,
      default() {
        return [];
      },
    },
  },
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  render(createElement: (arg0: string, arg1: object, arg2: Array<any>) => {}, context: any) {
    const { f } = context.props;
    if (typeof f === 'string') {
      return createElement('div', {}, [f]);
    }
    return f.apply({
      $createElement: createElement,
    }, context.props.args);
  },
};
