export type RecentCaller = {
  callerId: string
  contactId: string
  date: Date
  input: string
  results: string
}

export interface State {
  debug: boolean
  version: string
  isInitialized: boolean
  recentCallers: RecentCaller[]
}

const versionString = import.meta.env.MODE === 'development' ? _APP_VERSION + '-dev' : _APP_VERSION

export const state: State = {
  debug: import.meta.env.MODE === 'development',
  version: versionString,
  isInitialized: false,
  recentCallers: [],
}
