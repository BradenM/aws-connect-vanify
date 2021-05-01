import { MutationTree } from 'vuex'
import { RecentCaller, State } from './state'

export enum Mutation {
  SET_CALLERS = 'SET_CALLERS',
}

export type Mutations<S = State> = {
  [Mutation.SET_CALLERS](state: S, payload: RecentCaller[]): void
}

export const mutations: MutationTree<State> & Mutations = {
  [Mutation.SET_CALLERS](state: State, payload: RecentCaller[] = []) {
    state.recentCallers = payload
  },
}
