import axios from 'axios'
import { ActionTree, ActionContext } from 'vuex'

import { State } from './state'
import { Mutations, Mutation } from './mutations'

export enum Action {
  initApp = 'initApp',
  fetchRecentCallers = 'fetchRecentCallers',
}

type AugmentedActionContext = {
  commit<K extends keyof Mutations>(
    key: K,
    payload?: Parameters<Mutations[K]>[1]
  ): ReturnType<Mutations[K]>
} & Omit<ActionContext<State, State>, 'commit'>

export interface Actions {
  [Action.initApp]({ state, commit, dispatch }: AugmentedActionContext): void
  [Action.fetchRecentCallers]({ state, commit, dispatch }: AugmentedActionContext): Promise<void>
}

export const actions: ActionTree<State, State> & Actions = {
  [Action.initApp]({ state, commit, dispatch }) {
    console.log('app inited!')
  },
  async [Action.fetchRecentCallers]({ state, commit, dispatch }: AugmentedActionContext) {
    const recentUrl = 'https://omtuqhov52.execute-api.us-east-1.amazonaws.com/dev/recent'
    const resp = await axios.get(recentUrl)
    console.log('got response:', resp.data)
    const formatted = resp.data.recent.map((c) => ({
      ...c,
      results: c.results.reverse().join(', '),
      date: new Date(c.date).toDateString(),
      callerId: c.caller_id,
    }))
    commit<Mutation.SET_CALLERS>(Mutation.SET_CALLERS, formatted)
  },
}
