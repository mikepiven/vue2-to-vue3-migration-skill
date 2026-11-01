import Vue from 'vue'

interface Item {
  id: number
  name: string
}

export default Vue.extend({
  name: 'DataList',
  props: {
    items: { type: Array as () => Item[], default: () => [] }
  },
  methods: {
    firstItem(): HTMLElement | undefined {
      return (this.$refs.itemEls as HTMLElement[])[0]
    }
  },
  render(h) {
    return (
      <div class="data-list">
        {this.$scopedSlots.header && this.$scopedSlots.header({ count: this.items.length })}
        <ul>
          {this.items.map((item) => (
            <li key={item.id} ref="itemEls" refInFor={true}>
              {this.$scopedSlots.item ? this.$scopedSlots.item({ item }) : item.name}
            </li>
          ))}
        </ul>
      </div>
    )
  }
})
