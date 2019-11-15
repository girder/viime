import { Component, Prop, Vue } from 'vue-property-decorator';

interface IRenderJsxContext {
  $createElement: Vue.CreateElement;
}

interface IJSXProps {
  f: string | ((this: IRenderJsxContext, ...args: unknown[]) => Vue.VNode);
  args: unknown[];
}

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
  render(createElement: Vue.CreateElement, context: Vue.RenderContext<IJSXProps>) {
    const { f } = context.props;
    if (typeof f === 'string') {
      return createElement('div', {}, [f]);
    }
    return f.apply({
      $createElement: createElement,
    }, context.props.args);
  },
};
