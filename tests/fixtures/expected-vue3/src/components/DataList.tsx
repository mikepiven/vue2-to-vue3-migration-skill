import { defineComponent } from 'vue'

interface Item {
  id: number
  name: string
}

export default defineComponent({
  name: 'DataList',
  props: {
    items: { type: Array as () => Item[], default: () => [] }
  },
  data() {
    return { itemEls: [] as HTMLElement[] }
  },
  beforeUpdate() {
    this.itemEls = []
  },
  methods: {
    firstItem(): HTMLElement | undefined {
      return this.itemEls[0]
    },
    setItemEl(el: unknown, index: number) {
      if (el) {
        this.itemEls[index] = el as HTMLElement
      }
    }
  },
  render() {
    return (
      <div class="data-list">
        {this.$slots.header?.({ count: this.items.length })}
        <ul>
          {this.items.map((item, index) => (
            <li key={item.id} ref={(el) => this.setItemEl(el, index)}>
              {this.$slots.item ? this.$slots.item({ item }) : item.name}
            </li>
          ))}
        </ul>
      </div>
    )
  }
})
