import Vue from 'vue'

export default Vue.extend({
  name: 'BaseButton',
  props: {
    disabled: { type: Boolean, default: false }
  },
  methods: {
    onClick(event: MouseEvent) {
      if (!this.disabled) {
        this.$emit('click', event)
      }
    }
  },
  render(h) {
    return (
      <button class="base-button" disabled={this.disabled} onClick={this.onClick}>
        {this.$slots.default}
      </button>
    )
  }
})
