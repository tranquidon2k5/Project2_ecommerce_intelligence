/**
 * Download a CSV file from an API endpoint.
 * @param {string} apiPath - API path (e.g., "/export/products?platform=tiki")
 * @param {string} filename - Suggested filename for download
 */
export function downloadCsv(apiPath, filename = 'export.csv') {
  const link = document.createElement('a')
  link.href = `/api/v1${apiPath}`
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
