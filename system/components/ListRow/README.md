# ListRow

One item in a list: a status light, a mono name with a muted detail line beneath, and a right-aligned stat.

**Use** for inventories (services, jobs, devices). Rows divide with hairlines; the last has none.

**Consumer provides** `status`, `statusLabel` (optional, the state in words), `name`, `detail` and `stat` (it shows `·` when absent).
