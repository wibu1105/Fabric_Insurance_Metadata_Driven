export async function getEmbedConfig({ dashboardId }) {
  const query = new URLSearchParams({ dashboardId });
  const response = await fetch(`/api/powerbi/embed-config?${query.toString()}`, {
    credentials: 'include'
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Embed config request failed with ${response.status}`);
  }

  return response.json();
}
