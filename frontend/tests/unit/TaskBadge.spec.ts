import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import TaskBadge from '@/components/TaskBadge.vue'
import type { TaskStatus } from '@/types'

describe('TaskBadge', () => {
  it('renders human labels for statuses', () => {
    const cases: Array<[TaskStatus, string]> = [
      ['todo', 'To do'],
      ['in_progress', 'In progress'],
      ['done', 'Done'],
    ]
    for (const [value, label] of cases) {
      const wrapper = mount(TaskBadge, { props: { kind: 'status', value } })
      expect(wrapper.text()).toContain(label)
    }
  })

  it('renders priority labels with color classes', () => {
    const wrapper = mount(TaskBadge, { props: { kind: 'priority', value: 'high' } })
    expect(wrapper.text()).toContain('High')
    expect(wrapper.html()).toContain('bg-red-100')
  })
})
