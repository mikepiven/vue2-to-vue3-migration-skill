import type { SetupContext } from 'vue'

interface BadgeProps {
  label: string
}

export default function Badge(props: BadgeProps, { slots }: SetupContext) {
  return (
    <span class="badge">
      {props.label}
      {slots.default?.()}
    </span>
  )
}

Badge.props = {
  label: { type: String, required: true }
}
