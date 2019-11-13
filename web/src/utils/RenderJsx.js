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
  render(createElement, context) {
    const { f } = context.props;
    if (typeof f === 'string') {
      return createElement('div', {}, [f]);
    }
    return f.apply({
      $createElement: createElement,
    }, context.props.args);
  },
};
