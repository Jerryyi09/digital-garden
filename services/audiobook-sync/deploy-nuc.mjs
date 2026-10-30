import { spawnSync } from 'node:child_process'

const host = 'hp@10.0.0.85'
const sshOptions = ['-F', '/dev/null', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', '-p', '2222', '-i', '/Users/jerryyi/.ssh/id_rsa']

function run(command, args, capture = false) {
  const result = spawnSync(command, args, { stdio: capture ? 'pipe' : 'inherit', encoding: 'utf8' })
  if (result.status !== 0) throw new Error(result.stderr || `${command} exited with ${result.status}`)
  return result.stdout?.trim()
}

run('python3', ['-m', 'unittest', 'discover', '-s', 'services/audiobook-sync', '-v'])
const stage = run('ssh', [...sshOptions, host, 'mktemp -d /tmp/garden-sync-search.XXXXXX'], true)
if (!/^\/tmp\/garden-sync-search\.[a-zA-Z0-9]+$/.test(stage)) throw new Error('Unexpected staging path')
run('scp', ['-P', '2222', '-i', '/Users/jerryyi/.ssh/id_rsa',
  'services/audiobook-sync/server.py', 'services/audiobook-sync/library_index.py',
  'services/audiobook-sync/backup.py', 'services/audiobook-sync/deploy-nuc.py', `${host}:${stage}/`])
run('ssh', [...sshOptions, host, `python3 ${stage}/deploy-nuc.py ${stage}`])
