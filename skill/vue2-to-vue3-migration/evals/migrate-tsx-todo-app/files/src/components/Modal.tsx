import Vue from 'vue'
import { bus } from '../bus'
import BaseButton from './BaseButton'

export default Vue.extend({
  name: 'AppModal',
  props: {
    visible: { type: Boolean, default: false },
    title: { type: String, default: '' }
  },
  created() {
    bus.$on('close-all-modals', this.close)
  },
  beforeDestroy() {
    bus.$off('close-all-modals', this.close)
  },
  methods: {
    close() {
      this.$emit('update:visible', false)
    }
  },
  render(h) {
    if (!this.visible) {
      return null
    }
    return (
      <div class="modal" {...{ on: this.$listeners }}>
        <h3>{this.title}</h3>
        {this.$slots.default}
        <BaseButton nativeOnClick={this.close}>close</BaseButton>
      </div>
    )
  }
})
