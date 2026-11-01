import { defineComponent } from 'vue'
import { bus } from '../bus'
import BaseButton from './BaseButton'

export default defineComponent({
  name: 'AppModal',
  inheritAttrs: false,
  props: {
    visible: { type: Boolean, default: false },
    title: { type: String, default: '' }
  },
  emits: ['update:visible'],
  created() {
    bus.on('close-all-modals', this.close)
  },
  beforeUnmount() {
    bus.off('close-all-modals', this.close)
  },
  methods: {
    close() {
      this.$emit('update:visible', false)
    }
  },
  render() {
    if (!this.visible) {
      return null
    }
    return (
      <div class="modal" {...this.$attrs}>
        <h3>{this.title}</h3>
        {this.$slots.default?.()}
        <BaseButton onClick={this.close}>close</BaseButton>
      </div>
    )
  }
})
