import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import TaskForm from '@/components/TaskForm.vue'

describe('TaskForm', () => {
  it('rejects empty titles and does not emit submit', async () => {
    const wrapper = mount(TaskForm)
    await wrapper.find('#task-title').setValue('   ')
    await wrapper.find('form').trigger('submit')
    expect(wrapper.text()).toContain('Title is required.')
    expect(wrapper.emitted('submit')).toBeUndefined()
  })

  it('emits a normalized payload on valid submit', async () => {
    const wrapper = mount(TaskForm)
    await wrapper.find('#task-title').setValue('  Ship release  ')
    await wrapper.find('#task-description').setValue('Notes')
    await wrapper.find('#task-status').setValue('done')
    await wrapper.find('#task-priority').setValue('high')
    await wrapper.find('form').trigger('submit')
    const emitted = wrapper.emitted('submit')
    expect(emitted).toHaveLength(1)
    const payload = emitted![0][0]
    expect(payload.title).toBe('Ship release')
    expect(payload.status).toBe('done')
    expect(payload.priority).toBe('high')
    expect(payload.due_date).toBeNull()
  })

  it('converts due-date input to ISO', async () => {
    const wrapper = mount(TaskForm)
    await wrapper.find('#task-title').setValue('With due date')
    await wrapper.find('#task-due').setValue('2026-12-01T10:30')
    await wrapper.find('form').trigger('submit')
    const payload = wrapper.emitted('submit')![0][0]
    expect(payload.due_date).toBeTruthy()
    expect(new Date(payload.due_date as string).getMinutes()).toBe(30)
  })
})
