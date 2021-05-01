<template>
  <div>
    <div class="px-8 prose">
      <h1>{{ title }}</h1>
      <p class="text-sm text-gray-700">Frontend for AWS Connect Vanify Application.</p>
      <h2>Recent Callers</h2>
    </div>
    <div class="p-3">
      <DataTable :value="recentCallers" :autoLayout="true">
        <Column field="date" header="Date" />
        <Column field="callerId" header="Caller" />
        <Column field="input" header="Input" />
        <Column field="results" header="Results" />
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { computed, defineProps, onBeforeMount } from 'vue'

import { useStore, Action } from '@/store/index'

const store = useStore()
const appVersion = store.state.version // not reactive!

const recentCallers = computed(() => store.state.recentCallers)
onBeforeMount(async () => await store.dispatch(Action.fetchRecentCallers))

const props = defineProps<{
  title: string
}>()
</script>
