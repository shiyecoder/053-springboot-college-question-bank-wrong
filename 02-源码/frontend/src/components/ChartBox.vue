<template>
  <div ref="el" class="chart-box" :style="{ height: height + 'px' }"></div>
</template>

<script setup>
/**
 * ECharts 轻封装：初始化、随容器自适应、option 变更重绘、卸载销毁（避免内存泄漏）
 */
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: { type: Object, required: true },
  height: { type: Number, default: 220 }
})

const el = ref(null)
let chart = null
let ro = null

function render() {
  if (!el.value) return
  if (!chart) chart = echarts.init(el.value)
  chart.setOption(props.option, true)
}

onMounted(async () => {
  await nextTick()
  render()
  ro = new ResizeObserver(() => chart && chart.resize())
  ro.observe(el.value)
})

watch(() => props.option, render, { deep: true })

onBeforeUnmount(() => {
  if (ro) ro.disconnect()
  if (chart) chart.dispose()
  chart = null
})
</script>
