import { defineComponent } from 'vue'
import BaseButton from './BaseButton'

export default defineComponent({
  name: 'TodoItem',
  props: {
    modelValue: { type: String, required: true },
    done: { type: Boolean, default: false }
  },
  emits: {
    'update:modelValue': (value: string) => typeof value === 'string',
    'update:done': (value: boolean) => typeof value === 'boolean'
  },
  methods: {
    onInput(event: Event) {
      this.$emit('update:modelValue', (event.target as HTMLInputElement).value)
    },
    onToggle() {
      this.$emit('update:done', !this.done)
    }
  },
  render() {
    return (
      <li class={{ done: this.done }}>
        <input value={this.modelValue} onInput={this.onInput} />
        <BaseButton onClick={this.onToggle}>toggle</BaseButton>
        {this.$slots.actions?.({ done: this.done })}
      </li>
    )
  }
})
