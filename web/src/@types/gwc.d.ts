declare module '@girder/components/src/utils/mixins' {
  export const sizeFormatter: {
    methods: {
      formatSize: (size: number, { base, unit }?: { base: number; unit: string }) => string;
    };
  };
}
