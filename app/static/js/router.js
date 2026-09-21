/* 极简哈希路由：地址形如 #/problems/12，可以直接刷新和分享。 */
export function navigate(path) {
  const target = `#/${String(path).replace(/^#?\/?/, '')}`;
  if (window.location.hash === target) window.dispatchEvent(new HashChangeEvent('hashchange'));
  else window.location.hash = target;
}

export function currentRoute() {
  const raw = window.location.hash.replace(/^#\/?/, '');
  const [id = 'overview', ...rest] = raw.split('/');
  return { id: id || 'overview', param: rest.map(decodeURIComponent).join('/') };
}

export function onRouteChange(handler) {
  window.addEventListener('hashchange', handler);
}
