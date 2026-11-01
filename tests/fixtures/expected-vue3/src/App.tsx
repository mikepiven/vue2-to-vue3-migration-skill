import { defineComponent } from 'vue'
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

export default defineComponent({
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
      bus.emit('close-all-modals')
    }
  },
  render() {
    const slots = {
      header: (scope: { count: number }) => <h2>{scope.count} todos</h2>,
      item: (scope: { item: Todo }) => <Badge label={scope.item.name}>!</Badge>
    }
    return (
      <div id="app">
        <TodoItem v-model={this.text} v-model:done={this.done} />
        <DataList items={this.todos} v-slots={slots} />
        <BaseButton onClick={this.openModal}>open</BaseButton>
        <BaseButton onClick={this.closeEverything}>close all</BaseButton>
        <AppModal title="Hello" v-model:visible={this.showModal}>
          Modal body
        </AppModal>
      </div>
    )
  }
})
