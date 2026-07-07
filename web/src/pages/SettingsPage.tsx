import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Health } from '../types'

export default function SettingsPage({ showToast }: { showToast: (m: string) => void }) {
  const [health, setHealth] = useState<Health | null>(null)
  const [exporting, setExporting] = useState(false)
  const [lastExport, setLastExport] = useState<string | null>(
    localStorage.getItem('lastExport'))

  useEffect(() => { api.health().then(setHealth).catch(() => {}) }, [])

  const doExport = async () => {
    setExporting(true)
    try {
      const r = await api.exportNow()
      const stamp = new Date().toLocaleString('zh-CN')
      localStorage.setItem('lastExport', stamp)
      setLastExport(stamp)
      showToast(r.count ? `已导出 ${r.count} 篇到 Obsidian` : '没有需要导出的更新')
    } catch (e) {
      showToast((e as Error).message)
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="fade-in">
      <div className="section-title">设置</div>
      <div className="card">
        <button className="btn primary" style={{ width: '100%' }} disabled={exporting} onClick={doExport}>
          {exporting ? '导出中…' : '导出到 Obsidian'}
        </button>
        <div className="meta" style={{ justifyContent: 'center', marginTop: 10 }}>
          {lastExport ? `上次导出:${lastExport}` : '尚未导出过'}
        </div>
      </div>
      {health && (
        <div className="card">
          <div className="kv"><span className="k">API Key</span>
            <span className={`v ${health.api_key_set ? 'ok' : 'warn'}`}>{health.api_key_set ? '已配置' : '未配置'}</span></div>
          <div className="kv"><span className="k">语音转写 (Whisper)</span>
            <span className={`v ${health.whisper_installed ? 'ok' : 'warn'}`}>{health.whisper_installed ? '已安装' : '未安装'}</span></div>
          <div className="kv"><span className="k">自动合并门槛</span>
            <span className="v">{{ high: '高置信才自动', medium: '中等以上自动', low: '全自动' }[health.auto_merge_confidence] || health.auto_merge_confidence}</span></div>
          <div className="kv"><span className="k">处理队列</span><span className="v">{health.queue_depth} 条</span></div>
          <div className="kv" style={{ borderBottom: 'none' }}><span className="k">导出目录</span>
            <span className="v">{health.export_dir.replace(/^.*OBVault/, 'OBVault')}</span></div>
        </div>
      )}
      <div className="empty" style={{ padding: '24px 20px', fontSize: 12 }}>
        乱写 · 原文永远保留,合并可回滚<br />你的知识库,在你自己的 Obsidian 里
      </div>
    </div>
  )
}
