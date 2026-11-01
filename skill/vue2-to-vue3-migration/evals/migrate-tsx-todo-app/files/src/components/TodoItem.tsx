import Vue from 'vue'
import BaseButton from './BaseButton'

export default Vue.extend({
  name: 'TodoItem',
  props: {
    value: { type: String, required: true },
    done: { type: Boolean, default: false }
  },
  model: { prop: 'value', event: 'input' },
  methods: {
    onInput(event: Event) {
      this.$emit('input', (event.target as HTMLInputElement).value)
    },
    onToggle() {
      this.$emit('update:done', !this.done)
    }
  },
  render(h) {
    return (
      <li class={{ done: this.done }}>
        <input domPropsValue={this.value} onInput={this.onInput} />
        <BaseButton nativeOnClick={this.onToggle}>toggle</BaseButton>
        {this.$scopedSlots.actions && this.$scopedSlots.actions({ done: this.done })}
      </li>
    )
  }
})
