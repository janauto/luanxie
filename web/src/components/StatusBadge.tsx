const LABELS: Record<string, string> = {
  pending: '排队中',
  transcribing: '转写中',
  classifying: '归类中',
  merging: '合并中',
  awaiting_review: '待确认',
  done: '已入库',
  failed: '失败',
  rejected: '已拒绝',
}

const WORKING = new Set(['pending', 'transcribing', 'classifying', 'merging'])

export default function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`status-badge st-${status} ${WORKING.has(status) ? 'working' : ''}`}>
      <span className="dot" />
      {LABELS[status] || status}
    </span>
  )
}
