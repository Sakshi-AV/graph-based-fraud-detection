export function buildGraph(transactions) {
  const nodes = new Map();
  const edges = [];

  transactions.forEach((transaction) => {
    const sender = getOrCreateNode(nodes, transaction.sender);
    const receiver = getOrCreateNode(nodes, transaction.receiver);

    sender.outDegree += 1;
    receiver.inDegree += 1;
    sender.degree += 1;
    receiver.degree += 1;

    edges.push({
      source: transaction.sender,
      target: transaction.receiver,
      amount: transaction.amount,
      risk: transaction.risk || 0
    });
  });

  applyPageRank(nodes, edges);
  return { nodes, edges };
}

function emptyNodeStats() {
  return {
    inDegree: 0,
    outDegree: 0,
    degree: 0,
    pageRank: 0
  };
}

function getOrCreateNode(nodes, id) {
  if (!nodes.has(id)) {
    nodes.set(id, emptyNodeStats());
  }
  return nodes.get(id);
}

function applyPageRank(nodes, edges) {
  const nodeIds = [...nodes.keys()];
  if (nodeIds.length === 0) {
    return;
  }

  const damping = 0.85;
  let ranks = Object.fromEntries(nodeIds.map((id) => [id, 1 / nodeIds.length]));

  for (let iteration = 0; iteration < 12; iteration += 1) {
    const nextRanks = Object.fromEntries(nodeIds.map((id) => [id, (1 - damping) / nodeIds.length]));

    nodeIds.forEach((id) => {
      const outgoing = edges.filter((edge) => edge.source === id);
      if (outgoing.length === 0) {
        return;
      }

      outgoing.forEach((edge) => {
        nextRanks[edge.target] += damping * (ranks[id] / outgoing.length);
      });
    });

    ranks = nextRanks;
  }

  nodeIds.forEach((id) => {
    nodes.get(id).pageRank = ranks[id];
  });
}

