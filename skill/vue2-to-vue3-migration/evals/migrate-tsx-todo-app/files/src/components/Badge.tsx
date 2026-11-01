import Vue from 'vue'

export default Vue.extend({
  name: 'Badge',
  functional: true,
  props: {
    label: { type: String, required: true }
  },
  render(h, context) {
    return (
      <span class="badge">
        {context.props.label}
        {context.children}
      </span>
    )
  }
})
