import { defineComponent } from 'vue'

export default defineComponent({
  name: 'BaseButton',
  props: {
    disabled: { type: Boolean, default: false }
  },
  emits: ['click'],
  methods: {
    onClick(event: MouseEvent) {
      if (!this.disabled) {
        this.$emit('click', event)
      }
    }
  },
  render() {
    return (
      <button class="base-button" disabled={this.disabled} onClick={this.onClick}>
        {this.$slots.default?.()}
      </button>
    )
  }
})
