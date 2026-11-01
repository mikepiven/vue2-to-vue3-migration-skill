import { Component, Prop, Vue } from 'vue-property-decorator'

@Component
export default class LegacyWidget extends Vue {
  @Prop({ default: 'legacy' }) readonly label!: string

  render() {
    return <span class="legacy-widget">{this.label}</span>
  }
}
