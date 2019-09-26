export interface RootState {
  datasets: any;
  plots: any;
  analyses: any;
  lasterror: any;
  loading: boolean;
  store: Storage | null;
  session_id: string;
};
