import Vue from 'vue'
import { bus } from './bus'
import AppModal from './components/Modal'
import Badge from './components/Badge'
import BaseButton from './components/BaseButton'
import DataList from './components/DataList'
import TodoItem from './components/TodoItem'

interface Todo {
  id: number
  name: string
}

export default Vue.extend({
  name: 'App',
  data() {
    return {
      text: 'Buy milk',
      done: false,
      showModal: false,
      todos: [
        { id: 1, name: 'Buy milk' },
        { id: 2, name: 'Write migration skill' }
      ] as Todo[]
    }
  },
  methods: {
    openModal() {
      this.showModal = true
    },
    closeEverything() {
      bus.$emit('close-all-modals')
    },
    onDoneChange(value: boolean) {
      this.done = value
    },
    onVisibleChange(value: boolean) {
      this.showModal = value
    }
  },
  render(h) {
    return (
      <div id="app">
        <TodoItem
          vModel={this.text}
          done={this.done}
          {...{ on: { 'update:done': this.onDoneChange } }}
        />
        <DataList
          items={this.todos}
          scopedSlots={{
            header: (scope: { count: number }) => <h2>{scope.count} todos</h2>,
            item: (scope: { item: Todo }) => <Badge label={scope.item.name}>!</Badge>
          }}
        />
        <BaseButton nativeOnClick={this.openModal}>open</BaseButton>
        <BaseButton nativeOnClick={this.closeEverything}>close all</BaseButton>
        <AppModal
          title="Hello"
          visible={this.showModal}
          {...{ on: { 'update:visible': this.onVisibleChange } }}
        >
          Modal body
        </AppModal>
      </div>
    )
  }
})
