export const BACKEND_IP: string = "http://10.0.0.218:8000";
// export const BACKEND_IP: string = "http://localhost:8000";

export interface StateManager<T> {
  getter: T;
  setter: (state: T) => void;
}

export interface QueryResult {
  urls: StateManager<(string | null)[]>;
  size: StateManager<number>;
}

export interface ApplicationProps {
  isSearching: StateManager<boolean>;
  searchQuery: StateManager<string>;
  result: QueryResult;
}

export interface SectionProps {
  globals: ApplicationProps;
}
